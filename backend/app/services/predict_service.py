import io
import numpy as np
import os
from pathlib import Path
import torch
from app.utils.preprocess import load_audio_bytes, preprocess_signal
from app.models.pytorch_models import SignalClassifier


class PredictService:
    _model = None
    _onnx = None

    @classmethod
    def _model_paths(cls):
        base = Path(os.getcwd())
        # look in ./models by default (inside container or repo backend/models)
        return {
            "torchscript": base / "models" / "classifier_script.pt",
            "torch_state": base / "models" / "classifier.pt",
            "onnx": base / "models" / "classifier.onnx",
        }

    @classmethod
    def _load_model(cls):
        if cls._model is not None:
            return cls._model
        paths = cls._model_paths()
        # Prefer TorchScript
        if paths["torchscript"].exists():
            cls._model = torch.jit.load(str(paths["torchscript"]))
            cls._model.eval()
            return cls._model
        # Fallback to state_dict-loaded python model
        if paths["torch_state"].exists():
            model = SignalClassifier()
            model_path = str(paths["torch_state"])
            state = torch.load(model_path, map_location="cpu")
            try:
                model.load_state_dict(state)
            except Exception:
                # maybe saved whole model
                model = state
            model.eval()
            cls._model = model
            return cls._model
        # no real model: use python heuristic model
        cls._model = SignalClassifier.load_pretrained()
        return cls._model

    @classmethod
    def predict_from_bytes(cls, data: bytes):
        arr, sr = load_audio_bytes(data)
        x = preprocess_signal(arr, sr)
        model = cls._load_model()
        # ensure input shape: (B, C, L)
        if isinstance(model, torch.jit.ScriptModule) or hasattr(model, "forward"):
            try:
                inp = torch.tensor(x, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                with torch.no_grad():
                    out = model(inp)
                probs = torch.softmax(out.squeeze(0), dim=-1).cpu().numpy()
                idx = int(np.argmax(probs))
                labels = ["normal", "murmur", "arrhythmia"]
                return labels[idx], float(probs[idx])
            except Exception:
                # fallback to heuristic
                pass
        # fallback: heuristic stub
        probs = SignalClassifier().predict_proba(x)
        idx = int(np.argmax(probs))
        labels = ["normal", "murmur", "arrhythmia"]
        return labels[idx], float(probs[idx])
