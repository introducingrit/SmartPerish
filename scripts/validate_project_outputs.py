
from pathlib import Path
import pandas as pd
import json

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "outputs" / "reports"

print("\nSMARTPERISH - DATA VALIDATION")
print("=" * 60)

# Reports required by the Flask APIs
required_files = [
    "xgboost_report.json",
    "inventory_dashboard_summary.json",
    "carbon_aware_summary.json",
    "carbon_footprint_summary.json",
    "forecast_daily_summary.csv",
    "expiry_alerts.csv",
    "replenishment_recommendations.csv",
    "optimized_distribution.csv"
]

# Required columns for CSV reports
required_columns = {
    "forecast_daily_summary.csv": [
        "date",
        "total_predicted_sales"
    ],
    "expiry_alerts.csv": [
        "batch_id",
        "store_nbr",
        "family",
        "quantity_units",
        "expiry_date",
        "expiry_status"
    ],
    "replenishment_recommendations.csv": [
        "store_nbr",
        "family",
        "current_stock",
        "average_daily_demand",
        "lead_time_days",
        "safety_stock",
        "reorder_point",
        "recommended_order_quantity",
        "status"
    ],
    "optimized_distribution.csv": [
        "store",
        "required_units",
        "delivered_units",
        "unmet_units",
        "distance_km",
        "vehicles_required",
        "transport_cost"
    ]
}

passed = 0
failed = 0

for filename in required_files:

    path = REPORT_DIR / filename

    if not path.exists():
        print(f"\n[MISSING] {filename}")
        failed += 1
        continue

    try:

        if filename.endswith(".json"):

            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")

            print(f"\n[PASSED] {filename}")
            print("  Type: JSON")
            print("  Fields:", list(data.keys()))

        else:

            df = pd.read_csv(path)

            # Validate required columns
            expected = required_columns[filename]
            missing_columns = [
                column for column in expected
                if column not in df.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            # An empty expiry report is valid:
            # FEFO may have consumed all stock near expiry.
            if filename == "expiry_alerts.csv" and df.empty:

                print(f"\n[PASSED] {filename}")
                print("  Rows: 0")
                print("  Status: No remaining batches require expiry alerts")
                print("  Columns:", list(df.columns))

            else:

                if df.empty:
                    raise ValueError("CSV contains no records")

                print(f"\n[PASSED] {filename}")
                print("  Rows:", len(df))
                print("  Columns:", list(df.columns))

        passed += 1

    except Exception as error:

        print(f"\n[FAILED] {filename}")
        print("  Error:", error)
        failed += 1


print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print("Total reports:", len(required_files))
print("Passed:", passed)
print("Failed:", failed)

if failed == 0:
    print("\nALL REQUIRED REPORTS VALIDATED!")
else:
    print("\nSOME REPORTS NEED ATTENTION.")

print("\nSMARTPERISH DATA VALIDATION COMPLETED!")
