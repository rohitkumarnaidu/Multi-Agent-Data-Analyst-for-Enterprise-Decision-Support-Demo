# Phase 2 — Problem Understanding & Scope

*Locked before Phase 3 execution. All team members should review and agree.*

---

## 1. ML Target (Locked)

**Target: Late Delivery Risk — Binary Classification**

```
Label definition:
  is_late = 1  if  order_delivered_customer_date > order_estimated_delivery_date
  is_late = 0  if  order delivered on or before estimated date

Scope:
  ✅ INCLUDE: orders where order_status = 'delivered' AND delivered_date IS NOT NULL
  ❌ EXCLUDE: cancelled, unavailable, invoiced, processing orders (no ground truth)

Expected positive rate: ~8% of delivered orders are late
Expected training set size: ~96,000 orders
```

---

## 2. Feature Plan

These features will be engineered in Phase 5 from `orders_master`:

| Feature | Source | Type | Rationale |
|---|---|---|---|
| `customer_state` | customers | categorical | Geographic demand patterns |
| `seller_state` | sellers | categorical | Seller logistics region |
| `same_state` | derived | binary | Same-state = faster delivery |
| `order_to_approval_hrs` | orders | numeric | Slow approval → late delivery |
| `freight_to_price_ratio` | order_items | numeric | High freight = complex logistics |
| `product_weight_g` | products | numeric | Heavy = harder to ship |
| `product_volume_cm3` | products | numeric | Large = harder to ship |
| `day_of_week_ordered` | orders | categorical | Weekend orders ship slower |
| `month_ordered` | orders | categorical | Seasonality (holiday peaks) |
| `seller_hist_late_rate` | derived | numeric | Seller's past performance |
| `item_count` | order_items | numeric | Multi-item = more complex |
| `max_installments` | payments | numeric | Proxy for order value tier |

**Target variable:** `is_late` (from `clean_orders`)

---

## 3. Agent MVP Scope

### ✅ Build (MVP — 6 agents)

| # | Agent | LLM | Purpose |
|---|---|---|---|
| 1 | **Orchestrator** | GPT-4o-mini | Parse intent, route to correct agents |
| 2 | **Data Retrieval** | Ollama phi3:mini | Text-to-SQL → DuckDB |
| 3 | **Predictive** | Ollama phi3:mini | Call `late_delivery_xgb.pkl` |
| 4 | **Analysis** | Ollama phi3:mini | Aggregate/summarize data |
| 5 | **Visualization** | Ollama phi3:mini | Generate charts (matplotlib/plotly) |
| 6 | **Insight & Narrative** | GPT-4o-mini | Plain-English answer + recommendation |

### 🔜 Bonus (if time)
| Agent | Value |
|---|---|
| **Explainability/Validation** | Cross-checks narrative vs retrieved data — directly answers "how do we know it's not hallucinating" judge question |

### ❌ Out of Scope (this iteration)
- Multilingual support (Portuguese)
- Voice input (Whisper)
- Auto-PPT generation
- What-if simulator
- Proactive alerts

---

## 4. Success Criteria

### ML Model
| Metric | Target | Why |
|---|---|---|
| ROC-AUC | ≥ 0.75 | Standard for imbalanced binary classification |
| F1 (late class) | ≥ 0.60 | Precision + recall on the minority class |
| Precision (late) | ≥ 0.55 | Don't over-flag on-time orders as late |
| Recall (late) | ≥ 0.65 | Catch most actual late deliveries |

### Agent System
| Criterion | Target |
|---|---|
| Correct SQL on 20 test questions | ≥ 80% |
| Answer factually grounded in data | 100% |
| Response time (end-to-end) | < 30 seconds |
| 3 demo questions answered correctly live | 100% |

---

## 5. Demo Questions (Pre-Planned)

These 3 questions will be rehearsed before demo day. Answers pre-verified manually.

```
Q1: "Which sellers have the highest late delivery rate this year?"
    → Retrieval: SQL groupby seller + is_late, ordered DESC
    → Expected: table of top 10 sellers with late %

Q2: "What is the on-time delivery rate for orders from São Paulo?"
    → Retrieval: SQL filter customer_state='SP', AVG(1-is_late)
    → Expected: single % figure + comparison to national average

Q3: "Which orders placed today are at risk of arriving late?"
    → Predictive: load model, score recent orders, return ranked list
    → Expected: table of at-risk order IDs + risk scores + SHAP explanation
```

---

## 6. Deliverables Checklist

| Deliverable | File | Owner Phase |
|---|---|---|
| Source Code | Full repo | All phases |
| ML Model | `models/late_delivery_xgb.pkl` | Phase 6a |
| Data Pipeline | `pipeline/01_clean.py` → `03_features.py` | Phase 3–5 |
| Agent System | `agents/crew.py` + tools | Phase 6b |
| Backend API | `api/main.py` | Phase 10 |
| Chat UI | `chat_ui/streamlit_app.py` | Phase 10 |
| Dashboard | `dashboard/DatathonDashboard.pbix` | Phase 9 |
| Technical Docs | README + reports/*.md | All phases |
| Presentation | PPT from `reports/business_insights.md` | Phase 8–10 |
| Prediction Results | `reports/model_evaluation.md` | Phase 7 |

---

*Phase 2 locked: 2026-08-06 — answers: exclude cancelled orders, left join for reviews*
