# Multi-Agent Data Analyst for Enterprise Decision Support

> A Datathon project: AI-powered multi-agent analytics system where business users ask natural-language questions and get data-driven answers — automatically.

---

## Architecture

```
Business User → Streamlit Chat UI → FastAPI Backend
                                          ↓
                               Orchestrator Agent (GPT-4o-mini)
                              ↙            ↘
             Data Retrieval Agent     Predictive Agent
             (text-to-SQL / DuckDB)   (XGBoost late-delivery model)
                        ↓                   ↓
                   Analysis Agent ←─────────┘
                   ↙           ↘
     Visualization Agent    Insight & Narrative Agent
             ↘                   ↙
        Explainability / Validation Agent
                    ↓
              Back to User
```

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent Framework | CrewAI |
| LLM (strong) | OpenAI `gpt-4o-mini` / Anthropic Claude Haiku |
| LLM (local) | Ollama `phi3:mini` (runs on RTX 3050 6GB) |
| Dataset | Olist Brazilian E-Commerce (Kaggle) |
| Database | DuckDB |
| ML Model | XGBoost (late delivery risk classifier) |
| Explainability | SHAP |
| Backend | FastAPI |
| Chat UI | Streamlit |
| Dashboard | Power BI Desktop |
| Language | Python 3.11+ |

---

## Dataset

**Olist Brazilian E-Commerce** — 9 CSVs, ~100k real orders (2016–2018)

Download: [kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## Setup

### 1. Clone

```bash
git clone https://github.com/rohitkumarnaidu/Multi-Agent-Data-Analyst-for-Enterprise-Decision-Support-Demo.git
cd Multi-Agent-Data-Analyst-for-Enterprise-Decision-Support-Demo
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
copy .env.example .env
# Edit .env and fill in your API keys
```

### 4. Download Dataset

```bash
# Option A: Via script (requires Kaggle API key in .env)
python pipeline/00_download_data.py

# Option B: Manual download
# Download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Unzip all CSVs into the raw/ folder
```

### 5. Initialize DuckDB

```bash
python pipeline/00_init_duckdb.py
```

### 6. Validate Phase 0

```bash
python pipeline/00_validate_setup.py
```

---

## Project Structure

```
├── raw/                     # Olist CSVs (git-ignored)
├── clean/                   # Cleaned parquet tables (git-ignored)
├── features/                # ML feature tables (git-ignored)
├── models/                  # Trained .pkl models (git-ignored)
├── data/                    # DuckDB file (git-ignored)
├── pipeline/                # Data pipeline scripts (Phase 1–6)
├── agents/                  # CrewAI crew + tools
├── api/                     # FastAPI backend
├── chat_ui/                 # Streamlit chat UI
├── dashboard/               # Power BI + exported data
├── notebooks/               # EDA notebook
├── reports/                 # Evaluation + business insights
└── docs/                    # Build plan + architecture
```

---

## Deliverables

- [x] Source Code (full repo)
- [ ] ML Model — `late_delivery_xgb.pkl`
- [ ] Data Preprocessing Pipeline — `pipeline/01_clean.py` → `03_features.py`
- [ ] Dashboard — `dashboard/DatathonDashboard.pbix`
- [ ] Technical Documentation
- [ ] Presentation (PPT)
- [ ] Prediction Results

---

## Build Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Environment Setup & Dataset Download | ✅ Done |
| 1 | Dataset Release & Raw Data Verification | 🔜 |
| 2 | Problem Understanding & Scope Definition | 🔜 |
| 3 | Data Cleaning | 🔜 |
| 4 | Exploratory Data Analysis | 🔜 |
| 5 | Feature Engineering | 🔜 |
| 6a | ML Model Training | 🔜 |
| 6b | Agent System Build | 🔜 |
| 7 | Model Evaluation + SHAP | 🔜 |
| 8 | Business Insights | 🔜 |
| 9 | Power BI Dashboard | 🔜 |
| 10 | Integration + Demo Prep | 🔜 |
