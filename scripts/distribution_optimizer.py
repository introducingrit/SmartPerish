
from pathlib import Path
import pandas as pd
import pulp

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("\nSMARTPERISH - DISTRIBUTION OPTIMIZATION")
print("=" * 55)

# Load distribution data
demand_df = pd.read_csv(DATA_DIR / "distribution_demand.csv")
distance_df = pd.read_csv(DATA_DIR / "distribution_distances.csv")

if demand_df.empty:
    raise ValueError("No store demand found.")

# Convert input data into dictionaries
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
    raise ValueError("Missing distance information for one or more stores.")

# Demo warehouse and vehicle assumptions
total_demand = sum(demand.values())

warehouse_stock = int(total_demand * 0.80)
vehicle_capacity = 100

transport_cost_per_unit_km = 2.0
vehicle_fixed_cost_per_km = 10.0
shortage_penalty = 1000.0

print("Total store demand:", total_demand)
print("Available warehouse stock:", warehouse_stock)
print("Vehicle capacity:", vehicle_capacity)

# Create optimization problem
problem = pulp.LpProblem(
    "SmartPerish_Distribution",
    pulp.LpMinimize
)
# Decision variables
delivered = pulp.LpVariable.dicts(
    "Delivered_Units",
    stores,
    lowBound=0,
    cat="Integer"
)

unmet = pulp.LpVariable.dicts(
    "Unmet_Demand",
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

# Objective: transport cost + penalty for unmet demand
transport_cost = pulp.lpSum(
    delivered[s] * distance[s] * transport_cost_per_unit_km
    + vehicles[s] * distance[s] * vehicle_fixed_cost_per_km
    for s in stores
)

shortage_cost = pulp.lpSum(
    unmet[s] * shortage_penalty
    for s in stores
)

problem += transport_cost + shortage_cost

# Constraint 1: Fulfilled + unmet demand = total demand
for s in stores:
    problem += delivered[s] + unmet[s] == demand[s]

# Constraint 2: Total deliveries cannot exceed warehouse stock
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
    raise RuntimeError(
        f"Optimization did not find an optimal solution: {status}"
    )

# Extract results
results = []

for s in stores:

    delivered_units = int(round(pulp.value(delivered[s])))
    unmet_units = int(round(pulp.value(unmet[s])))
    vehicle_count = int(round(pulp.value(vehicles[s])))

    results.append({
        "store": s,
        "required_units": demand[s],
        "delivered_units": delivered_units,
        "unmet_units": unmet_units,
        "distance_km": distance[s],
        "vehicles_required": vehicle_count,
        "transport_cost": round(
            delivered_units * distance[s] * transport_cost_per_unit_km
            + vehicle_count * distance[s] * vehicle_fixed_cost_per_km,
            2
        )
    })

result_df = pd.DataFrame(results)

# Save results
output_path = REPORT_DIR / "optimized_distribution.csv"
result_df.to_csv(output_path, index=False)

total_delivered = result_df["delivered_units"].sum()
total_unmet = result_df["unmet_units"].sum()
total_vehicles = result_df["vehicles_required"].sum()
total_cost = result_df["transport_cost"].sum()

print("\nOPTIMIZED DISTRIBUTION PLAN")
print(result_df.to_string(index=False))

print("\nSUMMARY")
print("Warehouse stock:", warehouse_stock)
print("Total delivered:", total_delivered)
print("Total unmet demand:", total_unmet)
print("Vehicles required:", total_vehicles)
print("Transportation cost:", round(total_cost, 2))

print("\nSaved:", output_path)
print("\nSTEP 4.3 COMPLETED!")
