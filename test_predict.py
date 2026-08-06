import pandas as pd
import joblib
import sys

def main():
    print("--- Round-Trip Prediction Test ---")
    
    # 1. Load the best model
    try:
        model = joblib.load('models/late_delivery_xgb.pkl')
        print("Successfully loaded late_delivery_xgb.pkl")
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)
        
    # 2. Load feature names to ensure exactly the right columns
    feature_names = joblib.load('models/feature_names.pkl')
    
    # 3. Create a dummy order
    dummy_data = {col: 0 for col in feature_names}
    
    # Fill in some realistic dummy values
    if 'freight_value' in dummy_data:
        dummy_data['freight_value'] = 45.0
    if 'price' in dummy_data:
        dummy_data['price'] = 120.0
    if 'product_weight_g' in dummy_data:
        dummy_data['product_weight_g'] = 5000.0
    if 'order_to_approval_hrs' in dummy_data:
        dummy_data['order_to_approval_hrs'] = 2.5
    if 'seller_recent_late_rate' in dummy_data:
        dummy_data['seller_recent_late_rate'] = 0.15
        
    df_dummy = pd.DataFrame([dummy_data])
    
    # 4. Predict
    try:
        prob = model.predict_proba(df_dummy)[0][1]
        print(f"\nTest Prediction (Probability of Late Delivery): {prob:.4f}")
    except Exception as e:
        print(f"Prediction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
