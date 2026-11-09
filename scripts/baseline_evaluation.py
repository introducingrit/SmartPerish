
from pathlib import Path
import pandas as pd
import numpy as np
import json

# ==========================================
# SMARTPERISH - BASELINE MODEL EVALUATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "train_features.parquet"

REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH BASELINE MODEL")
print("=" * 45)

# ==========================================
# 1. LOAD FEATURE DATA
# ==========================================

print("\nLoading feature dataset...")

df = pd.read_parquet(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

print("Dataset shape:", df.shape)

# ==========================================
# 2. CHRONOLOGICAL TRAIN-TEST SPLIT
# ==========================================

print("\nCreating chronological validation split...")

last_date = df["date"].max()

# Use the last 16 calendar days for validation
validation_start = last_date - pd.Timedelta(days=15)

train = df[
    df["date"] < validation_start
].copy()

validation = df[
    df["date"] >= validation_start
].copy()

print("Training records:", len(train))
print("Validation records:", len(validation))

print("Training ends:", train["date"].max())
print("Validation starts:", validation["date"].min())
print("Validation ends:", validation["date"].max())

# ==========================================
# 3. DEFINE EVALUATION METRICS
# ==========================================

def calculate_metrics(actual, predicted):

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    mae = np.mean(
        np.abs(actual - predicted)
    )

    rmse = np.sqrt(
        np.mean((actual - predicted) ** 2)
    )

    total_actual = np.sum(np.abs(actual))

    if total_actual > 0:
        wape = (
            np.sum(np.abs(actual - predicted))
            / total_actual
        ) * 100
    else:
        wape = np.nan

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "WAPE": float(wape)
    }

# ==========================================
# 4. NAIVE FORECAST
# ==========================================

print("\nEvaluating naive forecast...")

validation["naive_prediction"] = (
    validation["lag_1"].clip(lower=0)
)

naive_metrics = calculate_metrics(
    validation["sales"],
    validation["naive_prediction"]
)

# ==========================================
# 5. SEASONAL NAIVE FORECAST
# ==========================================

print("Evaluating seasonal naive forecast...")

validation["seasonal_prediction"] = (
    validation["lag_7"].clip(lower=0)
)

seasonal_metrics = calculate_metrics(
    validation["sales"],
    validation["seasonal_prediction"]
)

# ==========================================
# 6. COMPARE RESULTS
# ==========================================

results = pd.DataFrame([
    {
        "Model": "Naive (Lag 1)",
        **naive_metrics
    },
    {
        "Model": "Seasonal Naive (Lag 7)",
        **seasonal_metrics
    }
])

print("\nBASELINE MODEL COMPARISON")
print("=" * 45)

print(results.to_string(index=False))

# ==========================================
# 7. SAVE RESULTS
# ==========================================

results.to_csv(
    REPORT_DIR / "baseline_results.csv",
    index=False
)

with open(
    REPORT_DIR / "baseline_results.json",
    "w"
) as file:

    json.dump(
        {
            "training_end": str(train["date"].max().date()),
            "validation_start": str(validation["date"].min().date()),
            "validation_end": str(validation["date"].max().date()),
            "naive": naive_metrics,
            "seasonal_naive": seasonal_metrics
        },
        file,
        indent=4
    )

# ==========================================
# 8. SAVE DAILY PREDICTIONS
# ==========================================

predictions = validation[
    [
        "date",
        "store_nbr",
        "family",
        "sales",
        "naive_prediction",
        "seasonal_prediction"
    ]
].copy()

predictions.to_csv(
    REPORT_DIR / "baseline_predictions.csv",
    index=False
)

# ==========================================
# 9. FINAL OUTPUT
# ==========================================

print("\nBASELINE EVALUATION COMPLETED!")
print("--------------------------------")

print("Results saved:")
print("- baseline_results.csv")
print("- baseline_results.json")
print("- baseline_predictions.csv")

print("\nSMARTPERISH STEP 2.2 COMPLETED!")
