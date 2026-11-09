
from pathlib import Path
import pandas as pd
import numpy as np

# ==========================================
# SMARTPERISH - FEATURE ENGINEERING
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "train_clean.parquet"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

print("\nSMARTPERISH FEATURE ENGINEERING")
print("=" * 45)

# ==========================================
# 1. LOAD DATA
# ==========================================

print("\nLoading processed dataset...")

df = pd.read_parquet(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

# Sort chronologically within each product-store series
df = df.sort_values(
    ["store_nbr", "family", "date"]
).reset_index(drop=True)

print("Dataset loaded:", df.shape)

# ==========================================
# 2. CALENDAR FEATURES
# ==========================================

print("\nCreating calendar features...")

df["day"] = df["date"].dt.day

df["month"] = df["date"].dt.month

df["year"] = df["date"].dt.year

df["weekday"] = df["date"].dt.dayofweek

df["is_weekend"] = (
    df["weekday"] >= 5
).astype("int8")

df["week_of_year"] = (
    df["date"].dt.isocalendar().week.astype("int16")
)

# ==========================================
# 3. LAG FEATURES
# ==========================================

print("Creating lag features...")

group_keys = ["store_nbr", "family"]

grouped_sales = df.groupby(
    group_keys,
    sort=False
)["sales"]

for lag in [1, 7, 14, 28]:

    df[f"lag_{lag}"] = grouped_sales.shift(lag)

# ==========================================
# 4. ROLLING FEATURES
# ==========================================

print("Creating rolling averages...")

for window in [7, 14, 28]:

    df[f"rolling_mean_{window}"] = (
        df.groupby(group_keys, sort=False)["sales"]
        .transform(
            lambda s: s.shift(1).rolling(
                window=window,
                min_periods=1
            ).mean()
        )
    )

# ==========================================
# 5. CLEAN FEATURE DATA
# ==========================================

print("Cleaning feature data...")

# Initial observations have no 28-day history.
# Remove these rows for consistent lag availability.

df = df.dropna(
    subset=[
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28"
    ]
).copy()

# Fill remaining rolling feature gaps if any
rolling_columns = [
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28"
]

df[rolling_columns] = (
    df[rolling_columns].fillna(0)
)

# ==========================================
# 6. CATEGORICAL FEATURES
# ==========================================

df["store_nbr"] = df["store_nbr"].astype("category")

df["family"] = df["family"].astype("category")

# ==========================================
# 7. SELECT FINAL FEATURES
# ==========================================

feature_columns = [
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

target_column = "sales"

# ==========================================
# 8. SAVE FEATURE DATASET
# ==========================================

output_path = OUTPUT_DIR / "train_features.parquet"

df.to_parquet(
    output_path,
    index=False
)

# ==========================================
# 9. DISPLAY SUMMARY
# ==========================================

print("\nFEATURE ENGINEERING COMPLETED")
print("=" * 45)

print("Final dataset shape:", df.shape)

print("\nFeatures created:")

for feature in feature_columns:
    print("-", feature)

print("\nTarget variable:", target_column)

print("\nDate range:")
print(df["date"].min(), "to", df["date"].max())

print("\nSaved to:", output_path)

print("\nSMARTPERISH STEP 2.1 COMPLETED!")
