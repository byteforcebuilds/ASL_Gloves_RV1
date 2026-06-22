from __future__ import annotations

import abc
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from .constants import FEATURE_COLS, TRAIN_SUBJECTS, VAL_SUBJECTS, TEST_SUBJECTS, WINDOW_SIZE, STRIDE


class ASLDataset(Dataset, abc.ABC):
    """Abstract base class for ASL gesture datasets.

    owns all shared logic: loading CSVs, per-subject normalization,
    windowing, and train/val/test splitting. subclasses only override
    which signs they handle and how a window becomes a model input.
    """

    def __init__(
        self,
        data_dir: Path,
        split: Literal['train', 'val', 'test'],
        window_size: int = WINDOW_SIZE,
        stride: int = STRIDE,
    ) -> None:
        self.data_dir    = data_dir
        self.split       = split
        self.window_size = window_size
        self.stride      = stride

        # load --> normalize --> window, in that order
        df = self._load(self._signs())
        df = self._normalize(df)
        self.windows, self.labels = self._window(df)

    # private methods

    def _subjects(self) -> list[str]:
        """return subject ids for the current split"""
        # KeyError here means an invalid split string was passed
        return {'train': TRAIN_SUBJECTS,
                'val':   VAL_SUBJECTS,
                'test':  TEST_SUBJECTS}[self.split]

    def _load(self, signs: list[str]) -> pd.DataFrame:
        """load CSVs for the current split's subjects and sign list"""
        frames = []
        for subject in self._subjects():
            for sign in signs:
                # build the path from data_dir / subject_id / sign.csv
                path = self.data_dir / subject / f'{sign}.csv'

                # skip silently if a file is missing rather than crashing
                if not path.exists():
                    continue
                df = pd.read_csv(path)

                # tag each row so we can group by subject and sign later
                df['subject'] = subject
                df['sign']    = sign
                frames.append(df)

        # stack all individual dataframes into one contiguous block
        return pd.concat(frames, ignore_index=True)

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """per-subject z-score normalization across all feature columns.

        flex channels have CoV up to 11 across subjects -- raw values are
        not comparable across signers without normalization.
        """
        normalized = df.copy()
        for subject in df['subject'].unique():
            # boolean mask selects only rows belonging to this subject
            mask = df['subject'] == subject

            # compute mean and std from this subject's data only
            mu  = df.loc[mask, FEATURE_COLS].mean()
            sig = df.loc[mask, FEATURE_COLS].std()

            # z-score: subtract mean, divide by std
            # 1e-8 prevents division by zero if a feature has zero variance
            normalized.loc[mask, FEATURE_COLS] = (df.loc[mask, FEATURE_COLS] - mu) / (sig + 1e-8)
        return normalized

    def _window(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """slice each recording into fixed-length overlapping windows.

        returns:
            windows -- shape (n_samples, window_size, n_features)
            labels  -- shape (n_samples,) integer class indices
        """
        # build a sign --> integer index mapping for this subclass's sign list
        # static and dynamic datasets each have independent label spaces (0-indexed)
        sign_to_idx = {sign: i for i, sign in enumerate(self._signs())}
        windows, labels = [], []

        # iterate over each unique (subject, sign) recording
        for (subject, sign), group in df.groupby(['subject', 'sign']):
            # extract raw feature values as a numpy array -- shape (1500, 21)
            data = group[FEATURE_COLS].values

            # calculate how many windows fit in this recording given window_size and stride
            n_windows = (len(data) - self.window_size) // self.stride + 1

            for i in range(n_windows):
                # stride * i gives the start index of each window
                start = i * self.stride

                # slice a fixed-length chunk of sensor data
                windows.append(data[start : start + self.window_size])

                # every timestep in a window shares the same label
                labels.append(sign_to_idx[sign])

        # stack into arrays -- float32 for features (pytorch default), int64 for labels (CrossEntropyLoss requirement)
        return np.array(windows, dtype=np.float32), np.array(labels, dtype=np.int64)

    # abstract methods

    @abc.abstractmethod
    def _signs(self) -> list[str]:
        """return the list of signs this dataset handles"""
        ...

    @abc.abstractmethod
    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """return a (input_tensor, label_tensor) pair for the given index"""
        ...

    # concrete dunder methods

    def __len__(self) -> int:
        # windows and labels are always the same length -- return either
        return len(self.labels)