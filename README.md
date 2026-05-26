# 🏙️ CivicFlow: Smart City Mobility & Grid Optimizer

An end-to-end Data Science & Optimization engine that uses real-time simulation, time-series feature engineering, and Machine Learning to optimize metropolitan EV charging infrastructure and public transit micro-routing.

## 🛠️ Tech Stack & Architecture
* **Data Simulation & Ingestion:** Python (`pandas`, `numpy`) simulating dynamic time-series city telemetry.
* **Geospatial Pipeline:** `geopandas`, `shapely`, and `folium` for geographical point mapping and interactive route rendering.
* **Machine Learning Engine:** `scikit-learn` (Random Forest Regressor) predicting fast-charger power grid loads.
* **Interactive Dashboard:** `streamlit` & `streamlit-folium` for a live operator tracking control panel.

## 📁 Project Structure
```text
civic_flow/
├── data/
│   ├── raw/          # Ingested EV station nodes & telemetry streams
│   └── processed/    # Compiled HTML interactive maps
├── src/
│   ├── ingest.py     # Grid generation and live data stream simulator
│   ├── preprocess.py # Geospatial transformation pipeline
│   ├── model.py      # Random Forest trainer & dynamic pricing logic
│   └── app.py        # Streamlit interactive UI dashboard
└── requirements.txt  # Project environment dependencies
