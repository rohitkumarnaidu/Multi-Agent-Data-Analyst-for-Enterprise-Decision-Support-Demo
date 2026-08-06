# Phase 6a: ML Model Metrics

## Dataset
- **Train Size:** 77176
- **Test Size:** 19294
- **Features:** 56

## Model Performance (Test Set)

| Model | ROC-AUC | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Logistic Regression** (Baseline) | 0.6430 | 0.1276 | 0.5636 | 0.2081 |
| **XGBoost** (Primary) | 0.7480 | 0.1819 | 0.5974 | 0.2789 |

### Imbalance Strategy
We applied a `scale_pos_weight` of **11.33** to the XGBoost model to heavily penalize missing a late delivery (prioritizing Recall over naive Accuracy). 

### Artifacts Exported
- Model: `models/late_delivery_xgb.pkl`
- Expected Feature Columns: `models/feature_names.pkl`
