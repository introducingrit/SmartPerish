# SmartPerish -- Project Summary

## Overview

**SmartPerish** is a perishable-goods supply-chain decision-support
system that combines demand forecasting, inventory management,
expiry-aware stock allocation, distribution optimization,
carbon-footprint analysis, and local Edge AI inference.

The project uses historical retail sales data to forecast demand,
supports inventory decisions using FEFO (First Expiry, First Out),
recommends replenishment, optimizes delivery allocation, and estimates
transportation-related carbon emissions. A Flask dashboard brings the
generated reports together in one interface.

## Main capabilities

-   **Demand forecasting:** XGBoost predicts product-family sales using
    historical sales, calendar, promotion, lag, and rolling-average
    features.
-   **Inventory management:** Simulated inventory batches are tracked by
    store, product family, quantity, and expiry date.
-   **FEFO allocation:** Available stock is allocated from the
    earliest-expiring batches first.
-   **Replenishment planning:** Reorder recommendations are generated
    using demand, lead time, safety stock, and stock levels.
-   **Distribution optimization:** Delivery quantities and vehicle
    requirements are optimized subject to the implemented constraints.
-   **Carbon analytics:** Transportation emissions and carbon-related
    costs are estimated and compared.
-   **Edge AI:** The trained XGBoost model is loaded locally for
    inference and benchmarked on the laptop.
-   **Dashboard:** A Flask backend serves forecast, inventory,
    distribution, and carbon reports to a plain HTML/CSS/JavaScript
    frontend.

## Verified results

-   XGBoost validation WAPE: **12.70%**
-   Seasonal-naive baseline WAPE: **21.46%**
-   Local inference test: **100 records**, approximately **3.36 ms**
    reported inference time
-   Edge benchmark mean latency: **3.2815 ms**
-   Edge benchmark throughput: approximately **30,473.91
    records/second**
-   Dashboard automated tests: **9 passed, 0 failed**

## Dataset

The forecasting pipeline uses the Kaggle **Store Sales -- Time Series
Forecasting** dataset. Inventory batches and operational scenarios are
simulated for demonstrating inventory, replenishment, distribution, and
carbon-optimization workflows.

## Implementation note

The current Edge AI implementation uses local XGBoost inference. ONNX
conversion was attempted but did not become the deployed inference path.

## Purpose

SmartPerish demonstrates how machine learning and optimization
techniques can support more informed decisions in perishable-goods
supply chains, with attention to demand, stock availability, expiry,
delivery efficiency, and emissions.
