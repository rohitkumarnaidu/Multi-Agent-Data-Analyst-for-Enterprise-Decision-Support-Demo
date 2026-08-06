# PROJECT_STATE.md
> Living document — updated at the end of each phase.

---

## Project Summary

**Name:** Multi-Agent Data Analyst for Enterprise Decision Support
**Type:** Datathon / Hackathon Project
**Goal:** A system where business users type natural-language questions and a team of specialized AI agents — not one monolithic prompt — splits the work: one agent figures out what's being asked, one pulls the right data, one runs the numbers, one makes the chart, one explains it in plain English with a recommendation.

| Item | Detail |
|---|---|
| Dataset | Olist Brazilian E-Commerce (Kaggle, ~100k orders, 9 CSVs) |
| ML Target | Late Delivery Risk — binary classification (on-time vs late) |
| Storage | DuckDB (raw + clean + feature tables, zero-setup SQL) |
| Agent Framework | CrewAI (role-based, hybrid LLM strategy) |
| Dashboard | Power BI Desktop reading from exported CSV/Parquet snapshots |
| Backend | FastAPI |
| Chat UI | Streamlit |
| Language | Python 3.14 |

---

## Architecture

```
Business User
    │
    ▼
Streamlit Chat UI  ──►  FastAPI Backend
                              │
                              ▼
                    Orchestrator Agent  (GPT-4o-mini / Claude Haiku)
                    │ Parses intent, plans steps
                    ├──────────────────────┐
                    ▼                      ▼
         Data Retrieval Agent      Predictive Agent
         (Text-to-SQL / DuckDB)    (XGBoost late-delivery model)
                    │                      │
                    └──────────┬───────────┘
                               ▼
                        Analysis Agent
                        (stats, aggregations)
                        │              │
                        ▼              ▼
            Visualization Agent    Insight & Narrative Agent
            (matplotlib/plotly)    (plain-English summary)
                        │              │
                        └──────┬───────┘
                               ▼
                  Explainability / Validation Agent  ← BONUS
                  (checks narrative matches data)
                               │
                               ▼
                          Back to User
```

### Agent Roster

| Agent | Role | LLM Tier |
|---|---|---|
| **Orchestrator** | Parses user question, routes to correct agents | Strong (hosted) |
| **Data Retrieval** | Text-to-SQL over DuckDB, returns raw rows | Light (Ollama phi3:mini) |
| **Predictive** | Calls `late_delivery_xgb.pkl`, scores orders | Light (Ollama phi3:mini) |
| **Analysis** | Aggregates / summarizes retrieved data | Light (Ollama phi3:mini) |
| **Visualization** | Picks chart type, generates it | Light (Ollama phi3:mini) |
| **Insight & Narrative** | Turns numbers into business-readable answer | Strong (hosted) |
| **Explainability/Validation** *(bonus)* | Cross-checks narrative vs retrieved data | Strong (hosted) |

### Dataset — Olist Brazilian E-Commerce

| File | Domain |
|---|---|
| `olist_orders_dataset.csv` | Sales / Operations |
| `olist_order_items_dataset.csv` | Sales |
| `olist_order_payments_dataset.csv` | Finance |
| `olist_order_reviews_dataset.csv` | Customer Service |
| `olist_customers_dataset.csv` | Sales / CRM |
| `olist_sellers_dataset.csv` | Operations |
| `olist_products_dataset.csv` | Operations / Sales |
| `olist_geolocation_dataset.csv` | Operations (logistics) |
| `product_category_name_translation.csv` | Utility |

### Storage Layout

```
data/olist.duckdb
  ├── raw_*          ← loaded directly from CSVs (Phase 0)
  ├── clean_*        ← cleaned tables (Phase 3)
  └── feat_*         ← ML features (Phase 5)
```

---

## Phase Log

| Phase | Description | Status | Date | Notes |
|---|---|---|---|---|
| 0 | Project setup, env, dataset download, DuckDB init | ✅ Done | 2026-08-06 | Python 3.14, crewai 0.11.2 |
| 1 | Dataset release & raw data verification | 🔜 Pending | — | — |
| 2 | Problem understanding & scope definition | 🔜 Pending | — | — |
| 3 | Data cleaning | 🔜 Pending | — | — |
| 4 | Exploratory Data Analysis (EDA) | 🔜 Pending | — | — |
| 5 | Feature engineering | 🔜 Pending | — | — |
| 6a | ML model training (XGBoost late delivery) | 🔜 Pending | — | — |
| 6b | Agent system build (CrewAI crew) | 🔜 Pending | — | — |
| 7 | Model evaluation + SHAP | 🔜 Pending | — | — |
| 8 | Business insights report | 🔜 Pending | — | — |
| 9 | Power BI dashboard | 🔜 Pending | — | — |
| 10 | Integration + demo prep | 🔜 Pending | — | — |

---

## Known Issues

| # | Issue | Impact | Resolution |
|---|---|---|---|
| 1 | `crewai` latest stable version (0.11.2) available for Python 3.14 — newer versions cap at `<3.14` | Agent features limited to crewai 0.11.2 API | Monitor crewai releases; upgrade when Python 3.14 wheels land |
| 2 | `shap` install pending — depends on numpy resolution with crewai's langchain dep | SHAP not yet installed | Install separately after crewai resolves numpy<2 |

---

*Last updated: 2026-08-06 — Phase 0*
