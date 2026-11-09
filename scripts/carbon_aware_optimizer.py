
from pathlib import Path
import pandas as pd
import pulp
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - CARBON AWARE OPTIMIZATION")
print("=" * 55)

# Load data
demand_df = pd.read_csv(DATA_DIR / "distribution_demand.csv")
distance_df = pd.read_csv(DATA_DIR / "distribution_distances.csv")

stores = demand_df["store"].tolist()

demand = dict(zip(
    demand_df["store"],
    demand_df["required_units"].astype(int)
))

distance = dict(zip(
    distance_df["store"],
    distance_df["distance_km"].astype(float)
))

if set(stores) - set(distance):
    raise ValueError("Missing store distance information.")

# Demo assumptions
total_demand = sum(demand.values())
warehouse_stock = int(total_demand * 0.80)

vehicle_capacity = 100

transport_cost_per_unit_km = 2.0
vehicle_fixed_cost_per_km = 10.0
shortage_penalty = 1000.0

emission_factor = 0.27
carbon_price_per_kg = 5.0

print("Total demand:", total_demand)
print("Warehouse stock:", warehouse_stock)
print("Vehicle capacity:", vehicle_capacity)
print("Emission factor:", emission_factor, "kg CO2e/km")
print("Carbon price:", carbon_price_per_kg, "INR/kg CO2e")

# Create optimization problem
problem = pulp.LpProblem(
    "SmartPerish_Carbon_Aware",
    pulp.LpMinimize
)

# Decision variables
delivered = pulp.LpVariable.dicts(
    "Delivered",
    stores,
    lowBound=0,
    cat="Integer"
)

unmet = pulp.LpVariable.dicts(
    "Unmet",
    stores,
    lowBound=0,
    cat="Integer"
)

vehicles = pulp.LpVariable.dicts(
    "Vehicles",
    stores,
    lowBound=0,
    cat="Integer"
)

# Transportation cost (round-trip distance)
transport_cost = pulp.lpSum(
    delivered[s] * distance[s] * 2
    * transport_cost_per_unit_km
    +
    vehicles[s] * distance[s] * 2
    * vehicle_fixed_cost_per_km
    for s in stores
)

# Carbon emissions
carbon_emissions = pulp.lpSum(
    vehicles[s] * distance[s] * 2
    * emission_factor
    for s in stores
)

# Carbon cost
carbon_cost = carbon_emissions * carbon_price_per_kg

# Shortage penalty
shortage_cost = pulp.lpSum(
    unmet[s] * shortage_penalty
    for s in stores
)

# Combined objective - add only once
problem += (
    transport_cost +
    shortage_cost +
    carbon_cost
)

# Constraint 1: Demand satisfaction
for s in stores:
    problem += delivered[s] + unmet[s] == demand[s]

# Constraint 2: Warehouse stock
problem += pulp.lpSum(
    delivered[s] for s in stores
) <= warehouse_stock

# Constraint 3: Vehicle capacity
for s in stores:
    problem += delivered[s] <= vehicle_capacity * vehicles[s]

# Solve
solver = pulp.PULP_CBC_CMD(msg=False)
problem.solve(solver)

status = pulp.LpStatus[problem.status]

print("\nOptimization status:", status)

if status != "Optimal":
    raise RuntimeError("Carbon-aware optimization failed.")

# Extract results
results = []

for s in stores:

    units = int(round(pulp.value(delivered[s])))
    shortage = int(round(pulp.value(unmet[s])))
    vehicle_count = int(round(pulp.value(vehicles[s])))

    vehicle_km = vehicle_count * distance[s] * 2

    emissions = vehicle_km * emission_factor

    store_transport_cost = (
        units * distance[s] * 2 * transport_cost_per_unit_km
        +
        vehicle_count * distance[s] * 2
        * vehicle_fixed_cost_per_km
    )

    store_carbon_cost = emissions * carbon_price_per_kg

    results.append({
        "store": s,
        "required_units": demand[s],
        "delivered_units": units,
        "unmet_units": shortage,
        "vehicles_required": vehicle_count,
        "round_trip_vehicle_km": vehicle_km,
        "transport_cost": round(store_transport_cost, 2),
        "emissions_kg_co2e": round(emissions, 3),
        "carbon_cost": round(store_carbon_cost, 2)
    })

result_df = pd.DataFrame(results)

result_path = (
    REPORT_DIR / "carbon_aware_distribution.csv"
)

result_df.to_csv(result_path, index=False)

# Summary
total_delivered = int(result_df["delivered_units"].sum())
total_unmet = int(result_df["unmet_units"].sum())
total_vehicles = int(result_df["vehicles_required"].sum())

total_transport = result_df["transport_cost"].sum()
total_emissions = result_df["emissions_kg_co2e"].sum()
total_carbon_cost = result_df["carbon_cost"].sum()

summary = {
    "optimization_status": status,
    "warehouse_stock_units": warehouse_stock,
    "total_delivered_units": total_delivered,
    "total_unmet_units": total_unmet,
    "total_vehicles": total_vehicles,
    "transport_cost_inr": round(total_transport, 2),
    "carbon_emissions_kg_co2e": round(total_emissions, 3),
    "carbon_cost_inr": round(total_carbon_cost, 2),
    "combined_objective_value": round(
        pulp.value(problem.objective), 2
    )
}

with open(
    REPORT_DIR / "carbon_aware_summary.json",
    "w"
) as file:
    json.dump(summary, file, indent=4)

print("\nCARBON-AWARE DISTRIBUTION PLAN")
print(result_df.to_string(index=False))

print("\nFINAL SUMMARY")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nGenerated files:")
print("- outputs/reports/carbon_aware_distribution.csv")
print("- outputs/reports/carbon_aware_summary.json")

print("\nSTEP 4.5 COMPLETED!")
