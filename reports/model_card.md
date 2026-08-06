# Model Card: Late Delivery Prediction Model

## Model Details
- **Architecture:** XGBoost Classifier (`xgboost`)
- **Objective:** Predict if an e-commerce order will be delivered later than the estimated delivery date.
- **Features:** 61 One-Hot Encoded features (derived from 11 raw features including product dimensions, price, freight, states, and seller historical late rate).

## Training Configuration
- **Handling Imbalance:** Applied `scale_pos_weight = 11.33` to heavily prioritize identifying late deliveries (Recall) over raw accuracy.
- **Hyperparameters:** `n_estimators=150`, `max_depth=5`, `learning_rate=0.1`, `subsample=0.8`.

## Evaluation Metrics (Test Set)
- **ROC-AUC:** ~0.748
- **Precision:** ~0.15 (Expectedly low due to aggressive scale_pos_weight)
- **Recall:** ~0.85 (Successfully captures vast majority of actual late deliveries)
- **F1-Score:** ~0.26

## Feature Importance (SHAP)
Based on TreeExplainer SHAP values generated in Phase 7:
1. **Seller's Historical Late Rate:** The dominant predictor. A high historical late rate vastly increases the probability of the current order being late.
2. **Freight Value & Freight-to-Price Ratio:** Higher freight generally correlates with increased late delivery risk.
3. **Customer/Seller State:** Geographic distance, particularly deliveries destined for remote states, significantly impacts delivery times.

## Limitations
- Model cannot account for real-time supply chain disruptions (e.g., strikes, extreme weather).
- Excludes canceled orders.
