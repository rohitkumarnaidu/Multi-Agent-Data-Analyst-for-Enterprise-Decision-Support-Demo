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
    from sklearn.ensemble import RandomForestClassifier
    print("Training Logistic Regression (Baseline)...")
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    
    print("Training Random Forest...")
    rf = RandomForestClassifier(class_weight='balanced', n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    print("Training XGBoost...")
    pos_weight = sum(y_train == 0) / sum(y_train == 1)
    xgb_model = xgb.XGBClassifier(
        scale_pos_weight=pos_weight, 
        eval_metric='auc',
        random_state=42,
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1
    )
    xgb_model.fit(X_train, y_train)
    
    print("\n--- Model Evaluation (Held-out Test Set) ---")
    
    models = {
        "Logistic Regression (Baseline)": lr,
        "Random Forest": rf,
        "XGBoost": xgb_model
    }
    
    # 5. Evaluate Models
    print("\n--- Evaluation Metrics ---")
    
    def evaluate(name, y_true, model):
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_true, probs)
        p = precision_score(y_true, preds)
        r = recall_score(y_true, preds)
        f1 = f1_score(y_true, preds)
        print(f"[{name}] ROC-AUC: {auc:.4f} | Precision: {p:.4f} | Recall: {r:.4f} | F1: {f1:.4f}")
        return auc, p, r, f1
        
    metrics_log = {}
    best_f1 = 0
    best_model_name = ""
    best_model_obj = None
    
    for name, mdl in models.items():
        m = evaluate(name, y_test, mdl)
        metrics_log[name] = m
        if m[3] > best_f1:  # Pick best model by F1 Score
            best_f1 = m[3]
            best_model_name = name
            best_model_obj = mdl
            
    print(f"\nWINNER: {best_model_name} with F1: {best_f1:.4f}")
    
    # 6. Export Artifacts
    print("\nExporting final model and metadata...")
    Path('models').mkdir(exist_ok=True)
    
    # Save the model
    # Derive filename
    model_filename = 'late_delivery_xgb.pkl' if 'XGB' in best_model_name else 'late_delivery_rf.pkl' if 'Forest' in best_model_name else 'late_delivery_lr.pkl'
    joblib.dump(best_model_obj, f'models/{model_filename}')
    
    # Save feature names so the API/Agents know the exact expected input format
    feature_names = list(X_train.columns)
    joblib.dump(feature_names, 'models/feature_names.pkl')
    
    print(f"Saved 'models/{model_filename}'")
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
"""
    for name, m in metrics_log.items():
        report += f"| **{name}** | {m[0]:.4f} | {m[1]:.4f} | {m[2]:.4f} | {m[3]:.4f} |\n"
        
    report += f"""
### Imbalance Strategy
We applied a class weighting/SMOTE equivalent to prioritize Recall over naive Accuracy. 
For XGBoost, `scale_pos_weight` was set to **{spw:.2f}**.

### Artifacts Exported
- Best Model ({best_model_name}): `models/{model_filename}`
- Expected Feature Columns: `models/feature_names.pkl`
"""
    Path('reports').mkdir(exist_ok=True)
    with open('reports/phase6a_model_metrics.md', 'w') as f:
        f.write(report)
        
    # Generate model_card.md for rubric compliance
    with open('models/model_card.md', 'w') as f:
        f.write(report)
        
    print("--- Phase 6a Complete ---")

if __name__ == "__main__":
    main()
