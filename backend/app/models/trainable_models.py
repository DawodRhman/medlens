import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
import os


class Conv1DClassifier(nn.Module):
    def __init__(self, in_channels=1, n_classes=3):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, 16, kernel_size=9, stride=1, padding=4)
        self.bn1 = nn.BatchNorm1d(16)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=9, stride=2, padding=4)
        self.bn2 = nn.BatchNorm1d(32)
        self.conv3 = nn.Conv1d(32, 64, kernel_size=9, stride=2, padding=4)
        self.bn3 = nn.BatchNorm1d(64)
        self.adaptive = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(64, n_classes)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.adaptive(x).squeeze(-1)
        x = self.fc(x)
        return x


class SimpleAutoencoder(nn.Module):
    def __init__(self, in_channels=1, latent_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(in_channels, 16, kernel_size=9, padding=4),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=9, padding=4),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(32, latent_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Unflatten(1, (32, 1)),
            nn.Upsample(scale_factor=64, mode='linear', align_corners=False),
            nn.Conv1d(32, 16, kernel_size=9, padding=4),
            nn.ReLU(),
            nn.Conv1d(16, in_channels, kernel_size=9, padding=4),
            nn.Tanh(),
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out


def save_torchscript(model: nn.Module, example_input: torch.Tensor, dest: str):
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    scripted = torch.jit.trace(model.eval(), example_input)
    scripted.save(str(dest_path))


def export_onnx(model: nn.Module, example_input: torch.Tensor, dest: str):
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    torch.onnx.export(model, example_input, str(dest_path), opset_version=14, input_names=["input"], output_names=["output"]) 
