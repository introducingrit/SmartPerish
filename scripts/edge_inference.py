
from pathlib import Path
import pandas as pd
import xgboost as xgb
import time

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR / "ml" / "saved_models" / "xgboost_demand_model.json"
)

DATA_PATH = (
    BASE_DIR / "outputs" / "reports" / "xgboost_predictions.csv"
)

print("\nSMARTPERISH - LOCAL EDGE AI INFERENCE")
print("=" * 50)

# Load the trained model locally
model = xgb.XGBRegressor()
model.load_model(str(MODEL_PATH))

# Load historical validation samples for testing
df = pd.read_parquet(
    BASE_DIR / "data" / "processed" / "train_features.parquet"
)

FEATURES = [
    "store_nbr", "family", "onpromotion", "day", "month", "year",
    "weekday", "is_weekend", "week_of_year", "lag_1", "lag_7",
    "lag_14", "lag_28", "rolling_mean_7", "rolling_mean_14",
    "rolling_mean_28"
]

TARGET = "sales"

# Take a small sample for local inference testing
sample = df.tail(100).copy()

sample["store_nbr"] = sample["store_nbr"].astype("category")
sample["family"] = sample["family"].astype("category")

X = sample[FEATURES]

print("Model loaded successfully.")
print("Inference records:", len(X))

# Run inference and measure time
start = time.perf_counter()

import numpy as np

predictions = model.predict(X)
predictions = np.maximum(predictions, 0)

elapsed = time.perf_counter() - start

# Save predictions
results = sample[["date", "store_nbr", "family", TARGET]].copy()

results["predicted_sales"] = predictions

output_path = (
    BASE_DIR / "outputs" / "reports" / "edge_inference_results.csv"
)

results.to_csv(output_path, index=False)

print("\nLOCAL INFERENCE RESULTS")
print("Predictions generated:", len(predictions))
print("Average predicted sales:", round(float(predictions.mean()), 2))
print("Inference time:", round(elapsed * 1000, 2), "milliseconds")

print("\nFirst 10 predictions:")
print(results.head(10).to_string(index=False))

print("\nSaved:", output_path)

print("\nLOCAL EDGE INFERENCE COMPLETED!")
