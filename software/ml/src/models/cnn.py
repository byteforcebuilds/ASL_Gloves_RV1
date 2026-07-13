from __future__ import annotations

import torch.nn as nn


class DynamicCNN(nn.Module):
    """1D CNN for dynamic ASL signs.

    operates on the full (n_channels, window_size) motion sequence kept by
    DynamicASLDataset. convolutional filters slide along the time axis to
    detect motion patterns regardless of when they occur in the window.
    """

    def __init__(self, n_channels: int = 21, n_classes: int = 16) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(n_channels, 32, kernel_size=5, padding=2),  # detect short motions
            nn.ReLU(),
            nn.MaxPool1d(2),                                      # 100 -> 50 timesteps

            nn.Conv1d(32, 64, kernel_size=5, padding=2),          # combine into bigger motions
            nn.ReLU(),
            nn.MaxPool1d(2),                                      # 50 -> 25 timesteps

            nn.AdaptiveAvgPool1d(1),   # collapse time: one summary per filter
            nn.Flatten(),              # (64, 1) -> (64,)
            nn.Linear(64, n_classes),  # 64 -> 16 scores, one per sign
        )

    def forward(self, x):
        return self.net(x)
