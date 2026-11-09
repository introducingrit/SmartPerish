
from pathlib import Path
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Load inventory after FEFO allocation
inventory = pd.read_csv(DATA_DIR / "inventory_after_fefo.csv")

# Load replenishment and FEFO reports
replenishment = pd.read_csv(
    REPORT_DIR / "replenishment_recommendations.csv"
)
allocations = pd.read_csv(REPORT_DIR / "fefo_allocations.csv")
demand = pd.read_csv(REPORT_DIR / "fefo_demand_summary.csv")

# Load forecast to establish reference date
forecast = pd.read_csv(REPORT_DIR / "forecast_daily_summary.csv")
today = pd.to_datetime(forecast["date"]).max()

inventory["expiry_date"] = pd.to_datetime(inventory["expiry_date"])

print("\nSMARTPERISH - INVENTORY EXPIRY ANALYSIS")
print("=" * 50)
print("Reference date:", today.date())

# Calculate days remaining until expiry
inventory["days_to_expiry"] = (
    inventory["expiry_date"] - today
).dt.days

# Only batches with remaining stock need alerts
remaining_stock = inventory[
    inventory["quantity_units"] > 0
].copy()

# Identify expired, critical and warning batches
remaining_stock["expiry_status"] = "SAFE"

remaining_stock.loc[
    remaining_stock["days_to_expiry"] < 0,
    "expiry_status"
] = "EXPIRED"

remaining_stock.loc[
    (remaining_stock["days_to_expiry"] >= 0) &
    (remaining_stock["days_to_expiry"] <= 3),
    "expiry_status"
] = "CRITICAL"

remaining_stock.loc[
    (remaining_stock["days_to_expiry"] > 3) &
    (remaining_stock["days_to_expiry"] <= 7),
    "expiry_status"
] = "WARNING"

# Keep only batches requiring attention
expiry_alerts = remaining_stock[
    remaining_stock["expiry_status"].isin(
        ["EXPIRED", "CRITICAL", "WARNING"]
    )
].copy()

# Prepare expiry alert report
expiry_alerts["expiry_date"] = (
    expiry_alerts["expiry_date"].dt.strftime("%Y-%m-%d")
)

expiry_alerts = expiry_alerts[
    [
        "batch_id",
        "store_nbr",
        "family",
        "quantity_units",
        "expiry_date",
        "expiry_status"
    ]
].sort_values(
    by=["expiry_date", "store_nbr", "family"]
)

expiry_alerts.to_csv(
    REPORT_DIR / "expiry_alerts.csv",
    index=False
)

# Basic inventory metrics
total_batches = len(inventory)

total_stock = int(
    inventory["quantity_units"].clip(lower=0).sum()
)

# Expiry metrics
days = inventory["days_to_expiry"]
positive_stock = inventory["quantity_units"] > 0

expired_stock = int(
    inventory.loc[
        (days < 0) & positive_stock,
        "quantity_units"
    ].clip(lower=0).sum()
)

critical_batches = int(
    (
        (days >= 0) &
        (days <= 3) &
        positive_stock
    ).sum()
)

warning_batches = int(
    (
        (days > 3) &
        (days <= 7) &
        positive_stock
    ).sum()
)

# FEFO metrics
total_requested = int(demand["requested_units"].sum())
total_fulfilled = int(demand["fulfilled_units"].sum())
total_unfulfilled = int(demand["unfulfilled_units"].sum())

fulfilment_rate = (
    total_fulfilled / total_requested * 100
    if total_requested > 0 else 0
)

# Replenishment metrics
reorder_items = int(
    (replenishment["status"] == "REORDER REQUIRED").sum()
)

total_reorder_quantity = int(
    replenishment["recommended_order_quantity"].sum()
)

# Store-wise stock summary
store_summary = inventory.groupby("store_nbr")[
    "quantity_units"
].sum().reset_index()

store_summary.to_csv(
    REPORT_DIR / "inventory_store_summary.csv",
    index=False
)

# Product-family stock summary
family_summary = inventory.groupby("family")[
    "quantity_units"
].sum().reset_index()

family_summary.to_csv(
    REPORT_DIR / "inventory_family_summary.csv",
    index=False
)

# Overall dashboard metrics
summary = {
    "reference_date": str(today.date()),
    "total_batches": total_batches,
    "total_stock_units": total_stock,
    "expired_stock_units": expired_stock,
    "critical_expiry_batches": critical_batches,
    "warning_expiry_batches": warning_batches,
    "total_requested_units": total_requested,
    "total_fulfilled_units": total_fulfilled,
    "total_unfulfilled_units": total_unfulfilled,
    "fulfilment_rate_percent": round(fulfilment_rate, 2),
    "items_requiring_reorder": reorder_items,
    "total_recommended_reorder_units": total_reorder_quantity
}

with open(
    REPORT_DIR / "inventory_dashboard_summary.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(summary, file, indent=4)

# Display results
print("\nEXPIRY ALERT SUMMARY")
print("-" * 40)
print("Expired batches:", (expiry_alerts["expiry_status"] == "EXPIRED").sum())
print("Critical batches:", critical_batches)
print("Warning batches:", warning_batches)
print("Total alert records:", len(expiry_alerts))

print("\nSMARTPERISH - INVENTORY DASHBOARD SUMMARY")
print("=" * 50)

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nGenerated files:")
print("- outputs/reports/expiry_alerts.csv")
print("- outputs/reports/inventory_dashboard_summary.json")
print("- outputs/reports/inventory_store_summary.csv")
print("- outputs/reports/inventory_family_summary.csv")

print("\nINVENTORY SUMMARY COMPLETED!")
