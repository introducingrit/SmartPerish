
from pathlib import Path
import pandas as pd
import json

# ==========================================
# SMARTPERISH - DATA PREPROCESSING
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH DATA PREPROCESSING")
print("=" * 40)

# ==========================================
# 1. CHECK DATASET FILES
# ==========================================

required_files = [
    "train.csv",
    "test.csv",
    "stores.csv",
    "oil.csv",
    "holidays_events.csv",
    "transactions.csv"
]

for filename in required_files:
    if not (RAW_DIR / filename).exists():
        raise FileNotFoundError(
            f"Missing dataset: {filename}"
        )

print("All dataset files found!")

# ==========================================
# 2. LOAD TRAINING DATA
# ==========================================

print("\nLoading training dataset...")

train = pd.read_csv(
    RAW_DIR / "train.csv",
    parse_dates=["date"]
)

print("Original shape:", train.shape)

# ==========================================
# 3. REMOVE EXACT DUPLICATES
# ==========================================

before = len(train)

train = train.drop_duplicates()

duplicates_removed = before - len(train)

# ==========================================
# 4. HANDLE MISSING VALUES
# ==========================================

missing_before = int(
    train.isnull().sum().sum()
)

train["sales"] = pd.to_numeric(
    train["sales"],
    errors="coerce"
)

train["onpromotion"] = pd.to_numeric(
    train["onpromotion"],
    errors="coerce"
)

train = train.dropna(
    subset=[
        "date",
        "store_nbr",
        "family",
        "sales"
    ]
)

train["onpromotion"] = (
    train["onpromotion"].fillna(0)
)

# Remove invalid negative sales
train = train[train["sales"] >= 0]

# ==========================================
# 5. CHECK DUPLICATE TIME KEYS
# ==========================================

keys = [
    "date",
    "store_nbr",
    "family"
]

duplicate_keys = int(
    train.duplicated(subset=keys).sum()
)

if duplicate_keys > 0:
    train = (
        train.groupby(keys, as_index=False)
        .agg({
            "sales": "sum",
            "onpromotion": "max"
        })
    )

# ==========================================
# 6. SORT DATA
# ==========================================

train = train.sort_values(
    ["store_nbr", "family", "date"]
)

train.reset_index(drop=True, inplace=True)

# ==========================================
# 7. LOAD TEST DATA
# ==========================================

test = pd.read_csv(
    RAW_DIR / "test.csv",
    parse_dates=["date"]
)

# ==========================================
# 8. LOAD SUPPORTING DATA
# ==========================================

stores = pd.read_csv(
    RAW_DIR / "stores.csv"
)

oil = pd.read_csv(
    RAW_DIR / "oil.csv",
    parse_dates=["date"]
)

holidays = pd.read_csv(
    RAW_DIR / "holidays_events.csv",
    parse_dates=["date"]
)

transactions = pd.read_csv(
    RAW_DIR / "transactions.csv",
    parse_dates=["date"]
)

# Remove duplicate supporting records
stores = stores.drop_duplicates()

oil = (
    oil.drop_duplicates(subset=["date"])
    .sort_values("date")
)

holidays = holidays.drop_duplicates()

transactions = transactions.drop_duplicates()

# ==========================================
# 9. SAVE PROCESSED DATA
# ==========================================

print("\nSaving processed datasets...")

train.to_parquet(
    PROCESSED_DIR / "train_clean.parquet",
    index=False
)

test.to_parquet(
    PROCESSED_DIR / "test_clean.parquet",
    index=False
)

stores.to_csv(
    PROCESSED_DIR / "stores_clean.csv",
    index=False
)

oil.to_csv(
    PROCESSED_DIR / "oil_clean.csv",
    index=False
)

holidays.to_csv(
    PROCESSED_DIR / "holidays_clean.csv",
    index=False
)

transactions.to_csv(
    PROCESSED_DIR / "transactions_clean.csv",
    index=False
)

# ==========================================
# 10. GENERATE DATA QUALITY REPORT
# ==========================================

report = {
    "project": "SmartPerish",
    "training_rows": int(len(train)),
    "test_rows": int(len(test)),
    "stores": int(train["store_nbr"].nunique()),
    "product_families": int(train["family"].nunique()),
    "start_date": str(train["date"].min().date()),
    "end_date": str(train["date"].max().date()),
    "duplicates_removed": int(duplicates_removed),
    "duplicate_time_keys": int(duplicate_keys),
    "missing_values_before": missing_before,
    "missing_values_after": int(
        train.isnull().sum().sum()
    )
}

with open(
    REPORT_DIR / "data_quality_report.json",
    "w"
) as file:
    json.dump(report, file, indent=4)

# ==========================================
# 11. DISPLAY FINAL REPORT
# ==========================================

print("\nPREPROCESSING COMPLETED")
print("=" * 40)

for key, value in report.items():
    print(f"{key}: {value}")

print("\nProcessed data saved successfully!")
print("SMARTPERISH PHASE 1 - STEP 1 COMPLETED")
