import torch
import torch.nn as nn
import numpy as np
import os


class SignalClassifier:
    def __init__(self):
        # Simple linear classifier placeholder
        self.model = None

    @staticmethod
    def load_pretrained():
        # For prototype return an instance with simple predict_proba
        return SignalClassifier()

    def predict_proba(self, x: np.ndarray):
        # naive heuristic: average energy
        energy = np.mean(np.abs(x))
        # fake probabilities
        p_normal = max(0.0, 1 - energy)
        p_murmur = max(0.0, min(energy, 0.5))
        p_arr = max(0.0, energy - 0.5)
        probs = np.array([p_normal, p_murmur, p_arr])
        probs = probs / (probs.sum() + 1e-8)
        return probs


class AnomalyAutoencoder:
    def __init__(self):
        pass

    @staticmethod
    def load_pretrained():
        return AnomalyAutoencoder()

    def reconstruction_error(self, x: np.ndarray):
        # use variance as a proxy for anomaly score
        return float(np.var(x))
