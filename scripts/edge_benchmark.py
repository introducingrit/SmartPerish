
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb
import time
import json

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR / "ml" / "saved_models" / "xgboost_demand_model.json"
)

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "train_features.parquet"
)

REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "store_nbr", "family", "onpromotion", "day", "month", "year",
    "weekday", "is_weekend", "week_of_year", "lag_1", "lag_7",
    "lag_14", "lag_28", "rolling_mean_7", "rolling_mean_14",
    "rolling_mean_28"
]

print("\nSMARTPERISH - EDGE AI BENCHMARK")
print("=" * 50)

# Load the existing model
model = xgb.XGBRegressor()
model.load_model(str(MODEL_PATH))

# Load data and prepare categorical features
df = pd.read_parquet(DATA_PATH)

df["store_nbr"] = df["store_nbr"].astype("category")
df["family"] = df["family"].astype("category")

# Select 100 records for testing
sample = df.tail(100).copy()
X = sample[FEATURES]

print("Model loaded successfully.")
print("Test records:", len(X))

# Warm-up runs (not included in benchmark)
for _ in range(5):
    model.predict(X)

# Benchmark repeated local inference
iterations = 100
latencies = []

for _ in range(iterations):
    start = time.perf_counter()
    raw_predictions = model.predict(X)
    predictions = np.maximum(raw_predictions, 0)
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

latencies = np.array(latencies)

total_time = latencies.sum()
mean_latency = float(np.mean(latencies))
median_latency = float(np.median(latencies))
p95_latency = float(np.percentile(latencies, 95))

throughput = (len(X) * iterations) / total_time

# Validate predictions
negative_raw = int(np.sum(raw_predictions < 0))
negative_final = int(np.sum(predictions < 0))

model_size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)

report = {
    "model": "XGBoost Local Edge Inference",
    "test_records_per_run": len(X),
    "benchmark_iterations": iterations,
    "mean_latency_ms": round(mean_latency * 1000, 4),
    "median_latency_ms": round(median_latency * 1000, 4),
    "p95_latency_ms": round(p95_latency * 1000, 4),
    "throughput_records_per_second": round(throughput, 2),
    "model_size_mb": round(model_size_mb, 2),
    "negative_raw_predictions": negative_raw,
    "negative_final_predictions": negative_final,
    "prediction_validation": (
        "PASSED" if negative_final == 0 else "FAILED"
    )
}

output_path = REPORT_DIR / "edge_benchmark_report.json"

with open(output_path, "w") as file:
    json.dump(report, file, indent=4)

print("\nBENCHMARK RESULTS")
print("=" * 50)

for key, value in report.items():
    print(f"{key}: {value}")

print("\nSaved:", output_path)
print("\nEDGE AI BENCHMARK COMPLETED!")
