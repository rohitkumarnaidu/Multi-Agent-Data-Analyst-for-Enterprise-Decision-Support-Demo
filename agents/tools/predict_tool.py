import joblib
import pandas as pd
import numpy as np
from langchain.tools import tool

# Load model and expected features at module level so it doesn't reload every call
MODEL_PATH = 'models/late_delivery_xgb.pkl'
FEATURES_PATH = 'models/feature_names.pkl'

try:
    xgb_model = joblib.load(MODEL_PATH)
    expected_features = joblib.load(FEATURES_PATH)
except FileNotFoundError:
    xgb_model = None
    expected_features = None

@tool("Predict Late Delivery Risk")
def predict_late_delivery(features_json: str) -> str:
    """
    Predicts the probability that an order will be delivered late based on its features.
    Input must be a valid JSON string representing a dictionary of features.
    
    Required features in the JSON:
    - product_weight_g (float, grams)
    - product_volume_cm3 (float, cm3)
    - freight_value (float, total freight paid)
    - price (float, total product price)
    - freight_to_price_ratio (float, freight / price)
    - order_to_approval_hrs (float, hours to approve payment)
    - day_of_week_ordered (int, 0=Mon, 6=Sun)
    - month_ordered (int, 1-12)
    - seller_recent_late_rate (float, historical late rate 0.0-1.0)
    - customer_state (string, e.g., 'SP', 'RJ')
    - seller_state (string, e.g., 'SP', 'MG')
    
    Example input:
    '{"product_weight_g": 500, "product_volume_cm3": 1000, "freight_value": 15.5, "price": 49.9, "freight_to_price_ratio": 0.31, "order_to_approval_hrs": 2.5, "day_of_week_ordered": 1, "month_ordered": 5, "seller_recent_late_rate": 0.05, "customer_state": "SP", "seller_state": "RJ"}'
    """
    if xgb_model is None or expected_features is None:
        return "Error: ML Model not found. Ensure Phase 6a has been run successfully."
        
    try:
        import json
        raw_features = json.loads(features_json)
        
        # 1. Convert raw input dictionary into a 1-row DataFrame
        df_raw = pd.DataFrame([raw_features])
        
        # 2. Replicate the exact One-Hot Encoding logic from training
        # First, ensure we have dummy columns for whatever state was passed
        cat_cols = ['customer_state', 'seller_state']
        for col in cat_cols:
            if col in df_raw.columns:
                df_raw = pd.get_dummies(df_raw, columns=[col])
        
        # 3. Align the DataFrame to exactly match the 61 features the model expects
        # We create a new DataFrame full of 0s with the exact expected columns
        df_final = pd.DataFrame(0, index=np.arange(1), columns=expected_features)
        
        # Map the values from df_raw into df_final
        for col in df_raw.columns:
            if col in df_final.columns:
                df_final[col] = df_raw[col]
                
        # Handle boolean from get_dummies by converting to int
        df_final = df_final.astype(float)

        # 4. Predict
        prob = xgb_model.predict_proba(df_final)[0][1]
        
        return f"Predicted Late Delivery Probability: {prob * 100:.2f}%"
        
    except json.JSONDecodeError:
        return "Error: Input must be a valid JSON string. Do NOT use single quotes for keys."
    except Exception as e:
        return f"Prediction Error: {str(e)}"
