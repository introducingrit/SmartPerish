
from pathlib import Path
import json
import pandas as pd

from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent.parent

REPORT_DIR = BASE_DIR / "outputs" / "reports"

app = Flask(__name__)


# ---------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------

def read_json(filename):
    path = REPORT_DIR / filename

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_csv(filename):
    path = REPORT_DIR / filename

    if not path.exists():
        return None

    df = pd.read_csv(path)

    # Convert missing values into JSON-compatible nulls
    df = df.astype(object).where(pd.notna(df), None)

    return df.to_dict(orient="records")


# ---------------------------------------
# DASHBOARD
# ---------------------------------------

@app.route("/")
def dashboard():
    return render_template("index.html")


# ---------------------------------------
# HEALTH API
# ---------------------------------------

@app.route("/api/health")
def health():

    return jsonify({
        "project": "SmartPerish",
        "status": "running",
        "backend": "Flask",
        "edge_ai": "Local XGBoost"
    })


# ---------------------------------------
# OVERVIEW API
# ---------------------------------------

@app.route("/api/overview")
def overview():

    model_report = read_json("xgboost_report.json")
    inventory = read_json("inventory_dashboard_summary.json")
    carbon = read_json("carbon_aware_summary.json")
    distribution = read_csv("optimized_distribution.csv")

    if any(x is None for x in [
        model_report, inventory, carbon, distribution
    ]):
        return jsonify({
            "error": "One or more project reports are missing."
        }), 404

    return jsonify({
        "forecast_wape": model_report["metrics"]["WAPE"],
        "warehouse_stock": inventory["total_stock_units"],
        "vehicles_required": carbon["total_vehicles"],
        "carbon_emissions": carbon["carbon_emissions_kg_co2e"],
        "total_delivered": carbon["total_delivered_units"],
        "unmet_demand": carbon["total_unmet_units"]
    })


# ---------------------------------------
# FORECAST API
# ---------------------------------------

@app.route("/api/forecast")
def forecast():

    data = read_csv("forecast_daily_summary.csv")

    if data is None:
        return jsonify({"error": "Forecast report not found."}), 404

    return jsonify(data)


# ---------------------------------------
# INVENTORY API
# ---------------------------------------

@app.route("/api/inventory")
def inventory():

    summary = read_json("inventory_dashboard_summary.json")
    expiry = read_csv("expiry_alerts.csv")
    replenishment = read_csv("replenishment_recommendations.csv")

    if any(x is None for x in [summary, expiry, replenishment]):
        return jsonify({
            "error": "Inventory reports are missing."
        }), 404

    return jsonify({
        "summary": summary,
        "expiry_alerts": expiry,
        "replenishment": replenishment
    })


# ---------------------------------------
# DISTRIBUTION API
# ---------------------------------------

@app.route("/api/distribution")
def distribution():

    data = read_csv("optimized_distribution.csv")
    summary = read_json("carbon_aware_summary.json")

    if data is None or summary is None:
        return jsonify({
            "error": "Distribution reports are missing."
        }), 404

    return jsonify({
        "distribution": data,
        "summary": summary
    })


# ---------------------------------------
# CARBON API
# ---------------------------------------

@app.route("/api/carbon")
def carbon():

    data = read_json("carbon_footprint_summary.json")
    optimized = read_json("carbon_aware_summary.json")

    if data is None or optimized is None:
        return jsonify({
            "error": "Carbon reports are missing."
        }), 404

    return jsonify({
        "baseline": data,
        "optimized": optimized
    })


# ---------------------------------------
# START SERVER
# ---------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
