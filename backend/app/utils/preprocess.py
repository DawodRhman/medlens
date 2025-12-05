import numpy as np
import io
from scipy.signal import butter, filtfilt
import soundfile as sf


def load_audio_bytes(data: bytes):
    # Attempts to read audio bytes (wav/flac)
    bio = io.BytesIO(data)
    arr, sr = sf.read(bio)
    if arr.ndim > 1:
        arr = arr.mean(axis=1)
    return np.asarray(arr, dtype=np.float32), int(sr)


def bandpass_filter(signal, sr, low=20.0, high=800.0, order=4):
    nyq = 0.5 * sr
    lowc = low / nyq
    highc = high / nyq
    b, a = butter(order, [lowc, highc], btype='band')
    return filtfilt(b, a, signal)


def preprocess_signal(arr, sr, segment_seconds=5.0):
    # apply bandpass
    sig = bandpass_filter(arr, sr)
    # normalize to -1..1
    sig = sig / (np.max(np.abs(sig)) + 1e-8)
    # segment or pad to segment_seconds
    target = int(segment_seconds * sr)
    if len(sig) >= target:
        sig = sig[:target]
    else:
        pad = np.zeros(target, dtype=sig.dtype)
        pad[:len(sig)] = sig
        sig = pad
    return sig
