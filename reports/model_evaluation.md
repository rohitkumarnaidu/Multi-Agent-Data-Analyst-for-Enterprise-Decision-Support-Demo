# Phase 7: Consolidated Model Evaluation Report

## 1. Machine Learning Metrics (XGBoost)

| Metric | Score | Context |
|---|---|---|
| **ROC-AUC** | ~0.748 | Moderate discriminative ability |
| **Precision** | ~0.150 | Expectedly low; reflects trade-off for high recall |
| **Recall** | ~0.850 | Excellent; captures 85% of actual late deliveries |
| **F1-Score** | ~0.260 | Heavily weighted towards recall |

*Note on Strategy:* We applied `scale_pos_weight = 11.33` to heavily penalize missing a late delivery, prioritizing Recall over naive Accuracy.

---

## 2. SHAP Explainability & Feature Importance

![SHAP Summary Plot](../reports/shap_summary.png)

### Top 5 Most Important Features
*(Business Interpretations)*

1. **`month_ordered`**: The strongest predictor by far. Seasonality (e.g. holiday rushes like Black Friday in November) fundamentally overwhelms the logistics network.
2. **`seller_recent_late_rate`**: Sellers with a historical track record of failing to deliver on time are highly likely to repeat the behavior on current orders.
3. **`customer_state_SP`**: As the state with the highest volume (Sao Paulo), deliveries here heavily swing the model's predictions.
4. **`order_to_approval_hrs`**: Prolonged payment approval times eat into the seller's fulfillment window, increasing the risk of missing the final delivery estimate.
5. **`customer_state_MG`**: Deliveries heading to Minas Gerais (MG) also present systemic logistical impacts.

**Sanity Check against Phase 4 EDA:** 
*PASS.* The SHAP values align perfectly with our EDA findings. In EDA, we saw massive seasonal spikes (Black Friday / November) causing the majority of delays, which is confirmed here by `month_ordered` being the #1 most important feature. We also saw that individual seller performance heavily dictated review scores (which act as a proxy for delivery success), aligning with `seller_recent_late_rate` being the #2 most important feature. The states of SP and MG being highly represented aligns with their massive volume in the dataset.

---

## 3. Agent System (Phase 6b) QA Transcript

> **STATUS: PENDING**
> The Docker container is currently downloading the required AI libraries over a slow network connection. Once it boots, `agents/run_audit.py` will execute the 5 SCOPE.md questions, and the condensed transcript will be injected here.
