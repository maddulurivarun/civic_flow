import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import joblib

st.set_page_config(page_title="CivicFlow Transit Control Center", layout="wide")

st.title("🏙️ CivicFlow: Smart City Mobility & Grid Optimizer")
st.markdown("Real-time optimization engine for electric vehicle infrastructure and public transit micro-routing.")

# Load data and artifacts
@st.cache_data
def get_data():
    stations = pd.read_csv("data/raw/ev_stations.csv")
    telemetry = pd.read_csv("data/raw/realtime_city_telemetry.csv")
    return stations, telemetry

df_stations, df_telemetry = get_data()

try:
    model = joblib.load("src/demand_model.pkl")
except:
    st.error("Model file not found. Please run 'python src/model.py' first.")
    st.stop()

# Layout Columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚡ Grid Analytics & Pricing")
    
    # Calculate Live Surge Multipliers using our model
    latest_step = df_telemetry['step'].max()
    live_df = df_telemetry[df_telemetry['step'] == latest_step].copy()
    live_df['hour'] = 12 # Simulating midday peak
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
    # Read the pre-compiled HTML map we generated in preprocess.py
    try:
        with open("data/processed/city_map.html", "r", encoding="utf-8") as f:
            html_map = f.read()
        st.components.v1.html(html_map, height=500)
    except:
        st.info("Run preprocessing to see the map or check file paths.")

st.success("CivicFlow Backend Core: Online & Optimizing.")
