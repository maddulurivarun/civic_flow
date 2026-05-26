import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

def load_and_clean_data():
    print("Loading raw simulated city data...")
    # Read the generated CSV files
    df_stations = pd.read_csv("data/raw/ev_stations.csv")
    df_telemetry = pd.read_csv("data/raw/realtime_city_telemetry.csv")
    
    # Check for missing values (even though it's simulated, good practice!)
    assert df_stations.isnull().sum().sum() == 0, "Found missing values in stations data"
    
    print(f"Loaded {len(df_stations)} stations and {len(df_telemetry)} telemetry records.")
    return df_stations, df_telemetry

def generate_interactive_map(df_stations, df_telemetry):
    print("Generating geospatial interactive map...")
    
    # Map centered around our metropolitan center
    city_map = folium.Map(location=[42.3601, -71.0589], zoom_start=13, tiles="cartodbpositron")
    
    # 1. Plot EV Charging Stations (Blue Markers)
    for _, row in df_stations.iterrows():
        popup_text = f"Station: {row['station_id']}<br>Total Ports: {row['total_ports']}<br>Base Price: ${row['base_price_per_kwh']}/kWh"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="flash", prefix="fa")
        ).add_to(city_map)
        
    # 2. Plot Recent Bus Telemetry Locations (Red Circle Markers showing passenger load)
    # Let's take the latest step to see where buses ended up
    latest_step = df_telemetry['step'].max()
    df_latest_bus = df_telemetry[df_telemetry['step'] == latest_step].drop_duplicates(subset=['route_id'])
    
    for _, row in df_latest_bus.iterrows():
        popup_text = f"Route: {row['route_id']}<br>Passengers: {row['passenger_count']}"
        folium.CircleMarker(
            location=[row['bus_latitude'], row['bus_longitude']],
            radius=8 + (row['passenger_count'] / 10), # Dynamically size based on passenger volume
            popup=popup_text,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6
        ).add_to(city_map)
        
    # Save the map to our processed data directory as an interactive webpage
    output_path = "data/processed/city_map.html"
    city_map.save(output_path)
    print(f"Interactive map successfully rendered and saved to {output_path}")

if __name__ == "__main__":
    stations, telemetry = load_and_clean_data()
    generate_interactive_map(stations, telemetry)
