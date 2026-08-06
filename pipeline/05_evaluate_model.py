import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import os

def main():
    print("--- Phase 7: Model Evaluation (SHAP & Confusion Matrix) ---")
    
    # 1. Load Model and Data
    print("Loading model and features...")
    xgb_model = joblib.load('models/late_delivery_xgb.pkl')
    
    df = pd.read_parquet('features/model_features.parquet')
    df = df.drop(columns=['order_id'])
    
    cat_cols = ['customer_state', 'seller_state']
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    X = df.drop(columns=['is_late'])
    y = df['is_late']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    os.makedirs('reports/eval', exist_ok=True)
    
    # 2. Confusion Matrix
    print("Generating Confusion Matrix...")
    y_pred = xgb_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["On Time", "Late"])
    disp.plot(cmap='Blues', values_format='d')
    plt.title("XGBoost Confusion Matrix")
    plt.savefig('reports/eval/confusion_matrix.png', bbox_inches='tight')
    plt.close()
    print("Saved 'reports/eval/confusion_matrix.png'")
    
    # 3. SHAP Feature Importance
    print("Generating SHAP Explanations (this might take a moment)...")
    # We use a sample for SHAP to speed up processing
    X_test_sample = X_test.sample(n=min(5000, len(X_test)), random_state=42)
    
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(X_test_sample)
    
    # Summary Plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test_sample, show=False)
    plt.title("SHAP Feature Importance (Late Delivery Drivers)")
    plt.savefig('reports/eval/shap_summary.png', bbox_inches='tight')
    plt.close()
    print("Saved 'reports/eval/shap_summary.png'")
    
    # Bar Plot for global feature importance
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test_sample, plot_type="bar", show=False)
    plt.title("Global Feature Importance")
    plt.savefig('reports/eval/shap_bar.png', bbox_inches='tight')
    plt.close()
    print("Saved 'reports/eval/shap_bar.png'")
    
    print("--- Phase 7 Complete ---")

if __name__ == "__main__":
    main()
