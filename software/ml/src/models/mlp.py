from __future__ import annotations

import torch.nn as nn


class StaticMLP(nn.Module):
    """MLP for static ASL signs.

    operates on a mean-pooled pose vector (n_features,) -- the time axis is
    already averaged away by StaticASLDataset, so there is no sequence to
    convolve over and a fully-connected network is the natural fit.
    """

    def __init__(self, n_features: int = 21, n_classes: int = 24) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),   # 21 -> 64 pattern detectors
            nn.ReLU(),
            nn.Linear(64, 32),           # 64 -> 32 combined patterns
            nn.ReLU(),
            nn.Linear(32, n_classes),    # 32 -> 24 scores, one per letter
        )

    def forward(self, x):
        return self.net(x)
