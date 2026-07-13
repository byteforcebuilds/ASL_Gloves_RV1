from __future__ import annotations

import torch
from torch.utils.data import DataLoader


def train_one_epoch(model, loader: DataLoader, criterion, optimizer, device) -> float:
    """run one full pass over the training data, updating weights.

    returns the average training loss across all batches.
    """
    model.train()
    total_loss = 0.0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)

        optimizer.zero_grad()             # clear last step's gradients
        logits = model(xb)                # forward pass
        loss   = criterion(logits, yb)    # how wrong are we?
        loss.backward()                   # compute gradients
        optimizer.step()                  # nudge weights to reduce loss

        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate(model, loader: DataLoader, criterion, device) -> tuple[float, float]:
    """measure the model on data without learning from it.

    returns (average loss, accuracy). uses no_grad and never steps the
    optimizer, so model weights are left unchanged.
    """
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            total_loss += criterion(logits, yb).item()

            preds = logits.argmax(dim=1)              # guess = highest score
            correct += (preds == yb).sum().item()
            total   += yb.size(0)
    return total_loss / len(loader), correct / total
