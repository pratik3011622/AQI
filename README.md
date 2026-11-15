# Air Quality Forecasting Dashboard

A full-stack AI/ML project that predicts tomorrow’s AQI using city-level air-quality history, a trained regression model, and a polished React dashboard.

This project brings together:

- Python data processing and feature engineering
- model training and evaluation
- a FastAPI backend for inference
- a React + Vite frontend for interaction and presentation
- project-ready documentation for demos, presentations, and further deployment

> Research prototype only. It is designed for demonstration and learning workflows, not as an official public-health advisory.

## Project overview

The system lets a user choose a city, automatically loads recent AQI data from the dataset, and predicts the next day’s AQI. The app hides the technical feature engineering from the end user and keeps the experience simple: select city, click predict, and view the result.

The core idea is to forecast next-day AQI using recent AQI values and supporting time-based signals. The pipeline is structured so the same model can be used in research, API inference, and a web demo.

## What this project does

- loads and normalizes daily AQI CSV data
- builds lag and rolling features from historical AQI
- trains and compares forecasting models
- saves the best model and metadata
- exposes prediction and analysis endpoints through FastAPI
- renders a modern dashboard in React
- supports city selection and automatic AQI history loading

## Tech stack

- Python 3.10+
- pandas, numpy, scikit-learn, xgboost, joblib
- FastAPI + Uvicorn
- React + Vite + Recharts
- Node.js 20+

## Dataset

The project is designed to work with real AQI datasets in daily format. It accepts common schema variations such as:

- City / Date / AQI
- area / date / aqi_value
- state-level or city-level daily monitoring data

The preprocessing logic normalizes field names and date formats so that real-world CSVs work without major manual editing.

Recommended workflow:

1. Place the AQI CSV file inside data/raw/
2. Ensure it contains city and date columns
3. Let the training and API code normalize the format automatically

## System architecture

```text
data/raw/CSV
    ↓
Python preprocessing + feature engineering
    ↓
Model training (Ridge / Random Forest / XGBoost)
    ↓
Saved model artifact in models/
    ↓
FastAPI backend (backend/main.py)
    ↓
React frontend (frontend/src/App.jsx)
    ↓
User interaction and prediction dashboard
```

## How the prediction flow works

1. The user selects a city.
2. The frontend requests recent AQI history from the backend.
3. The backend loads the city’s latest AQI values from the dataset.
4. The app derives the last 7-day AQI pattern automatically.
5. The prediction payload is sent to the model endpoint.
6. The model returns tomorrow’s AQI estimate and a category label.

This means the user does not need to manually type all lag values.

## Project structure

```text
AIML/
├── backend/
│   ├── main.py
│   ├── schemas.py
│   └── __init__.py
├── data/
│   ├── raw/
│   └── processed/
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── models/
│   ├── best_model.joblib
│   └── metadata.json
├── src/
│   ├── config.py
│   ├── data_utils.py
│   ├── evaluate.py
│   ├── experiments.py
│   ├── train.py
│   ├── weather.py
│   └── __init__.py
├── tests/
│   └── test_data_utils.py
├── README.md
├── requirements.txt
├── paper/
├── results/
└── notebooks/
```

## Setup and installation

### 1) Create the Python environment

```powershell
cd "path/to/AIML"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2) Train the model

```powershell
python -m src.train
```

This step builds the AQI forecasting model and stores artifacts in the models folder.

### 3) Run the backend API

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

Open the docs here:

- http://127.0.0.1:8001/docs

### 4) Run the frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Then open the port shown in the terminal, usually:

- http://localhost:5173

## API endpoints

- GET /health
- GET /cities
- GET /history/{city}
- POST /predict
- GET /transfer-matrix
- GET /explain/{city}

The predict endpoint supports a simple city-first request such as:

```json
{
  "city": "Delhi"
}
```

The backend automatically fills the missing lag values from recent AQI data when needed.

## Deployment notes

For real deployment, do the following:

1. host the FastAPI backend on a cloud service or VM
2. set the frontend API URL in the environment or deployment config
3. keep the model artifact in a stable storage path
4. configure CORS for the production frontend domain
5. use environment variables instead of hardcoded ports
6. add monitoring and logging for failed predictions and missing data

## Validation commands

Run the Python tests:

```powershell
python -m unittest discover -s tests
```

Build the frontend:

```powershell
cd frontend
npm run build
```

## Final note

This project is a strong presentation-ready AI/ML application because it combines a real data pipeline, model training, API integration, and web interface in one coherent system. It is suitable for showcasing in academic, portfolio, or internship contexts.

If you want, the next step can be to add:

- deployment to Render/Fly.io/VM
- database storage for requests
- improved AQI category insights
- a public landing page and project demo video script
