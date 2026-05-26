import os
import random
import time
from datetime import datetime
import pandas as pd
import numpy as np

def generate_city_base(num_ev_stations=15, num_bus_routes=5):
    print("Initializing CivicFlow City Grid Simulation...")
    
    # Center coordinates around a metropolitan center (Lat: 42.3601, Lon: -71.0589)
    center_lat, center_lon = 42.3601, -71.0589
    
    # 1. Generate Static EV Charging Stations
    stations = []
    for i in range(num_ev_stations):
        # Introduce slight random variance to distribute stations across the city
        lat = center_lat + random.uniform(-0.05, 0.05)
        lon = center_lon + random.uniform(-0.05, 0.05)
        total_ports = random.choice([4, 8, 12, 16])
        
        stations.append({
            "station_id": f"EV_{i:03d}",
            "latitude": lat,
            "longitude": lon,
            "total_ports": total_ports,
            "base_price_per_kwh": 0.25
        })
    
    df_stations = pd.DataFrame(stations)
    df_stations.to_csv("data/raw/ev_stations.csv", index=False)
    print(f" Saved {num_ev_stations} static EV station locations to data/raw/ev_stations.csv")

    # 2. Generate Simulated Transit Bus Route Nodes
    routes = {}
    for r in range(1, num_bus_routes + 1):
        # Create a linear path of 5 stops for each route
        start_lat = center_lat + random.uniform(-0.04, 0.04)
        start_lon = center_lon + random.uniform(-0.04, 0.04)
        
        route_stops = []
        for s in range(5):
            route_stops.append((
                start_lat + (s * 0.01 * random.uniform(0.8, 1.2)),
                start_lon + (s * 0.01 * random.uniform(0.8, 1.2))
            ))
        routes[f"Route_{r}"] = route_stops
        
    return df_stations, routes

def simulate_realtime_stream(df_stations, routes, duration_steps=50):
    print("\nStarting real-time data stream simulation...")
    
    all_telemetry = []
    
    for step in range(duration_steps):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simulate EV Station real-time loads
        for _, station in df_stations.iterrows():
            # Higher utilization simulated randomly to mimic peak hours
            occupied_ports = random.randint(0, station["total_ports"])
            grid_load_kw = occupied_ports * random.uniform(50.0, 150.0) # Fast chargers
            
            # Simulate real-time transit telemetry pings
            for route_id, stops in routes.items():
                # Pick a random point along the route stops to represent current bus position
                current_stop_idx = random.randint(0, len(stops) - 1)
                bus_lat, bus_lon = stops[current_stop_idx]
                passenger_count = random.randint(0, 50)
                
                all_telemetry.append({
                    "timestamp": current_time,
                    "step": step,
                    "station_id": station["station_id"],
                    "occupied_ports": occupied_ports,
                    "grid_load_kw": round(grid_load_kw, 2),
                    "route_id": route_id,
                    "bus_latitude": bus_lat + random.uniform(-0.001, 0.001), # Add slight traffic jitter
                    "bus_longitude": bus_lon + random.uniform(-0.001, 0.001),
                    "passenger_count": passenger_count
                })
                
        time.sleep(0.1) # Simulate rapid real-time pings
        
    df_telemetry = pd.DataFrame(all_telemetry)
    df_telemetry.to_csv("data/raw/realtime_city_telemetry.csv", index=False)
    print(f" Generated {len(df_telemetry)} real-time telemetry events in data/raw/realtime_city_telemetry.csv")

if __name__ == "__main__":
    stations, routes = generate_city_base()
    simulate_realtime_stream(stations, routes)
