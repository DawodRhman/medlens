from prometheus_client import Counter, Histogram

PREDICTIONS = Counter('medlens_predictions_total', 'Total predictions')
PREDICTION_LATENCY = Histogram('medlens_prediction_latency_seconds', 'Prediction latency')
