import streamlit as st
import pandas as pd
import os
import subprocess
import sys
import joblib

st.set_page_config(page_title="CivicFlow Transit Control Center", layout="wide")

st.title("🏙️ CivicFlow: Smart City Mobility & Grid Optimizer")
st.markdown("Real-time optimization engine for electric vehicle infrastructure and public transit micro-routing.")

# Create missing data paths immediately
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# Explicitly use sys.executable to run scripts in the correct cloud venv environment
if not os.path.exists("data/raw/ev_stations.csv") or not os.path.exists("src/demand_model.pkl"):
    with st.spinner("Initializing cloud datasets and training ML engine (this may take up to 30 seconds)..."):
        subprocess.run([sys.executable, "src/ingest.py"])
        subprocess.run([sys.executable, "src/preprocess.py"])
        subprocess.run([sys.executable, "src/model.py"])

@st.cache_data
def get_data():
    stations = pd.read_csv("data/raw/ev_stations.csv")
    telemetry = pd.read_csv("data/raw/realtime_city_telemetry.csv")
    return stations, telemetry

df_stations, df_telemetry = get_data()
model = joblib.load("src/demand_model.pkl")

# Layout Columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚡ Grid Analytics & Pricing")
    
    latest_step = df_telemetry['step'].max()
    live_df = df_telemetry[df_telemetry['step'] == latest_step].copy()
    live_df['hour'] = 12
    live_df['station_numeric'] = live_df['station_id'].astype('category').cat.codes
    
    X_live = live_df[['step', 'hour', 'station_numeric', 'passenger_count']]
    live_df['predicted_load'] = model.predict(X_live)
    
    for _, row in live_df.drop_duplicates(subset=['station_id']).head(4).iterrows():
        is_surge = row['predicted_load'] > 700
        rate = 0.38 if is_surge else 0.25
        status_emoji = "🚨 High Load" if is_surge else "✅ Normal"
        
        st.metric(
            label=f"Station {row['station_id']} ({status_emoji})", 
            value=f"${rate:.2f} / kWh", 
            delta=f"{row['predicted_load']:.1f} kW Load"
        )

with col2:
    st.header("🗺️ Live Dispatch Map")
    try:
        with open("data/processed/city_map.html", "r", encoding="utf-8") as f:
            html_map = f.read()
        st.components.v1.html(html_map, height=500)
    except:
        st.info("Generating map layer coordinates...")
