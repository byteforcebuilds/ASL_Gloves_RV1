from __future__ import annotations

import torch

from .base_dataset import ASLDataset
from .constants import DYNAMIC_SIGNS


class DynamicASLDataset(ASLDataset):
    """Dataset for dynamic ASL signs (J, Z, and 14 common words).

    dynamic signs require wrist motion to perform correctly.
    input to the model is the full 100-timestep sequence --
    preserving the time axis since motion pattern is what matters.
    """

    def _signs(self) -> list[str]:
        """return the 16 dynamic signs this dataset handles"""
        return DYNAMIC_SIGNS

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """return a full sequence window and its label.

        the full (window_size, n_features) shape is preserved --
        the 1D CNN needs the temporal dimension to learn motion patterns.
        channels are transposed to (n_features, window_size) since
        pytorch Conv1d expects (batch, channels, length).
        """
        # retrieve the raw window -- shape (window_size, 21) i.e. (100, 21)
        window = self.windows[idx]

        # transpose to (n_features, window_size) i.e. (21, 100)
        # Conv1d expects (channels, length) not (length, channels)
        transposed = window.T

        # convert to tensors -- float32 for input, int64 for label
        x = torch.tensor(transposed, dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.int64)

        return x, y