from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.data import StaticASLDataset, DynamicASLDataset
from src.models import StaticMLP, DynamicCNN
from src.engine import train_one_epoch, evaluate

# --- config -------------------------------------------------------------
MODEL      = 'static'   # 'static' or 'dynamic'
EPOCHS     = 15
BATCH_SIZE = 64
LR         = 1e-3
DATA_DIR   = Path(__file__).resolve().parent.parent / 'data'
CKPT_DIR   = Path(__file__).resolve().parent.parent / 'checkpoints'

# maps the MODEL string to its dataset class, model class, and checkpoint name
REGISTRY = {
    'static':  (StaticASLDataset,  StaticMLP,   'static_mlp_best.pt'),
    'dynamic': (DynamicASLDataset, DynamicCNN,  'dynamic_cnn_best.pt'),
}
# ------------------------------------------------------------------------


def get_device() -> str:
    if torch.backends.mps.is_available():
        return 'mps'
    if torch.cuda.is_available():
        return 'cuda'
    return 'cpu'


def main() -> None:
    dataset_cls, model_cls, ckpt_name = REGISTRY[MODEL]
    CKPT_DIR.mkdir(exist_ok=True)
    ckpt_path = CKPT_DIR / ckpt_name
    device = get_device()
    print(f'model: {MODEL} | device: {device}')

    # datasets + loaders
    train_ds = dataset_cls(DATA_DIR, split='train')
    val_ds   = dataset_cls(DATA_DIR, split='val')
    test_ds  = dataset_cls(DATA_DIR, split='test')
    print(f'train: {len(train_ds)} | val: {len(val_ds)} | test: {len(test_ds)}')

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False)

    # derive model dimensions from the data so they can never drift out of sync
    # sample shape is (n_features,) for static and (n_channels, window_size) for
    # dynamic -- shape[0] is the sensor-channel count in both cases
    n_inputs  = train_ds[0][0].shape[0]
    n_classes = len(train_ds._signs())
    print(f'inputs: {n_inputs} | classes: {n_classes}')

    # model, loss, optimizer
    model     = model_cls(n_inputs, n_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    # train, tracking the best validation accuracy
    best_val_acc = 0.0
    for epoch in range(1, EPOCHS + 1):
        train_loss        = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        flag = ''
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), ckpt_path)
            flag = '  <- best so far (saved)'

        print(f'epoch {epoch:2d}/{EPOCHS}  |  train loss {train_loss:.3f}  |  '
              f'val loss {val_loss:.3f}  |  val acc {val_acc:.1%}{flag}')

    # final honest score on the untouched test set, using the best checkpoint
    best_model = model_cls(n_inputs, n_classes).to(device)
    best_model.load_state_dict(torch.load(ckpt_path))
    test_loss, test_acc = evaluate(best_model, test_loader, criterion, device)

    print(f'\nbest val accuracy:  {best_val_acc:.1%}')
    print(f'test accuracy:      {test_acc:.1%}')
    print(f'test loss:          {test_loss:.3f}')


if __name__ == '__main__':
    main()
