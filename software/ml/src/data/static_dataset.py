from __future__ import annotations

import torch

from .base_dataset import ASLDataset
from .constants import STATIC_SIGNS


class StaticASLDataset(ASLDataset):
    """Dataset for static ASL signs (A-Y excluding J and Z).

    static signs are hand poses with no meaningful wrist motion.
    input to the model is the mean of each feature across the window --
    collapsing the time dimension since pose not motion is what matters.
    """

    def _signs(self) -> list[str]:
        """return the 24 static signs this dataset handles"""
        return STATIC_SIGNS

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """return a mean-pooled feature vector and its label.

        mean pooling collapses (window_size, n_features) --> (n_features,)
        discarding the time axis since static signs are defined by pose alone.
        """
        # retrieve the raw window -- shape (window_size, 21)
        window = self.windows[idx]

        # mean pool across the time axis (axis=0) -- shape (21,)
        # each feature becomes its average value over the 1-second window
        pooled = window.mean(axis=0)

        # convert to tensors -- float32 for input, int64 for label (CrossEntropyLoss requirement)
        x = torch.tensor(pooled, dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.int64)

        return x, y