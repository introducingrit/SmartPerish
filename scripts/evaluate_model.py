
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "outputs" / "reports"
PLOT_DIR = BASE_DIR / "outputs" / "plots"
MODEL_PATH = BASE_DIR / "ml" / "saved_models" / "xgboost_demand_model.json"

PLOT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - MODEL EVALUATION")
print("=" * 45)

# Load validation predictions
df = pd.read_csv(REPORT_DIR / "xgboost_predictions.csv")
df["date"] = pd.to_datetime(df["date"])

print("Validation records:", len(df))

# 1. Actual vs Predicted scatter plot
sample = df.sample(
    n=min(5000, len(df)),
    random_state=42
)

plt.figure(figsize=(9, 6))
plt.scatter(
    sample["sales"],
    sample["xgboost_prediction"],
    alpha=0.3
)

max_value = max(
    sample["sales"].max(),
    sample["xgboost_prediction"].max()
)

plt.plot([0, max_value], [0, max_value], linestyle="--")
plt.xlabel("Actual Sales")
plt.ylabel("Predicted Sales")
plt.title("Actual vs Predicted Sales")
plt.tight_layout()
plt.savefig(PLOT_DIR / "actual_vs_predicted.png", dpi=150)
plt.close()

# 2. Daily total sales comparison
daily = df.groupby("date")[
    ["sales", "xgboost_prediction"]
].sum()

plt.figure(figsize=(12, 6))
plt.plot(daily.index, daily["sales"], label="Actual Sales")
plt.plot(
    daily.index,
    daily["xgboost_prediction"],
    label="Predicted Sales"
)
plt.xlabel("Date")
plt.ylabel("Total Sales")
plt.title("Daily Actual vs Predicted Sales")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOT_DIR / "daily_prediction_comparison.png", dpi=150)
plt.close()

# 3. Feature importance
model = xgb.XGBRegressor()
model.load_model(str(MODEL_PATH))

importance = pd.DataFrame({
    "Feature": model.feature_names_in_,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

top_features = importance.head(15).sort_values(
    by="Importance"
)

plt.figure(figsize=(10, 7))
plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)
plt.xlabel("Importance Score")
plt.title("Top 15 Demand Forecasting Features")
plt.tight_layout()
plt.savefig(PLOT_DIR / "feature_importance.png", dpi=150)
plt.close()

# Save feature importance data
importance.to_csv(
    REPORT_DIR / "feature_importance.csv",
    index=False
)

print("\nEVALUATION COMPLETED!")
print("\nTop 10 Important Features:")
print(importance.head(10).to_string(index=False))

print("\nGenerated plots:")
print("- actual_vs_predicted.png")
print("- daily_prediction_comparison.png")
print("- feature_importance.png")

print("\nSMARTPERISH STEP 2.4 COMPLETED!")
