# GramUrja-AI

Backend system for intelligent household energy management.
Focuses on **predicting demand, optimizing appliance usage, and integrating solar availability** using lightweight ML + rule-based scheduling.

---

## What it does

The system models a household’s daily energy usage and answers:

* *How much energy will be consumed?* → demand forecasting
* *When should appliances run?* → cost-aware scheduling
* *How to use solar efficiently?* → generation-aware optimization

Outputs include:

* optimized appliance schedules
* predicted load curves
* basic cost/usage insights

---

## How it works

1. **Input Layer**

   * Simulated household data (load, appliances, solar)
   * Time-based features (hour, tariff window)

2. **Prediction Layer**

   * ML model forecasts short-term energy demand
   * Solar generation estimated from patterns

3. **Optimization Layer**

   * Rule-based scheduler shifts flexible loads
   * Minimizes cost while respecting constraints

4. **API Layer**

   * FastAPI exposes endpoints for predictions, scheduling, and insights

5. **Frontend**

   * Static HTML served via backend for quick visualization

---

## Stack

* **Backend:** FastAPI
* **ML:** scikit-learn
* **Optimization:** custom logic (constraint-based)
* **Data:** simulated CSV
* **Serving:** Uvicorn

---

## Structure

```
.
├── app.py
├── backend/
│   ├── services/      # business logic
│   ├── model/         # ML models
│   ├── optimizer/     # scheduling logic
│   └── data/          # simulated datasets
├── frontend/
├── requirements.txt
```

---

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

---

## Env

```
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
```

---

## Notes

* Designed as a hackathon MVP
* No external DB (stateless, file-based)
* Easily deployable on Azure App Service

---

## API

* `/` → UI
* `/docs` → Swagger
* `/api/*` → prediction + optimization endpoints
