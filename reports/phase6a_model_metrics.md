# Phase 6a: ML Model Metrics

## Dataset
- **Train Size:** 77176
- **Test Size:** 19294
- **Features:** 56

## Model Performance (Test Set)

| Model | ROC-AUC | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Logistic Regression (Baseline)** | 0.6430 | 0.1276 | 0.5636 | 0.2081 |
| **Random Forest** | 0.7325 | 0.1824 | 0.5642 | 0.2757 |
| **XGBoost** | 0.7439 | 0.1980 | 0.5757 | 0.2947 |

### Imbalance Strategy
We applied a class weighting/SMOTE equivalent to prioritize Recall over naive Accuracy. 
For XGBoost, `scale_pos_weight` was set to **11.33**.

### Artifacts Exported
- Best Model (XGBoost): `models/late_delivery_xgb.pkl`
- Expected Feature Columns: `models/feature_names.pkl`
