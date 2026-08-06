import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os

def main():
    print("--- Phase 7: SHAP Explainability Analysis ---")
    
    # 1. Load Model and Data
    print("Loading XGBoost model and model_features.parquet...")
    xgb_model = joblib.load('models/late_delivery_xgb.pkl')
    
    df = pd.read_parquet('features/model_features.parquet')
    df = df.drop(columns=['order_id'])
    
    # One-hot encode to match training space
    cat_cols = ['customer_state', 'seller_state']
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    X = df.drop(columns=['is_late'])
    y = df['is_late']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    os.makedirs('reports', exist_ok=True)
    
    # 2. SHAP Feature Importance
    print("Computing SHAP values...")
    # Sample for speed
    X_test_sample = X_test.sample(n=min(5000, len(X_test)), random_state=42)
    
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(X_test_sample)
    
    # Summary Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test_sample, show=False)
    plt.title("SHAP Feature Importance (Late Delivery Drivers)")
    plt.savefig('reports/shap_summary.png', bbox_inches='tight')
    plt.close()
    
    # 3. Print Top 5 Features
    # Calculate mean absolute SHAP value for each feature
    vals = np.abs(shap_values).mean(0)
    feature_importance = pd.DataFrame(list(zip(X_test_sample.columns, vals)), columns=['Feature', 'Importance'])
    feature_importance.sort_values(by=['Importance'], ascending=False, inplace=True)
    
    print("\n--- TOP 5 MOST IMPORTANT FEATURES ---")
    for i, row in feature_importance.head(5).iterrows():
        print(f"{row['Feature']}: {row['Importance']:.4f}")
        
    print("\nSaved 'reports/shap_summary.png'")
    print("--- Phase 7 SHAP Complete ---")

if __name__ == "__main__":
    main()
