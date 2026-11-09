
from pathlib import Path
import pandas as pd
import numpy as np
import json
import math

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - CARBON FOOTPRINT CALCULATOR")
print("=" * 55)

# Load distribution data
demand_df = pd.read_csv(
    DATA_DIR / "distribution_demand.csv"
)

distance_df = pd.read_csv(
    DATA_DIR / "distribution_distances.csv"
)

optimized_df = pd.read_csv(
    REPORT_DIR / "optimized_distribution.csv"
)

# Demo assumptions
VEHICLE_CAPACITY = 100

# Illustrative emission factor for a delivery vehicle.
# This is a project assumption, not measured fleet data.
EMISSION_FACTOR = 0.27  # kg CO2e per vehicle-km

print("Vehicle capacity:", VEHICLE_CAPACITY)
print("Emission factor:", EMISSION_FACTOR, "kg CO2e/km")
print("Trip assumption: warehouse to store and return")

# Get total available warehouse stock
total_demand = int(demand_df["required_units"].sum())
warehouse_stock = int(total_demand * 0.80)

# Calculate baseline proportional allocation
baseline = demand_df.copy()

baseline["exact_allocation"] = (
    baseline["required_units"] / total_demand
) * warehouse_stock

baseline["delivered_units"] = np.floor(
    baseline["exact_allocation"]
).astype(int)

# Distribute any remaining units using largest remainders
remaining_units = (
    warehouse_stock - baseline["delivered_units"].sum()
)

baseline["fraction"] = (
    baseline["exact_allocation"] -
    baseline["delivered_units"]
)

for index in baseline.sort_values(
    "fraction", ascending=False
).index[:remaining_units]:

    baseline.loc[index, "delivered_units"] += 1

baseline["unmet_units"] = (
    baseline["required_units"] -
    baseline["delivered_units"]
)

# Calculate emissions for both approaches
distance_map = dict(zip(
    distance_df["store"],
    distance_df["distance_km"]
))

def calculate_emissions(df, method):

    results = []

    for _, row in df.iterrows():

        store = row["store"]
        delivered = int(row["delivered_units"])

        distance = float(distance_map[store])

        vehicles = math.ceil(
            delivered / VEHICLE_CAPACITY
        ) if delivered > 0 else 0

        # Round trip distance for each vehicle
        total_vehicle_km = vehicles * distance * 2

        emissions = (
            total_vehicle_km * EMISSION_FACTOR
        )

        results.append({
            "method": method,
            "store": store,
            "delivered_units": delivered,
            "vehicles_required": vehicles,
            "one_way_distance_km": distance,
            "total_vehicle_km": total_vehicle_km,
            "emissions_kg_co2e": round(emissions, 3)
        })

    return pd.DataFrame(results)

# Optimized distribution
optimized_emissions = calculate_emissions(
    optimized_df,
    "Optimized"
)

# Baseline proportional distribution
baseline_emissions = calculate_emissions(
    baseline,
    "Baseline"
)

# Combine results
comparison = pd.concat(
    [baseline_emissions, optimized_emissions],
    ignore_index=True
)

comparison.to_csv(
    REPORT_DIR / "distribution_emissions_detail.csv",
    index=False
)

baseline_total = baseline_emissions[
    "emissions_kg_co2e"
].sum()

optimized_total = optimized_emissions[
    "emissions_kg_co2e"
].sum()

difference = baseline_total - optimized_total

percentage_reduction = (
    difference / baseline_total * 100
    if baseline_total > 0 else 0
)

# Save summary
summary = {
    "warehouse_stock_units": warehouse_stock,
    "vehicle_capacity_units": VEHICLE_CAPACITY,
    "emission_factor_kg_co2e_per_km": EMISSION_FACTOR,
    "trip_type": "Round trip",
    "baseline_emissions_kg_co2e": round(
        baseline_total, 3
    ),
    "optimized_emissions_kg_co2e": round(
        optimized_total, 3
    ),
    "emission_difference_kg_co2e": round(
        difference, 3
    ),
    "percentage_emission_reduction": round(
        percentage_reduction, 2
    )
}

with open(
    REPORT_DIR / "carbon_footprint_summary.json",
    "w"
) as file:
    json.dump(summary, file, indent=4)

# Display results
print("\nBASELINE EMISSIONS")
print(baseline_emissions.to_string(index=False))

print("\nOPTIMIZED EMISSIONS")
print(optimized_emissions.to_string(index=False))

print("\nCARBON COMPARISON")
print("Baseline emissions:", round(baseline_total, 3), "kg CO2e")
print("Optimized emissions:", round(optimized_total, 3), "kg CO2e")
print("Emission difference:", round(difference, 3), "kg CO2e")
print("Percentage reduction:", round(percentage_reduction, 2), "%")

if difference > 0:
    print("\nOptimized distribution has lower emissions.")
elif difference < 0:
    print("\nOptimized distribution has higher emissions.")
else:
    print("\nBoth approaches have equal emissions.")

print("\nGenerated files:")
print("- outputs/reports/distribution_emissions_detail.csv")
print("- outputs/reports/carbon_footprint_summary.json")

print("\nSTEP 4.4 COMPLETED!")
