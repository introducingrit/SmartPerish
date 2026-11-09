
from pathlib import Path
import pandas as pd
import numpy as np
import json
import time

from xgboost import XGBRegressor

# ==========================================
# SMARTPERISH - XGBOOST MODEL TRAINING
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "train_features.parquet"

REPORT_DIR = BASE_DIR / "outputs" / "reports"
MODEL_DIR = BASE_DIR / "ml" / "saved_models"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - XGBOOST TRAINING")
print("=" * 50)

# ==========================================
# 1. LOAD DATASET
# ==========================================

print("\nLoading feature dataset...")

df = pd.read_parquet(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

print("Dataset shape:", df.shape)

# ==========================================
# 2. DEFINE FEATURES AND TARGET
# ==========================================

FEATURES = [
    "store_nbr",
    "family",
    "onpromotion",
    "day",
    "month",
    "year",
    "weekday",
    "is_weekend",
    "week_of_year",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28"
]

TARGET = "sales"

# Preserve categorical data types
df["store_nbr"] = df["store_nbr"].astype("category")
df["family"] = df["family"].astype("category")

# ==========================================
# 3. CHRONOLOGICAL TRAIN-VALIDATION SPLIT
# ==========================================

print("\nPreparing chronological split...")

last_date = df["date"].max()

validation_start = (
    last_date - pd.Timedelta(days=15)
)

train = df[
    df["date"] < validation_start
].copy()

validation = df[
    df["date"] >= validation_start
].copy()

print("Training rows:", len(train))
print("Validation rows:", len(validation))

print("Training ends:", train["date"].max())
print("Validation starts:", validation["date"].min())
print("Validation ends:", validation["date"].max())

# ==========================================
# 4. PREPARE INPUT AND TARGET
# ==========================================

X_train = train[FEATURES]
y_train = train[TARGET]

X_val = validation[FEATURES]
y_val = validation[TARGET]

# ==========================================
# 5. INITIALIZE XGBOOST MODEL
# ==========================================

print("\nInitializing XGBoost...")

model = XGBRegressor(

    objective="reg:squarederror",

    n_estimators=300,

    learning_rate=0.05,

    max_depth=8,

    min_child_weight=5,

    subsample=0.8,

    colsample_bytree=0.8,

    reg_lambda=5,

    tree_method="hist",

    enable_categorical=True,

    eval_metric="mae",

    n_jobs=-1,

    random_state=42

)

# ==========================================
# 6. TRAIN MODEL
# ==========================================

print("\nTraining XGBoost model...")
print("This may take several minutes.")

start_time = time.time()

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=50
)

training_time = time.time() - start_time

print("\nTraining completed!")

print(
    "Training time:",
    round(training_time, 2),
    "seconds"
)

# ==========================================
# 7. GENERATE PREDICTIONS
# ==========================================

print("\nGenerating validation predictions...")

predictions = model.predict(X_val)

# Sales cannot be negative
predictions = np.maximum(predictions, 0)

# ==========================================
# 8. CALCULATE PERFORMANCE METRICS
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

    wape = (
        np.sum(np.abs(actual - predicted))
        / np.sum(np.abs(actual))
    ) * 100

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "WAPE": float(wape)
    }


xgb_metrics = calculate_metrics(
    y_val,
    predictions
)

print("\nXGBOOST PERFORMANCE")
print("=" * 40)

for metric, value in xgb_metrics.items():
    print(f"{metric}: {value:.4f}")

# ==========================================
# 9. COMPARE WITH BASELINE MODELS
# ==========================================

baseline_path = REPORT_DIR / "baseline_results.csv"

baseline = pd.read_csv(baseline_path)

comparison = baseline.copy()

comparison = pd.concat(
    [
        comparison,
        pd.DataFrame([{
            "Model": "XGBoost",
            **xgb_metrics
        }])
    ],
    ignore_index=True
)

print("\nMODEL COMPARISON")
print("=" * 50)

print(comparison.to_string(index=False))

# ==========================================
# 10. SAVE MODEL
# ==========================================

model_path = MODEL_DIR / "xgboost_demand_model.json"

model.save_model(model_path)

print("\nModel saved:", model_path)

# ==========================================
# 11. SAVE PREDICTIONS
# ==========================================

prediction_df = validation[
    ["date", "store_nbr", "family", "sales"]
].copy()

prediction_df["xgboost_prediction"] = predictions

prediction_df.to_csv(
    REPORT_DIR / "xgboost_predictions.csv",
    index=False
)

# ==========================================
# 12. SAVE COMPARISON REPORT
# ==========================================

comparison.to_csv(
    REPORT_DIR / "model_comparison.csv",
    index=False
)

report = {
    "model": "XGBoost",
    "training_rows": int(len(train)),
    "validation_rows": int(len(validation)),
    "training_start": str(train["date"].min().date()),
    "training_end": str(train["date"].max().date()),
    "validation_start": str(validation["date"].min().date()),
    "validation_end": str(validation["date"].max().date()),
    "training_time_seconds": round(training_time, 2),
    "metrics": xgb_metrics
}

with open(
    REPORT_DIR / "xgboost_report.json",
    "w"
) as file:
    json.dump(report, file, indent=4)

# ==========================================
# 13. FINAL RESULT
# ==========================================

print("\nXGBOOST TRAINING COMPLETED")
print("=" * 50)

print("Saved files:")
print("- ml/saved_models/xgboost_demand_model.json")
print("- outputs/reports/xgboost_predictions.csv")
print("- outputs/reports/model_comparison.csv")
print("- outputs/reports/xgboost_report.json")

print("\nSMARTPERISH STEP 2.3 COMPLETED!")
