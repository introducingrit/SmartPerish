
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Demo distribution network
# Distances are illustrative, not real road distances.

locations = pd.DataFrame([
    {
        "location": "WAREHOUSE",
        "location_type": "warehouse",
        "latitude": 22.5726,
        "longitude": 88.3639
    },
    {
        "location": "STORE_1",
        "location_type": "store",
        "latitude": 22.5740,
        "longitude": 88.4100
    },
    {
        "location": "STORE_2",
        "location_type": "store",
        "latitude": 22.5350,
        "longitude": 88.3500
    },
    {
        "location": "STORE_3",
        "location_type": "store",
        "latitude": 22.6100,
        "longitude": 88.3900
    }
])

locations.to_csv(
    DATA_DIR / "distribution_locations.csv",
    index=False
)

# Illustrative one-way warehouse-to-store distances
distances = pd.DataFrame([
    {"warehouse": "WAREHOUSE", "store": "STORE_1", "distance_km": 6},
    {"warehouse": "WAREHOUSE", "store": "STORE_2", "distance_km": 5},
    {"warehouse": "WAREHOUSE", "store": "STORE_3", "distance_km": 7}
])

distances.to_csv(
    DATA_DIR / "distribution_distances.csv",
    index=False
)

# Obtain store-level replenishment quantities
replenishment = pd.read_csv(
    REPORT_DIR / "replenishment_recommendations.csv"
)

store_demand = (
    replenishment.groupby("store_nbr")[
        "recommended_order_quantity"
    ].sum().reset_index()
)

store_demand["store"] = (
    "STORE_" + store_demand["store_nbr"].astype(str)
)

store_demand.rename(
    columns={
        "recommended_order_quantity": "required_units"
    },
    inplace=True
)

store_demand = store_demand[
    ["store", "required_units"]
]

store_demand.to_csv(
    DATA_DIR / "distribution_demand.csv",
    index=False
)

print("\nSMARTPERISH - DISTRIBUTION DATA")
print("=" * 45)

print("\nLocations:")
print(locations.to_string(index=False))

print("\nWarehouse distances:")
print(distances.to_string(index=False))

print("\nStore demand:")
print(store_demand.to_string(index=False))

print("\nGenerated files:")
print("- data/processed/distribution_locations.csv")
print("- data/processed/distribution_distances.csv")
print("- data/processed/distribution_demand.csv")

print("\nSTEP 4.1 COMPLETED!")
