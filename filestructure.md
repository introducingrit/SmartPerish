# SmartPerish -- File Structure

This document describes the project structure and the purpose of the
main files confirmed during implementation. It is a functional overview,
not a claim that every generated or environment-specific file is listed.

``` text
SmartPerish/
|
|-- venv/                         Python virtual environment
|
|-- data/
|   |-- raw/                      Original Kaggle CSV files and archive
|   |-- processed/                Cleaned datasets, features, inventory data
|   |-- external/                 Reserved for external datasets
|
|-- scripts/
|   |-- preprocess.py             Data cleaning and quality checks
|   |-- eda.py                    Exploratory data analysis and plots
|   |-- feature_engineering.py    Calendar, lag, and rolling features
|   |-- baseline_evaluation.py    Naive baseline evaluation
|   |-- train_xgboost.py          XGBoost model training
|   |-- forecast_next_7_days.py   Seven-day demand forecasting
|   |-- evaluate_model.py         Model evaluation support
|   |-- create_inventory_demo.py  Simulated inventory data generation
|   |-- fefo_allocation.py        FEFO stock allocation
|   |-- inventory_planning.py     Replenishment planning
|   |-- inventory_summary.py      Inventory and expiry summary reports
|   |-- create_distribution_data.py
|   |                              Distribution input data generation
|   |-- distribution_optimizer.py Distribution optimization
|   |-- carbon_footprint.py       Carbon-footprint calculations
|   |-- carbon_aware_optimizer.py Carbon-aware distribution optimization
|   |-- edge_inference.py         Local XGBoost inference
|   |-- edge_benchmark.py         Edge inference benchmarking
|   |-- test_onnx_conversion.py   ONNX conversion experiment/testing
|   |-- test_dashboard.py         Flask dashboard endpoint and asset tests
|   |-- validate_project_outputs.py
|   |                              Generated-report validation
|
|-- ml/
|   |-- saved_models/
|       |-- xgboost_demand_model.json
|                                  Saved XGBoost model
|
|-- outputs/
|   |-- plots/                    EDA charts
|   |-- reports/                  Forecast, inventory, distribution,
|   |                              carbon, and Edge AI reports
|
|-- webapp/
|   |-- app.py                    Flask application and API routes
|   |-- templates/
|   |   |-- index.html            Dashboard page
|   |-- static/
|       |-- css/
|       |   |-- style.css         Dashboard styling
|       |-- js/
|           |-- dashboard.js      Dashboard data loading, charts,
|                                  navigation, and refresh behavior
|
|-- database/                     Reserved for database-related files
|-- requirements.txt              Python dependencies
|-- project_structure.txt         Saved directory-tree output
|
|-- projectsummary.md             Short project overview
|-- goal.md                       Project goal and workflow
|-- filestructure.md              This file
|-- techstack.md                  Technology stack
```

## Important generated outputs

### Forecasting

-   `outputs/reports/data_quality_report.json`
-   `outputs/reports/model_comparison.csv`
-   `outputs/reports/xgboost_report.json`
-   `outputs/reports/forecast_daily_summary.csv`
-   `outputs/reports/forecast_next_7_days.csv`

### Inventory

-   `data/processed/inventory_batches.csv`
-   `data/processed/inventory_after_fefo.csv`
-   `outputs/reports/fefo_allocations.csv`
-   `outputs/reports/fefo_demand_summary.csv`
-   `outputs/reports/expiry_alerts.csv`
-   `outputs/reports/replenishment_recommendations.csv`
-   `outputs/reports/inventory_dashboard_summary.json`

### Distribution and carbon

-   `outputs/reports/optimized_distribution.csv`
-   `outputs/reports/carbon_aware_summary.json`
-   `outputs/reports/carbon_footprint_summary.json`

### Edge AI

-   `outputs/reports/edge_inference_results.csv`
-   `outputs/reports/edge_benchmark_report.json`

## Notes

-   `venv/` contains the local Python environment and should generally
    not be committed to version control.
-   `data/raw/` contains source data; `data/processed/` contains
    generated cleaned or transformed data.
-   `outputs/reports/` contains generated artifacts consumed by the
    Flask dashboard.
-   Some filenames and directory contents may vary if scripts are rerun
    or additional files are added.
