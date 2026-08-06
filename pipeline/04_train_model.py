import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, precision_score, recall_score, f1_score
from pathlib import Path
import joblib

def main():
    print("--- Phase 6a: ML Model Training ---")
    
    # 1. Load Data
    print("Loading features...")
    df = pd.read_parquet('features/model_features.parquet')
    
    # 2. Preprocessing
    print("Preprocessing (One-Hot Encoding)...")
    # Drop order_id as it has no predictive value
    df = df.drop(columns=['order_id'])
    
    # One-Hot Encode states
    cat_cols = ['customer_state', 'seller_state']
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    # 3. Train/Test Split
    print("Splitting data (80/20 Stratified)...")
    X = df.drop(columns=['is_late'])
    y = df['is_late']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Calculate scale_pos_weight for XGBoost to handle class imbalance
    negative_count = (y_train == 0).sum()
    positive_count = (y_train == 1).sum()
    spw = negative_count / positive_count
    print(f"Class imbalance handling -> scale_pos_weight: {spw:.2f}")
    
    # 4. Train Models
    print("\nTraining Baseline: Logistic Regression...")
    lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    lr_probs = lr_model.predict_proba(X_test)[:, 1]
    
    print("Training Advanced: XGBoost Classifier...")
    xgb_model = xgb.XGBClassifier(
        scale_pos_weight=spw,
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        eval_metric='auc',
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    # 5. Evaluate Models
    print("\n--- Evaluation Metrics ---")
    
    def evaluate(name, y_true, preds, probs):
        auc = roc_auc_score(y_true, probs)
        p = precision_score(y_true, preds)
        r = recall_score(y_true, preds)
        f1 = f1_score(y_true, preds)
        print(f"[{name}] ROC-AUC: {auc:.4f} | Precision: {p:.4f} | Recall: {r:.4f} | F1: {f1:.4f}")
        return auc, p, r, f1
        
    lr_metrics = evaluate("Logistic Regression", y_test, lr_preds, lr_probs)
    xgb_metrics = evaluate("XGBoost", y_test, xgb_preds, xgb_probs)
    
    # 6. Export Artifacts
    print("\nExporting final model and metadata...")
    Path('models').mkdir(exist_ok=True)
    
    # Save the model
    joblib.dump(xgb_model, 'models/late_delivery_xgb.pkl')
    
    # Save feature names so the API/Agents know the exact expected input format
    feature_names = list(X_train.columns)
    joblib.dump(feature_names, 'models/feature_names.pkl')
    
    print("Saved 'models/late_delivery_xgb.pkl'")
    print("Saved 'models/feature_names.pkl'")
    
    # Generate Report
    report = f"""# Phase 6a: ML Model Metrics

## Dataset
- **Train Size:** {len(X_train)}
- **Test Size:** {len(X_test)}
- **Features:** {len(feature_names)}

## Model Performance (Test Set)

| Model | ROC-AUC | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Logistic Regression** (Baseline) | {lr_metrics[0]:.4f} | {lr_metrics[1]:.4f} | {lr_metrics[2]:.4f} | {lr_metrics[3]:.4f} |
| **XGBoost** (Primary) | {xgb_metrics[0]:.4f} | {xgb_metrics[1]:.4f} | {xgb_metrics[2]:.4f} | {xgb_metrics[3]:.4f} |

### Imbalance Strategy
We applied a `scale_pos_weight` of **{spw:.2f}** to the XGBoost model to heavily penalize missing a late delivery (prioritizing Recall over naive Accuracy). 

### Artifacts Exported
- Model: `models/late_delivery_xgb.pkl`
- Expected Feature Columns: `models/feature_names.pkl`
"""
    Path('reports').mkdir(exist_ok=True)
    with open('reports/phase6a_model_metrics.md', 'w') as f:
        f.write(report)
        
    print("--- Phase 6a Complete ---")

if __name__ == "__main__":
    main()
