
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================
# SMARTPERISH - EXPLORATORY DATA ANALYSIS
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "train_clean.parquet"
PLOT_DIR = BASE_DIR / "outputs" / "plots"

PLOT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - EDA STARTED")
print("=" * 40)

# Load processed data
df = pd.read_parquet(DATA_PATH)

# =====================================
# 1. BASIC DATASET INFORMATION
# =====================================

print("\nDataset Shape:", df.shape)

print("\nDataset Information:")
print(df.info())

print("\nStatistical Summary:")
print(df[["sales", "onpromotion"]].describe())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nNumber of Stores:", df["store_nbr"].nunique())

print("\nProduct Families:", df["family"].nunique())

# =====================================
# 2. DAILY SALES TREND
# =====================================

daily_sales = df.groupby("date")["sales"].sum()

plt.figure(figsize=(12, 5))

daily_sales.plot()

plt.title("Daily Grocery Sales Trend")
plt.xlabel("Date")
plt.ylabel("Total Sales")

plt.tight_layout()

plt.savefig(PLOT_DIR / "daily_sales.png")
plt.close()

# =====================================
# 3. PRODUCT FAMILY SALES
# =====================================

family_sales = (
    df.groupby("family")["sales"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 7))

family_sales.plot(kind="bar")

plt.title("Sales by Product Family")
plt.xlabel("Product Family")
plt.ylabel("Total Sales")

plt.xticks(rotation=70)

plt.tight_layout()

plt.savefig(PLOT_DIR / "family_sales.png")
plt.close()

# =====================================
# 4. WEEKDAY SALES PATTERN
# =====================================

df["weekday"] = df["date"].dt.day_name()

weekday_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
    "Sunday"
]

weekday_sales = (
    df.groupby("weekday")["sales"]
    .mean()
    .reindex(weekday_order)
)

plt.figure(figsize=(10, 5))

weekday_sales.plot(kind="bar")

plt.title("Average Sales by Weekday")
plt.xlabel("Weekday")
plt.ylabel("Average Sales")

plt.tight_layout()

plt.savefig(PLOT_DIR / "weekday_sales.png")
plt.close()

# =====================================
# 5. STORE-WISE SALES
# =====================================

store_sales = (
    df.groupby("store_nbr")["sales"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 5))

store_sales.plot(kind="bar")

plt.title("Total Sales by Store")
plt.xlabel("Store Number")
plt.ylabel("Total Sales")

plt.tight_layout()

plt.savefig(PLOT_DIR / "store_sales.png")
plt.close()

# =====================================
# 6. MONTHLY SALES TREND
# =====================================

df["month"] = df["date"].dt.month

monthly_sales = (
    df.groupby("month")["sales"]
    .mean()
)

plt.figure(figsize=(10, 5))

monthly_sales.plot(kind="line", marker="o")

plt.title("Average Sales by Month")
plt.xlabel("Month")
plt.ylabel("Average Sales")

plt.xticks(range(1, 13))

plt.tight_layout()

plt.savefig(PLOT_DIR / "monthly_sales.png")
plt.close()

# =====================================
# 7. TOP 10 PRODUCT FAMILIES
# =====================================

top_products = family_sales.head(10)

print("\nTop 10 Product Families:")
print(top_products)

print("\nEDA COMPLETED SUCCESSFULLY!")
print("Graphs saved in outputs/plots/")
