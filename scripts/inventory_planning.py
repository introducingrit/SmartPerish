
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

INVENTORY_PATH = (
    BASE_DIR / "data" / "processed" / "inventory_after_fefo.csv"
)

DEMAND_PATH = (
    BASE_DIR / "outputs" / "reports" / "fefo_demand_summary.csv"
)

FORECAST_PATH = (
    BASE_DIR / "outputs" / "reports" / "forecast_daily_summary.csv"
)

REPORT_DIR = BASE_DIR / "outputs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - INVENTORY PLANNING")
print("=" * 50)

# Load inventory after FEFO allocation
inventory = pd.read_csv(INVENTORY_PATH)
inventory["expiry_date"] = pd.to_datetime(inventory["expiry_date"])

# Use the same reference date as the demo inventory
forecast = pd.read_csv(FORECAST_PATH)
forecast["date"] = pd.to_datetime(forecast["date"])
today = forecast["date"].max()

print("Inventory reference date:", today.date())

# ------------------------------------------------
# PART 1: EXPIRY ALERTS
# ------------------------------------------------

inventory["days_to_expiry"] = (
    inventory["expiry_date"] - today
).dt.days

def expiry_status(days):
    if days < 0:
        return "EXPIRED"
    elif days <= 3:
        return "CRITICAL - EXPIRES WITHIN 3 DAYS"
    elif days <= 7:
        return "WARNING - EXPIRES WITHIN 7 DAYS"
    else:
        return "SAFE"

inventory["expiry_status"] = (
    inventory["days_to_expiry"].apply(expiry_status)
)

# Only batches with stock remaining need an expiry alert
expiry_alerts = inventory[
    inventory["quantity_units"] > 0
].copy()

expiry_alerts = expiry_alerts[
    expiry_alerts["days_to_expiry"] <= 7
].sort_values("expiry_date")

expiry_alerts.to_csv(
    REPORT_DIR / "expiry_alerts.csv",
    index=False
)

# ------------------------------------------------
# PART 2: AUTOMATIC REPLENISHMENT
# ------------------------------------------------

demand = pd.read_csv(DEMAND_PATH)

replenishment_records = []

for _, row in demand.iterrows():

    store = int(row["store_nbr"])
    family = row["family"]

    matching = inventory[
        (inventory["store_nbr"] == store) &
        (inventory["family"] == family)
    ]

    # Exclude expired stock from usable inventory
    usable = matching[
        matching["expiry_date"] >= today
    ]

    current_stock = int(
        usable["quantity_units"].clip(lower=0).sum()
    )

    requested_units = int(row["requested_units"])

    # Demo demand represents a simulated 7-day requirement
    average_daily_demand = requested_units / 7

    lead_time = int(matching["lead_time_days"].max())
    safety_stock = int(matching["reorder_level"].max())

    # Stock needed during supplier lead time plus safety stock
    reorder_point = (
        average_daily_demand * lead_time
    ) + safety_stock

    # Target stock covers lead time and the next 7 days
    target_stock = (
        average_daily_demand * (lead_time + 7)
    ) + safety_stock

    reorder_quantity = max(
        0,
        int(np.ceil(target_stock - current_stock))
    )

    if current_stock <= reorder_point:
        status = "REORDER REQUIRED"
    else:
        status = "STOCK SUFFICIENT"

    replenishment_records.append({
        "store_nbr": store,
        "family": family,
        "current_stock": current_stock,
        "average_daily_demand": round(average_daily_demand, 2),
        "lead_time_days": lead_time,
        "safety_stock": safety_stock,
        "reorder_point": round(reorder_point, 2),
        "recommended_order_quantity": reorder_quantity,
        "status": status
    })

replenishment = pd.DataFrame(replenishment_records)

replenishment.to_csv(
    REPORT_DIR / "replenishment_recommendations.csv",
    index=False
)

# ------------------------------------------------
# DISPLAY RESULTS
# ------------------------------------------------

print("\nEXPIRY ALERT SUMMARY")
print("Expired batches:", (inventory["expiry_status"] == "EXPIRED").sum())
print("Critical batches:", (
    inventory["expiry_status"] ==
    "CRITICAL - EXPIRES WITHIN 3 DAYS"
).sum())
print("Warning batches:", (
    inventory["expiry_status"] ==
    "WARNING - EXPIRES WITHIN 7 DAYS"
).sum())

print("\nEXPIRY ALERT DETAILS")
if expiry_alerts.empty:
    print("No batches expiring within 7 days.")
else:
    print(expiry_alerts[
        ["batch_id", "store_nbr", "family",
         "quantity_units", "expiry_date", "expiry_status"]
    ].to_string(index=False))

print("\nREPLENISHMENT RECOMMENDATIONS")
print(replenishment.to_string(index=False))

print("\nTotal units recommended for reorder:",
      replenishment["recommended_order_quantity"].sum())

print("\nGenerated files:")
print("- outputs/reports/expiry_alerts.csv")
print("- outputs/reports/replenishment_recommendations.csv")

print("\nSTEP 3.3 COMPLETED!")
