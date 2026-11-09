
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_PATH = BASE_DIR / "data" / "raw" / "train.csv"
CLEAN_TRAIN_PATH = BASE_DIR / "data" / "processed" / "train_features.parquet"
TEST_PATH = BASE_DIR / "data" / "processed" / "test_clean.parquet"

MODEL_PATH = (
    BASE_DIR / "ml" / "saved_models" / "xgboost_demand_model.json"
)

REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - 7 DAY DEMAND FORECAST")
print("=" * 50)

# Load model
model = xgb.XGBRegressor()
model.load_model(str(MODEL_PATH))

# Load historical sales and future test dates/promotions
history_df = pd.read_csv(TRAIN_PATH)
history_df["date"] = pd.to_datetime(history_df["date"])
history_df["sales"] = pd.to_numeric(
    history_df["sales"], errors="coerce"
).fillna(0)

test_df = pd.read_parquet(TEST_PATH)
test_df["date"] = pd.to_datetime(test_df["date"])
test_df["onpromotion"] = pd.to_numeric(
    test_df["onpromotion"], errors="coerce"
).fillna(0)

# Load category definitions used during training
feature_df = pd.read_parquet(CLEAN_TRAIN_PATH)

store_categories = sorted(feature_df["store_nbr"].unique())
family_categories = sorted(feature_df["family"].unique())

print("Historical records:", len(history_df))
print("Future test records:", len(test_df))

# Select the first seven future dates
future_dates = sorted(test_df["date"].unique())[:7]

if len(future_dates) != 7:
    raise ValueError("The test dataset does not contain 7 future dates.")

last_history_date = history_df["date"].max()

if pd.Timestamp(future_dates[0]) != (
    last_history_date + pd.Timedelta(days=1)
):
    raise ValueError("Future dates do not immediately follow historical data.")

print("Historical data ends:", last_history_date.date())
print("Forecast starts:", pd.Timestamp(future_dates[0]).date())
print("Forecast ends:", pd.Timestamp(future_dates[-1]).date())

# Create historical sales lists for every store-product family
history = {}

for (store, family), group in history_df.groupby(
    ["store_nbr", "family"], observed=True
):
    group = group.sort_values("date")
    history[(store, family)] = group["sales"].astype(float).tolist()

# Forecast one day at a time
all_forecasts = []

FEATURES = [
    "store_nbr", "family", "onpromotion", "day", "month", "year",
    "weekday", "is_weekend", "week_of_year", "lag_1", "lag_7",
    "lag_14", "lag_28", "rolling_mean_7", "rolling_mean_14",
    "rolling_mean_28"
]

for forecast_date in future_dates:

    day_data = test_df[
        test_df["date"] == forecast_date
    ].copy()

    records = []

    # Generate features using only available historical values
    for _, row in day_data.iterrows():

        store = row["store_nbr"]
        family = row["family"]
        key = (store, family)

        if key not in history or len(history[key]) < 28:
            raise ValueError(
                f"Insufficient history for store {store}, family {family}"
            )

        values = history[key]
        date = pd.Timestamp(forecast_date)

        records.append({
            "store_nbr": store,
            "family": family,
            "onpromotion": float(row["onpromotion"]),
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "weekday": date.dayofweek,
            "is_weekend": int(date.dayofweek >= 5),
            "week_of_year": int(date.isocalendar().week),
            "lag_1": values[-1],
            "lag_7": values[-7],
            "lag_14": values[-14],
            "lag_28": values[-28],
            "rolling_mean_7": np.mean(values[-7:]),
            "rolling_mean_14": np.mean(values[-14:]),
            "rolling_mean_28": np.mean(values[-28:])
        })

    # Convert features into a DataFrame
    X_future = pd.DataFrame(records, columns=FEATURES)

    # Match categorical definitions used during training
    X_future["store_nbr"] = pd.Categorical(
        X_future["store_nbr"],
        categories=store_categories
    )

    X_future["family"] = pd.Categorical(
        X_future["family"],
        categories=family_categories
    )

    # Predict the entire day
    predictions = np.maximum(model.predict(X_future), 0)

    # Store predictions and update history after the day's predictions
    for (_, row), prediction in zip(day_data.iterrows(), predictions):

        store = row["store_nbr"]
        family = row["family"]
        key = (store, family)

        all_forecasts.append({
            "date": pd.Timestamp(forecast_date),
            "store_nbr": store,
            "family": family,
            "onpromotion": row["onpromotion"],
            "predicted_sales": float(prediction)
        })

    # Update history only after predicting all products for this day
    for (_, row), prediction in zip(day_data.iterrows(), predictions):
        key = (row["store_nbr"], row["family"])
        history[key].append(float(prediction))

    print(
        "Completed forecast for:",
        pd.Timestamp(forecast_date).date()
    )

# Save detailed forecasts
forecast_df = pd.DataFrame(all_forecasts)

forecast_path = REPORT_DIR / "forecast_next_7_days.csv"
forecast_df.to_csv(forecast_path, index=False)

# Create daily summary
daily_summary = forecast_df.groupby("date")[
    "predicted_sales"
].sum().reset_index()

daily_summary.rename(
    columns={"predicted_sales": "total_predicted_sales"},
    inplace=True
)

daily_path = REPORT_DIR / "forecast_daily_summary.csv"
daily_summary.to_csv(daily_path, index=False)

print("\nSEVEN-DAY FORECAST COMPLETED")
print("=" * 50)

print("\nDaily Forecast:")
print(daily_summary.to_string(index=False))

print("\nTotal predicted sales for 7 days:",
      round(forecast_df["predicted_sales"].sum(), 2))

print("\nForecast records:", len(forecast_df))

print("\nSaved files:")
print("- outputs/reports/forecast_next_7_days.csv")
print("- outputs/reports/forecast_daily_summary.csv")

print("\nSMARTPERISH STEP 2.5 COMPLETED!")
