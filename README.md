# GramUrja-AI

AI-powered household energy management and optimization system for forecasting electricity demand, predicting solar generation, and scheduling flexible loads using advanced time-series ML and constrained optimization.

GramUrja-AI is being upgraded from a lightweight hackathon MVP into a multi-model energy intelligence platform that combines forecasting, uncertainty estimation, appliance scheduling, battery/EV optimization, anomaly detection, explainability, and a tool-using AI assistant.

## Demo

[Watch the GramUrja-AI demo](https://drive.google.com/file/d/1cZCKmNuRsAuWd_IpOPWChsjohZtrRUTR/view?usp=sharing)

---

## Overview

GramUrja-AI addresses three connected household energy-management problems:

1. **Forecast demand**  
   Predict electricity consumption for the next 24–48 hours using historical load, weather, calendar, tariff, and household features.

2. **Forecast solar generation**  
   Estimate future solar generation using historical generation, irradiance, weather, and temporal information.

3. **Optimize energy usage**  
   Use forecasts and constraints to determine when flexible appliances, batteries, and EVs should operate while balancing cost, grid demand, and renewable availability.

The system is designed around the principle that forecasting should feed decision-making rather than exist as an isolated ML component.

---

## System Architecture

```text
                                  GRAMURJA-AI
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
  Smart Meter Data                Weather Data                  User / Tariff Data
  Load History                   Temperature                     Appliance Preferences
  Solar Generation               Humidity                        Electricity Prices
  Appliance State                Irradiance                      Operating Constraints
        |                              |                              |
        +------------------------------+------------------------------+
                                       |
                                       v
                              Data & Feature Layer
                                       |
                 +---------------------+---------------------+
                 |                     |                     |
                 v                     v                     v
          Temporal Features      Lag / Rolling        External Features
          Hour / Day / Month     Load / Solar         Weather / Tariff
          Weekend / Holiday      Statistics           Solar Conditions
                 |                     |                     |
                 +---------------------+---------------------+
                                       |
                                       v
                              Forecasting Engine
                                       |
                 +---------------------+---------------------+
                 |                     |                     |
                 v                     v                     v
          XGBoost Baseline       Temporal Fusion       PatchTST /
                                Transformer (TFT)       Foundation Models
                 |                     |                     |
                 +---------------------+---------------------+
                                       |
                                       v
                              Forecast Selection
                         Rolling Time-Series Evaluation
                         MAE / RMSE / MAPE / Coverage
                                       |
                                       v
                           Probabilistic Forecasts
                         P10 / P50 / P90 Intervals
                                       |
                +----------------------+----------------------+
                |                      |                      |
                v                      v                      v
         Demand Forecast        Solar Forecast         Price Forecast
                |                      |                      |
                +----------------------+----------------------+
                                       |
                                       v
                              Decision / Optimizer
                                       |
             +-------------------------+-------------------------+
             |                         |                         |
             v                         v                         v
       Appliance Scheduling      Battery Dispatch          EV Charging
             |                         |                         |
             +-------------------------+-------------------------+
                                       |
                                       v
                              Optimization Objectives
                    +----------------+----------------+
                    |                |                |
                    v                v                v
               Lower Cost      Lower Peak       Lower Carbon
                    |                |                |
                    +----------------+----------------+
                                     |
                                     v
                              Decision Engine
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
             AI Energy Assistant              Dashboard / API
             Tool-based reasoning              Forecasts / Schedules
                    |                                 |
                    +----------------+----------------+
                                     |
                                     v
                                PostgreSQL
```

---

## Core ML Architecture

The forecasting layer is designed as a model-comparison pipeline rather than relying on a single algorithm.

```text
Historical Time Series
        |
        v
Feature Engineering
        |
        +-------------------+
        |                   |
        v                   v
Classical Baselines    Advanced Models
        |                   |
        |          +--------+--------+
        |          |                 |
        v          v                 v
     Naive      TFT / PatchTST   Time-Series
     XGBoost                     Foundation Models
        |          |                 |
        +----------+-----------------+
                   |
                   v
          Rolling Time-Series CV
                   |
                   v
       Model Metrics & Comparison
                   |
                   v
          Selected Forecast Model
                   |
                   v
       Probabilistic Forecast Output
```

### Demand forecasting

The demand model predicts short-term household electricity consumption using:

- historical consumption
- lagged consumption
- rolling statistics
- temperature and weather variables
- hour of day
- day of week
- weekend and holiday indicators
- tariff information
- appliance-level information where available

The initial baseline is XGBoost. Advanced experiments use Transformer-based time-series models such as Temporal Fusion Transformer (TFT) and PatchTST, with time-series foundation models evaluated where the dataset and deployment constraints make them appropriate.

### Solar forecasting

Solar generation forecasting combines:

- historical solar generation
- GHI/DNI/DHI where available
- cloud cover
- temperature
- humidity
- wind conditions
- time of day
- day of year
- solar position features

The forecasting pipeline can compare ML predictions against physics-informed or analytical solar estimates.

### Probabilistic forecasting

Instead of returning a single point estimate, the forecasting layer is designed to support prediction intervals:

```text
                 Forecast
                    |
        +-----------+-----------+
        |           |           |
       P10         P50         P90
     Lower        Median       Upper
    estimate      forecast    estimate
```

This allows the optimizer to account for uncertainty in demand and renewable generation.

---

## Energy Optimization

Forecasts feed a constrained optimization engine rather than a simple rule-based scheduler.

```text
Demand Forecast
       |
Solar Forecast
       |
Tariff Forecast
       |
Battery State
       |
Appliance Constraints
       |
EV Requirements
       |
       v
+---------------------------+
|   Constrained Optimizer   |
|                           |
|  Appliance Scheduling     |
|  Battery Dispatch        |
|  EV Charging              |
|  Peak Management          |
+-------------+-------------+
              |
              v
        Optimal Schedule
```

The optimization objective can balance:

```text
Total Objective
    =
    Energy Cost
    + Peak Demand Penalty
    + Grid Carbon Penalty
    + Battery Degradation Cost
    + Constraint Violations
```

Subject to constraints such as:

- appliance operating windows
- appliance power requirements
- user-defined schedules
- maximum grid import
- battery state-of-charge limits
- battery charge/discharge efficiency
- EV departure and target-SOC requirements
- solar availability
- tariff periods

Potential optimization technologies include OR-Tools, PuLP, or other mixed-integer/constrained optimization solvers.

---

## Key Features

### 1. Multi-horizon demand forecasting

Predict household load for the next 24–48 hours rather than only estimating a single future value.

### 2. Solar generation forecasting

Forecast renewable availability using weather, irradiance, historical generation, and temporal features.

### 3. Model benchmarking

Compare:

- seasonal/naive forecasting
- linear regression
- XGBoost
- Temporal Fusion Transformer
- PatchTST
- selected time-series foundation models

Models are evaluated using rolling time-series validation rather than random train/test splitting.

### 4. Uncertainty-aware forecasting

Produce P10/P50/P90 forecasts that can be consumed by the optimization engine.

### 5. Appliance scheduling

Schedule flexible appliances around:

- expected solar surplus
- electricity tariffs
- household demand
- user preferences
- peak-demand windows

### 6. Battery optimization

Determine when to charge and discharge a household battery while respecting SOC and efficiency constraints.

### 7. EV charging optimization

Schedule EV charging according to:

- current SOC
- target SOC
- departure time
- solar availability
- electricity tariffs
- household demand

### 8. Peak-demand management

Identify expected demand peaks and shift flexible loads to reduce peak grid consumption.

### 9. Energy anomaly detection

Detect unusual household or appliance-level consumption patterns using methods such as Isolation Forest or autoencoder-based approaches.

### 10. Explainable forecasting

Use SHAP and model-specific interpretability techniques to explain the factors influencing demand predictions.

Example:

```text
Predicted demand: 4.2 kW

Temperature          +0.6 kW
Hour of day          +0.8 kW
Previous demand      +0.5 kW
Weekend              -0.2 kW
Solar generation     -0.4 kW
```

### 11. What-if simulation

Simulate household changes such as:

- adding an AC
- adding an EV
- increasing solar capacity
- adding a battery
- changing appliance usage
- changing tariff plans

The system recalculates expected consumption, cost, peak demand, and renewable utilization.

### 12. AI Energy Assistant

The assistant acts as a decision interface over the underlying forecasting and optimization services.

```text
User
  |
  v
AI Energy Assistant
  |
  +--> Demand Forecast
  +--> Solar Forecast
  +--> Tariff Data
  +--> Appliance State
  +--> Optimization Engine
  +--> Anomaly Detection
  |
  v
Grounded Energy Recommendation
```

The LLM is responsible for understanding requests and explaining results. Numerical forecasting and optimization are performed by dedicated services.

---

## Data Pipeline

```text
Raw Data
   |
   v
Validation
   |
   v
Cleaning / Resampling
   |
   v
Feature Engineering
   |
   v
Time-Series Dataset
   |
   +--------------------+
   |                    |
   v                    v
Training Dataset    Inference Dataset
   |                    |
   v                    v
Model Training      Model Inference
   |                    |
   +---------+----------+
             |
             v
      Forecast Storage
             |
             v
       Optimization
```

The target production dataset should contain sufficiently long historical sequences, ideally covering multiple months to multiple years and, where possible, multiple households.

Example feature schema:

```text
timestamp
household_id

load_kw
solar_generation_kw

temperature
humidity
cloud_cover
wind_speed
ghi
dni
dhi

electricity_price

hour
day_of_week
month
is_weekend
is_holiday

ac_usage
water_heater_usage
washing_machine_usage
ev_usage

battery_soc
```

---

## Model Evaluation

Forecasting models are evaluated using chronological splits or rolling-origin validation.

```text
|---------------- Training ----------------|--- Validation ---|--- Test ---|
Past                                                                  Future
```

Primary metrics:

- MAE
- RMSE
- MAPE / sMAPE where appropriate
- prediction interval coverage
- inference latency
- model size / resource requirements

Example evaluation table:

| Model | MAE | RMSE | MAPE | Latency |
|---|---:|---:|---:|---:|
| Seasonal Naive | - | - | - | - |
| XGBoost | - | - | - | - |
| TFT | - | - | - | - |
| PatchTST | - | - | - | - |
| Foundation Model | - | - | - | - |

Values should be populated from actual experiments rather than assumed results.

---

## Explainability and Monitoring

The ML system is designed to expose model behavior rather than treating predictions as black boxes.

Monitoring can include:

```text
Forecast Quality
    |
    +--> MAE
    +--> RMSE
    +--> MAPE
    +--> Interval Coverage

Data Quality
    |
    +--> Missing Values
    +--> Outliers
    +--> Feature Drift

Model Health
    |
    +--> Prediction Drift
    +--> Performance Drift
    +--> Retraining Status
```

SHAP or equivalent methods can be used for feature-level explanations.

---

## Technology Stack

### Backend

- FastAPI
- Uvicorn
- Python

### Machine Learning

- PyTorch
- scikit-learn
- XGBoost
- Transformer-based time-series models
- Time-series foundation models where applicable
- NumPy
- Pandas

### Optimization

- OR-Tools / PuLP
- Constraint-based scheduling
- Battery and EV dispatch optimization

### Data

- PostgreSQL
- Historical smart-meter data
- Weather and irradiance data
- Solar generation data
- Tariff data
- Simulated household/IoT data for development

### AI Assistant

- Azure OpenAI
- Tool-based access to forecasting, optimization, analytics, and simulation services

### Frontend

- HTML/CSS/JavaScript
- Dashboard visualizations

### Serving

- Uvicorn
- Azure App Service or equivalent cloud deployment

---

## Project Structure

The project is being evolved toward the following structure:

```text
.
├── app.py
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   └── schemas/
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── simulation/
│   │
│   ├── features/
│   │   ├── temporal.py
│   │   ├── lag_features.py
│   │   └── weather_features.py
│   │
│   ├── models/
│   │   ├── baselines/
│   │   ├── xgboost/
│   │   ├── tft/
│   │   ├── patchtst/
│   │   └── foundation_models/
│   │
│   ├── forecasting/
│   │   ├── demand.py
│   │   ├── solar.py
│   │   └── uncertainty.py
│   │
│   ├── optimizer/
│   │   ├── appliance_scheduler.py
│   │   ├── battery.py
│   │   ├── ev.py
│   │   └── objective.py
│   │
│   ├── anomaly/
│   │   └── detector.py
│   │
│   ├── explainability/
│   │   └── shap.py
│   │
│   ├── services/
│   │   ├── energy_service.py
│   │   ├── weather_service.py
│   │   └── analytics_service.py
│   │
│   ├── agent/
│   │   ├── tools.py
│   │   └── assistant.py
│   │
│   └── database/
│       ├── models.py
│       └── session.py
│
├── frontend/
│
├── tests/
│
├── requirements.txt
└── README.md
```

The exact structure may evolve during implementation.

---

## API

Core API areas include:

```text
/                       → Dashboard
/docs                   → Swagger / OpenAPI
/api/forecast/*        → Demand and solar forecasting
/api/optimization/*    → Appliance, battery and EV optimization
/api/energy/*          → Household energy data
/api/anomalies/*       → Consumption anomaly detection
/api/simulation/*      → What-if simulations
/api/assistant/*       → AI energy assistant
/api/analytics/*       → Energy analytics and insights
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/rithvik318/gramurja-ai.git
cd gramurja-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
```

Additional database, weather, and model-service variables can be added as the corresponding services are introduced.

### 4. Run the backend

```bash
uvicorn app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---
