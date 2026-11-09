
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

INVENTORY_PATH = (
    BASE_DIR / "data" / "processed" / "inventory_batches.csv"
)

FORECAST_PATH = (
    BASE_DIR / "outputs" / "reports" / "forecast_daily_summary.csv"
)

OUTPUT_DIR = BASE_DIR / "outputs" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - FEFO INVENTORY ALLOCATION")
print("=" * 50)

# Load inventory
inventory = pd.read_csv(INVENTORY_PATH)

inventory["expiry_date"] = pd.to_datetime(inventory["expiry_date"])
inventory["received_date"] = pd.to_datetime(inventory["received_date"])

# Use the same reference date as the inventory demo
forecast = pd.read_csv(FORECAST_PATH)
forecast["date"] = pd.to_datetime(forecast["date"])
today = forecast["date"].max()

print("Inventory reference date:", today.date())

# Generate clearly labelled simulated demand for demonstration
rng = np.random.default_rng(42)

demand_records = []

for (store, family), group in inventory.groupby(
    ["store_nbr", "family"]
):
    demand_records.append({
        "store_nbr": store,
        "family": family,
        "requested_units": int(rng.integers(80, 181))
    })

demand = pd.DataFrame(demand_records)

allocation_records = []
summary_records = []

# Process each store and product family
for _, request in demand.iterrows():

    store = request["store_nbr"]
    family = request["family"]
    requested = int(request["requested_units"])

    remaining = requested
    fulfilled = 0

    matching = inventory[
        (inventory["store_nbr"] == store) &
        (inventory["family"] == family)
    ].copy()

    # Exclude expired and empty batches
    available = matching[
        (matching["expiry_date"] >= today) &
        (matching["quantity_units"] > 0)
    ]

    # FEFO: earliest expiry first
    available = available.sort_values(
        by=["expiry_date", "received_date"]
    )

    for index in available.index:

        if remaining <= 0:
            break

        stock = int(inventory.loc[index, "quantity_units"])
        allocated = min(stock, remaining)

        inventory.loc[index, "quantity_units"] -= allocated

        remaining -= allocated
        fulfilled += allocated

        allocation_records.append({
            "store_nbr": store,
            "family": family,
            "batch_id": inventory.loc[index, "batch_id"],
            "expiry_date": inventory.loc[index, "expiry_date"].date(),
            "allocated_units": allocated,
            "remaining_batch_stock": int(
                inventory.loc[index, "quantity_units"]
            )
        })

    summary_records.append({
        "store_nbr": store,
        "family": family,
        "requested_units": requested,
        "fulfilled_units": fulfilled,
        "unfulfilled_units": remaining,
        "status": "FULFILLED" if remaining == 0 else "STOCK SHORTAGE"
    })

# Save results
allocation_df = pd.DataFrame(allocation_records)
summary_df = pd.DataFrame(summary_records)

inventory["expiry_date"] = inventory["expiry_date"].dt.date
inventory["received_date"] = inventory["received_date"].dt.date

allocation_df.to_csv(
    OUTPUT_DIR / "fefo_allocations.csv",
    index=False
)

summary_df.to_csv(
    OUTPUT_DIR / "fefo_demand_summary.csv",
    index=False
)

inventory.to_csv(
    BASE_DIR / "data" / "processed" / "inventory_after_fefo.csv",
    index=False
)

print("\nFEFO ALLOCATION RESULTS")
print(summary_df.to_string(index=False))

print("\nTotal requested:", summary_df["requested_units"].sum())
print("Total fulfilled:", summary_df["fulfilled_units"].sum())
print("Total unfulfilled:", summary_df["unfulfilled_units"].sum())

print("\nGenerated files:")
print("- outputs/reports/fefo_allocations.csv")
print("- outputs/reports/fefo_demand_summary.csv")
print("- data/processed/inventory_after_fefo.csv")

print("\nSTEP 3.2 COMPLETED!")
