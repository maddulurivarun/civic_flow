import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

def prepare_ml_data():
    print("Preparing features for the optimization model...")
    df = pd.read_csv("data/raw/realtime_city_telemetry.csv")
    
    # Feature Engineering
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['station_numeric'] = df['station_id'].astype('category').cat.codes
    df['route_numeric'] = df['route_id'].astype('category').cat.codes
    
    # Define features and target for EV Grid Load forecasting
    X = df[['step', 'hour', 'station_numeric', 'passenger_count']]
    y = df['grid_load_kw']
    
    return train_test_split(X, y, test_size=0.2, random_state=42), df

def train_demand_forecaster(splits):
    X_train, X_test, y_train, y_test = splits
    print("Training Random Forest Grid-Load Predictor Engine...")
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Model Training Complete. R^2 Variance Score: {score:.4f}")
    
    joblib.dump(model, "src/demand_model.pkl")
    return model

def run_dynamic_optimization(model, original_df):
    print("\nRunning live smart-city optimization algorithms...")
    
    latest_events = original_df[original_df['step'] == original_df['step'].max()].copy()
    latest_events['hour'] = pd.to_datetime(latest_events['timestamp']).dt.hour
    latest_events['station_numeric'] = latest_events['station_id'].astype('category').cat.codes
    latest_events['route_numeric'] = latest_events['route_id'].astype('category').cat.codes
    
    X_live = latest_events[['step', 'hour', 'station_numeric', 'passenger_count']]
    predicted_loads = model.predict(X_live)
    
    latest_events['predicted_grid_load'] = predicted_loads
    
    print("\n[OPTIMIZATION RESULTS: EV CHARGING NETWORK]")
    for _, row in latest_events.drop_duplicates(subset=['station_id']).head(5).iterrows():
        base_price = 0.25
        surge_multiplier = 1.5 if row['predicted_grid_load'] > 700 else 1.0
        final_price = base_price * surge_multiplier
        print(f" Station {row['station_id']}: Predicted Load {row['predicted_grid_load']:.1f}kW | Dynamic Rate: ${final_price:.2f}/kWh (Multiplier: {surge_multiplier}x)")

    print("\n[OPTIMIZATION RESULTS: PUBLIC TRANSIT CONGESTION]")
    high_occupancy_threshold = 35
    congested_routes = latest_events[latest_events['passenger_count'] > high_occupancy_threshold]['route_id'].unique()
    
    if len(congested_routes) > 0:
        for route in congested_routes:
            print(f" ALERT: {route} passenger load exceeded threshold. Triggering micro-routing backup logic.")
    else:
        print(" Transit network flowing normally. No route adjustments needed.")

if __name__ == "__main__":
    splits, original_df = prepare_ml_data()
    trained_model = train_demand_forecaster(splits)
    run_dynamic_optimization(trained_model, original_df)
