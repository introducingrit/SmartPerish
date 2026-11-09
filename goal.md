# SmartPerish -- Goal and Working

## Goal

The goal of SmartPerish is to develop an integrated decision-support
system for perishable-goods supply chains. It aims to forecast demand,
reduce avoidable inventory waste, plan replenishment, optimize
distribution, and estimate transportation-related carbon emissions.

## Problem addressed

Perishable-goods supply chains must balance product availability with
limited shelf life. Poor demand estimates can contribute to overstocking
or shortages. Inefficient stock allocation and delivery planning can
also increase operating costs and transportation emissions.

SmartPerish brings these decision areas into one workflow.

## How the system works

1.  **Data collection**
    -   Historical sales and supporting store, oil, holiday, and
        transaction data are collected from the Store Sales dataset.
    -   Inventory batches are generated as simulated operational data
        for the selected stores and product families.
2.  **Data preprocessing**
    -   The training and supporting datasets are checked, cleaned, and
        saved in processed formats.
    -   Data-quality information is recorded in a report.
3.  **Demand forecasting**
    -   Calendar, promotion, lag, and rolling-average features are
        prepared.
    -   A seasonal-naive baseline is evaluated.
    -   An XGBoost model is trained and evaluated using a chronological
        validation period.
    -   The forecasting pipeline generates a seven-day forecast.
4.  **Inventory and FEFO**
    -   Inventory is represented as batches with quantities and expiry
        dates.
    -   FEFO allocation fulfils simulated demand using the
        earliest-expiring available stock first.
    -   Remaining stock is analyzed for expiry risk.
5.  **Replenishment**
    -   Replenishment recommendations are generated using stock and
        demand-planning inputs, including lead time and safety stock.
6.  **Distribution and carbon analysis**
    -   Distribution planning determines delivery quantities and vehicle
        requirements under the implemented optimization model.
    -   Carbon calculations estimate emissions and related costs for the
        modeled transportation scenarios.
7.  **Local Edge AI**
    -   The saved XGBoost model is loaded on the local machine.
    -   Predictions are generated locally and inference latency and
        throughput are benchmarked.
8.  **Dashboard**
    -   Flask exposes APIs for overview, forecast, inventory,
        distribution, and carbon information.
    -   HTML, CSS, JavaScript, and Chart.js present the information in a
        browser dashboard.

## Overall workflow

``` text
Historical sales data
        |
        v
Preprocessing and feature engineering
        |
        v
Demand forecasting (XGBoost)
        |
        +----------------------+
        |                      |
        v                      v
Inventory and FEFO       Seven-day forecast
        |                      |
        v                      v
Replenishment planning   Distribution optimization
                               |
                               v
                       Carbon-footprint analysis

Saved XGBoost model --> Local Edge AI inference

Generated reports and model outputs
                |
                v
          Flask APIs
                |
                v
       Web dashboard
```

## Scope and assumptions

-   Historical sales forecasting is based on the Kaggle Store Sales
    dataset.
-   The inventory batches and operational scenarios are simulated
    demonstration data; they are not live warehouse feeds.
-   The current Edge AI path is local XGBoost inference. ONNX conversion
    was explored but is not the deployed inference implementation.
-   Carbon results are estimates based on the parameters and assumptions
    in the project's carbon model.
