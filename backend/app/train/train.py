"""
Train a small 1D CNN classifier and a simple autoencoder on synthetic signals
and export models to `../models/` as TorchScript and ONNX for inference.

This is a minimal example for development and testing.
"""
import numpy as np
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
from app.models.trainable_models import Conv1DClassifier, SimpleAutoencoder, save_torchscript, export_onnx


class SyntheticDataset(Dataset):
    def __init__(self, n=120, length=10000, sr=2000):
        self.X = []
        self.y = []
        for i in range(n):
            if i % 3 == 0:
                x = 0.1 * np.sin(2 * np.pi * 50 * np.arange(length) / sr)
                self.y.append(0)
            elif i % 3 == 1:
                x = 0.1 * np.sin(2 * np.pi * 150 * np.arange(length) / sr) + 0.05 * np.random.randn(length)
                self.y.append(1)
            else:
                x = np.random.randn(length) * 0.2
                self.y.append(2)
            self.X.append(x.astype(np.float32))
        self.X = np.stack(self.X)
        self.y = np.array(self.y)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        x = self.X[idx]
        x = x.reshape(1, -1)
        return torch.from_numpy(x), int(self.y[idx])


def train_classifier(out_dir: Path, epochs=4):
    ds = SyntheticDataset(n=150)
    dl = DataLoader(ds, batch_size=8, shuffle=True)
    model = Conv1DClassifier(in_channels=1, n_classes=3)
    opt = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        model.train()
        total = 0
        correct = 0
        for xb, yb in dl:
            opt.zero_grad()
            out = model(xb)
            loss = loss_fn(out, yb)
            loss.backward()
            opt.step()
            preds = out.argmax(dim=1)
            total += yb.size(0)
            correct += (preds == yb).sum().item()
        print(f"Epoch {epoch+1}/{epochs} acc={correct/total:.3f}")
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "classifier.pt")
    # export torchscript
    example = torch.randn(1, 1, ds.X.shape[1])
    save_torchscript(model, example, out_dir / "classifier_script.pt")
    # export onnx
    export_onnx(model, example, out_dir / "classifier.onnx")


def train_autoencoder(out_dir: Path, epochs=4):
    ds = SyntheticDataset(n=150)
    dl = DataLoader(ds, batch_size=8, shuffle=True)
    model = SimpleAutoencoder(in_channels=1, latent_dim=64)
    opt = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for xb, _ in dl:
            opt.zero_grad()
            out = model(xb)
            loss = loss_fn(out, xb)
            loss.backward()
            opt.step()
            total_loss += loss.item()
        print(f"AE Epoch {epoch+1}/{epochs} avg_loss={total_loss/len(dl):.6f}")
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "autoencoder.pt")
    example = torch.randn(1, 1, ds.X.shape[1])
    save_torchscript(model, example, out_dir / "autoencoder_script.pt")
    export_onnx(model, example, out_dir / "autoencoder.onnx")


def main():
    out = Path(__file__).resolve().parents[2] / "models"
    print("Training classifier and autoencoder into:", out)
    train_classifier(out)
    train_autoencoder(out)


if __name__ == '__main__':
    main()
