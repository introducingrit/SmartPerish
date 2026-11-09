
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_PATH = BASE_DIR / "data" / "processed" / "train_features.parquet"
FORECAST_PATH = BASE_DIR / "outputs" / "reports" / "forecast_daily_summary.csv"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - INVENTORY DATA GENERATION")
print("=" * 45)

# Use the forecast's final date as the demo date reference
forecast = pd.read_csv(FORECAST_PATH)
forecast["date"] = pd.to_datetime(forecast["date"])
reference_date = forecast["date"].max()

# Get actual store and product-family identifiers
features = pd.read_parquet(FEATURE_PATH)

stores = sorted(features["store_nbr"].unique())[:3]
families = sorted(features["family"].unique())[:5]

rng = np.random.default_rng(42)

suppliers = [
    "FreshFoods Supplier",
    "GreenHarvest Ltd",
    "DailySupply Co"
]

records = []

for store in stores:
    for family in families:

        # Create two separate inventory batches
        for batch_number in range(1, 3):

            received_offset = rng.integers(1, 10)
            shelf_life = rng.integers(5, 31)

            received_date = (
                reference_date - pd.Timedelta(days=int(received_offset))
            )

            expiry_date = (
                reference_date + pd.Timedelta(days=int(shelf_life))
            )

            records.append({
                "store_nbr": int(store),
                "family": family,
                "batch_id": f"S{store}_{batch_number}_{len(records)+1}",
                "quantity_units": int(rng.integers(20, 151)),
                "received_date": received_date.date(),
                "expiry_date": expiry_date.date(),
                "supplier": suppliers[int(rng.integers(0, len(suppliers)))],
                "lead_time_days": int(rng.integers(2, 8)),
                "reorder_level": int(rng.integers(30, 61)),
                "unit_cost": round(float(rng.uniform(10, 100)), 2)
            })

inventory = pd.DataFrame(records)

output_path = OUTPUT_DIR / "inventory_batches.csv"
inventory.to_csv(output_path, index=False)

print("Reference date:", reference_date.date())
print("Stores:", len(stores))
print("Product families:", len(families))
print("Inventory batches:", len(inventory))

print("\nSample inventory records:")
print(inventory.head(10).to_string(index=False))

print("\nSaved:", output_path)
print("\nSTEP 3.1 COMPLETED!")
