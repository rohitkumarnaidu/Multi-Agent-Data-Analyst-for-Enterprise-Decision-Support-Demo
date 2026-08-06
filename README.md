# 🚀 Multi-Agent Data Analyst for Enterprise Decision Support

*A next-generation conversational AI dashboard that replaces static BI tools with an autonomous, reasoning team of AI Agents.*

---

## 🛑 The Problem
Enterprise executives and operators face a massive bottleneck when making data-driven decisions:
1. **Static Dashboards**: Tools like Power BI or Tableau only answer the questions they were explicitly designed to answer. If a manager asks a new question, they have to submit a ticket to the data engineering team and wait days.
2. **Data Silos**: Machine learning predictions (like our XGBoost model) live in a separate pipeline from the raw operational data (SQL warehouse), making it hard to bridge the gap between "What happened?" and "What will happen?"
3. **AI Hallucinations**: Standard ChatGPT interfaces cannot be trusted with enterprise data because they guess answers instead of running deterministic, auditable code.

---

## 💡 The Solution
We built a **Multi-Agent System powered by CrewAI** that acts as an entire data team in a box. 

Instead of a single monolithic prompt, the user interacts with an **Orchestrator Agent**. This orchestrator interprets the natural-language question and dynamically delegates sub-tasks to a highly specialized crew of AI agents. These agents don't guess—they write and execute live SQL against a DuckDB data warehouse, run live Machine Learning models, and generate real Python charts.

---

## ⚙️ How It Works (The Architecture)

Our system consists of 6 specialized roles:

1. 🧠 **Orchestrator Agent**: Parses the user's intent and plans the execution steps.
2. 🕵️ **Data Retrieval Agent**: Translates English into precise SQL queries and executes them against the local `DuckDB` warehouse to fetch raw operational data.
3. 🔮 **Predictive Agent**: Loads our pre-trained `XGBoost` model to actively score orders for "Late Delivery Risk" on the fly.
4. 🧮 **Analysis Agent**: Performs mathematical aggregations (Counts, Averages, Group Bys) on the retrieved data.
5. 📊 **Visualization Agent**: Writes Python code (`matplotlib`/`seaborn`) to dynamically generate beautiful charts based on the data.
6. ✍️ **Narrative Agent**: Interprets the mathematical results and the charts, translating them into a plain-English, business-friendly summary with actionable recommendations.

*(All of this is wrapped in a beautiful **Streamlit** Chat UI that non-technical users can interact with!)*

---

## 🛠️ The Technology Stack
* **Data Warehouse**: `DuckDB` (Blazing fast, zero-setup, embedded SQL analytics).
* **Machine Learning**: `XGBoost` & `SHAP` (For predicting late deliveries and explaining *why* they will be late).
* **Agent Framework**: `CrewAI` (For role-playing and task delegation).
* **LLM Engine**: `LiteLLM` (Allows us to seamlessly swap between local hardware models like Ollama/Llama3 and hosted models like GPT-4o-mini).
* **Frontend**: `Streamlit` (Interactive chat and dashboard UI).

---

## ✨ What It Can Do (Core Capabilities)

Our Multi-Agent system can autonomously answer complex enterprise questions such as:

* **"What is the average delivery time?"**
  *(Retrieval Agent writes SQL -> Analysis Agent averages the dates -> Visualization Agent draws a histogram -> Narrative Agent explains).*
* **"How many orders are late?"**
  *(Predictive Agent runs the XGBoost model -> Analysis Agent counts the flags).*
* **"Which seller has the most late deliveries?"**
  *(Retrieval Agent joins the Orders and Items tables -> Analysis Agent isolates the bad actors).*
* **"Which product category has the highest profit margin?"**
  *(Retrieval Agent queries the products table -> Analysis Agent computes freight-to-price ratios).*

### 🔍 Unprecedented Explainability
Unlike black-box AI tools, our system includes a **"View Agent Reasoning & Data Provenance"** feature. Users can click a button to see exactly which SQL query the Data Retrieval Agent ran, proving that the data is mathematically sound and not hallucinated.

---

## 📈 Business Impact & Insights Discovered (Olist E-Commerce)
By deploying this tool against the Olist E-Commerce dataset, our Agent Team instantly unlocked the following enterprise insights:
1. **The Seasonality Crash**: November (Black Friday) volume completely breaks the logistics network. *Action: Implement dynamic shipping estimates (+5 days) during peak holidays.*
2. **The "Maranhão Penalty"**: The Northern/Northeastern states suffer from a near 20% late delivery rate. *Action: Renegotiate regional carrier SLAs.*
3. **The Freight/Satisfaction Trap**: Customers who pay high shipping fees ($24+) and receive late items aggressively leave 1-star reviews. *Action: Trigger automated partial freight refunds for late premium shipments.*
4. **Payment Delays**: Long approval times for Boleto (invoice) payments eat directly into the seller's fulfillment window. *Action: Only start the delivery clock *after* payment clearance.*

---

## 🚀 Running the Hackathon Demo

To run the interactive Streamlit Chat UI on your local Windows machine:

1. Clone this repository.
2. Double-click the **`run_demo.bat`** file in the root directory.
3. Your browser will automatically open `http://localhost:8501`.
4. Ask the agents one of the 5 demo questions!

---

*This project was completed across 10 structured phases, from raw data ingestion and feature engineering to XGBoost training and Multi-Agent integration.*
