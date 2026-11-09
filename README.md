
# SmartPerish
### Perishable Goods Supply Chain Demand Forecaster with Edge-AI Carbon Footprint Optimization

SmartPerish is an intelligent supply-chain decision-support system that combines machine learning, inventory management, distribution optimization, and carbon-footprint analysis to improve the management of perishable goods.

It forecasts product demand, supports expiry-aware inventory allocation, recommends replenishment, optimizes distribution, and performs local Edge AI inference.

## Key Features

- **Demand Forecasting:** XGBoost-based demand prediction using historical sales, promotions, calendar features, lag values, and rolling averages.
- **Inventory Management:** Tracks simulated inventory batches, stock quantities, and expiry dates.
- **FEFO Allocation:** Uses First Expiry, First Out to allocate stock from batches expiring earliest.
- **Replenishment Planning:** Generates reorder recommendations based on stock and demand-planning inputs.
- **Distribution Optimization:** Optimizes delivery quantities and vehicle requirements.
- **Carbon Analytics:** Estimates transportation emissions and carbon-related costs.
- **Edge AI:** Runs local inference using the trained XGBoost model.
- **Interactive Dashboard:** Displays forecasting, inventory, distribution, and carbon analytics through a Flask-powered web interface.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python, HTML, CSS, JavaScript |
| Backend | Flask |
| Machine Learning | XGBoost, scikit-learn |
| Data Processing | pandas, NumPy |
| Optimization | PuLP |
| Visualization | Matplotlib, Seaborn, Chart.js |
| Data Formats | CSV, JSON, Parquet |
| Environment | Windows 11, VS Code |

## Project Architecture

```text
Historical Sales Dataset
          |
          v
Data Preprocessing
          |
          v
Feature Engineering
          |
          v
XGBoost Demand Forecasting
          |
          +----------------------+
          |                      |
          v                      v
Inventory and FEFO        Demand Forecast
          |                      |
          v                      v
Replenishment Planning    Distribution Optimization
                                 |
                                 v
                         Carbon Analysis

Saved XGBoost Model
          |
          v
Local Edge AI Inference

Generated Reports
          |
          v
Flask Backend APIs
          |
          v
HTML / CSS / JavaScript Dashboard
```

## Dataset

The forecasting model uses the Kaggle competition dataset:

**Store Sales – Time Series Forecasting**

Dataset:
https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data

The repository does not include the raw dataset or large processed training files. Download them separately before running the complete data pipeline.

Inventory and operational scenarios are simulated demonstration data.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartPerish.git
cd SmartPerish
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate on Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download the dataset

Download the competition files from Kaggle and extract the required CSV files into:

```text
data/raw/
```

Required files include:

- train.csv
- test.csv
- stores.csv
- oil.csv
- holidays_events.csv
- transactions.csv
- sample_submission.csv

You can use Kaggle CLI after configuring your own Kaggle credentials.

Do not upload Kaggle API tokens or credential files to GitHub.

## Running the Data Pipeline

Run the scripts from the project root in the following order:

```powershell
python .\scripts\preprocess.py
python .\scripts\eda.py
python .\scripts\feature_engineering.py
python .\scripts\baseline_evaluation.py
python .\scripts\train_xgboost.py
python .\scripts\forecast_next_7_days.py
```

Inventory, distribution, carbon, and Edge AI scripts are also available in the `scripts/` directory. Refer to the project documentation for their workflow and generated outputs.

## Running the Dashboard

After the required reports are available:

```powershell
python .\webapp\app.py
```

Open:

http://127.0.0.1:5000

## Model Performance

The following results were obtained during the project's chronological validation:

| Model | WAPE |
|---|---:|
| Naive (Lag 1) | 24.13% |
| Seasonal Naive (Lag 7) | 21.46% |
| XGBoost | **12.70%** |

XGBoost achieved a substantially lower WAPE than the seasonal-naive baseline.

## Edge AI Benchmark

| Metric | Result |
|---|---:|
| Test records per run | 100 |
| Mean latency | 3.2815 ms |
| Median latency | 3.2673 ms |
| P95 latency | 3.4753 ms |
| Throughput | 30,473.91 records/sec |
| Model size | 6.71 MB |

The current Edge AI implementation uses local XGBoost inference. ONNX conversion was explored but is not the deployed inference path.

## Dashboard Testing

The automated Flask dashboard test suite completed successfully:

- Total tests: 9
- Passed: 9
- Failed: 0

## Project Documentation

Additional documentation is available in:

- `projectsummary.md` – Project overview
- `goal.md` – Project goal and workflow
- `filestructure.md` – Directory structure
- `techstack.md` – Technologies and tools

## Limitations

- Inventory batches and operational scenarios are simulated.
- Forecasting depends on the historical dataset and engineered features.
- Carbon emissions are estimates based on the model's configured assumptions.
- Local Edge AI inference is implemented using XGBoost; ONNX deployment is not currently implemented.
- The project is a prototype and is not connected to live warehouse or transport systems.

## Future Scope

- Integration with real-time inventory and warehouse systems.
- Live demand updates and automated replenishment.
- Real-world transport and vehicle data integration.
- Deployment of a lightweight edge model on dedicated hardware.
- Improved expiry prediction and waste-reduction analytics.

## License

Add a suitable open-source license before distributing the project. Until then, all rights are reserved by the project owner.
