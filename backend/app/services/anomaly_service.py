from app.utils.preprocess import load_audio_bytes, preprocess_signal
from app.models.pytorch_models import AnomalyAutoencoder


class AnomalyService:
    _model = None

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            cls._model = AnomalyAutoencoder.load_pretrained()
        return cls._model

    @classmethod
    def detect_from_bytes(cls, data: bytes):
        arr, sr = load_audio_bytes(data)
        x = preprocess_signal(arr, sr)
        model = cls._load_model()
        score = model.reconstruction_error(x)
        is_anom = float(score) > 0.1
        return float(score), bool(is_anom)
