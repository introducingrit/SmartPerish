# SmartPerish -- Technology Stack

## Languages

  -----------------------------------------------------------------------
  Technology                          Role
  ----------------------------------- -----------------------------------
  Python                              Data processing, machine learning,
                                      optimization, Edge AI, and Flask
                                      backend

  HTML                                Dashboard page structure

  CSS                                 Dashboard layout, styling, and
                                      responsive presentation

  JavaScript                          Dashboard interactions, API
                                      requests, tables, and charts

  PowerShell                          Windows terminal commands and
                                      project execution
  -----------------------------------------------------------------------

## Python libraries and frameworks

  -----------------------------------------------------------------------
  Technology                          Role in SmartPerish
  ----------------------------------- -----------------------------------
  Flask                               Serves the dashboard and JSON API
                                      endpoints

  pandas                              Loads, cleans, transforms,
                                      aggregates, and exports tabular
                                      data

  NumPy                               Numerical operations and
                                      reproducible simulated-data
                                      generation

  scikit-learn                        Machine-learning utilities and
                                      evaluation support used in the
                                      project environment

  XGBoost                             Demand-forecasting model

  Matplotlib                          Exploratory data-analysis plots

  Seaborn                             Statistical data visualization

  PyArrow                             Parquet data-file support

  PuLP                                Linear/integer optimization support
                                      for distribution planning, where
                                      used by the optimizer
  -----------------------------------------------------------------------

## Frontend libraries

  -----------------------------------------------------------------------
  Technology                          Role
  ----------------------------------- -----------------------------------
  Chart.js                            Renders dashboard charts

  HTML/CSS/JavaScript                 Builds the browser-based dashboard
                                      without React
  -----------------------------------------------------------------------

## Edge AI

-   **Runtime approach:** Local Python inference using the saved XGBoost
    model.
-   **Model artifact:** `ml/saved_models/xgboost_demand_model.json`.
-   **Measurements:** Inference latency, median latency, p95 latency,
    throughput, and model size are recorded by the benchmark script.
-   **Implementation status:** ONNX conversion was tested but was not
    adopted as the working inference path. Do not describe the current
    system as running ONNX Runtime inference.

## Data source and formats

-   **Primary forecasting dataset:** Kaggle Store Sales -- Time Series
    Forecasting.
-   **CSV:** Raw data, reports, predictions, inventory, replenishment,
    and distribution outputs.
-   **Parquet:** Cleaned and feature-engineered datasets.
-   **JSON:** Model, data-quality, inventory, carbon, and Edge AI
    summary reports.

## Development environment

  Component             Environment
  --------------------- --------------------------
  Operating system      Windows 11
  Editor                Visual Studio Code
  Terminal              PowerShell
  Python environment    Project-local `venv`
  Backend               Flask development server
  Local dashboard URL   `http://127.0.0.1:5000`

## Architecture summary

``` text
CSV / Parquet data
       |
       v
Python data pipeline
       |
       +--> pandas / NumPy
       |
       v
XGBoost forecasting model
       |
       +--> Local Python inference
       |
       v
Inventory, optimization, and carbon scripts
       |
       v
CSV / JSON reports
       |
       v
Flask backend APIs
       |
       v
HTML + CSS + JavaScript + Chart.js
```

## Reproducibility note

The exact package versions should be taken from the project's installed
environment or pinned `requirements.txt`. This document lists the
technologies used or identified in the project; it does not assert
unverified version numbers.
