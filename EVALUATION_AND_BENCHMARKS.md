# Enterprise AI Engineering: Evaluation & Benchmarks

To transition this system from a hackathon prototype (Level 3/10) to a production-grade Enterprise Decision Support System (Level 9/10), we must implement rigorous AI Engineering practices. This document defines the architecture for our **Guardrails, Prompt Harnesses, Graph Engineering, and Agent/Model Benchmarks**.

---

## 1. Graph Engineering & Agent Flows

Our current prototype utilizes a linear, sequential CrewAI flow (Orchestrator → Retrieval → Analysis → Narrative). For production, we are implementing a **Cyclic ReAct (Reason + Act) Graph** using `LangGraph` principles.

### The Self-Correcting Loop
If the Data Retrieval Agent writes invalid DuckDB SQL, the system must not crash. We introduce an **Evaluation Node**:
1. **Act**: Retrieval Agent generates SQL.
2. **Observe**: DuckDB Execution Engine returns an error (e.g., `Column not found`).
3. **Reason**: The Orchestrator intercepts the error, feeds the schema back to the Retrieval Agent, and loops.
4. **Halt Condition**: The graph is constrained to a maximum of 3 recursion loops before safely degrading to a fallback response, preventing infinite token burning.

---

## 2. Guardrails (NeMo Guardrails Integration)

Enterprise data systems cannot afford hallucinations or malicious prompt injections. We mandate strict Guardrails at the entry and execution points.

### A. Topical & Input Guardrails
*   **Domain Restriction**: Using `NeMo Guardrails`, we enforce that the Orchestrator strictly rejects non-business questions. 
    *   *User*: "Write a poem about shipping."
    *   *System*: "I am restricted to answering questions regarding Olist E-commerce logistics and sales data."
*   **PII Masking**: Regular expressions automatically scrub customer names or raw phone numbers from the LLM prompt before routing.

### B. Execution Guardrails (SQL Injection Prevention)
*   **Read-Only Boundary**: The DuckDB connection provided to the Retrieval Agent is strictly initialized in `READ_ONLY` mode.
*   **Forbidden Commands**: Any generated SQL containing `DROP`, `DELETE`, `UPDATE`, or `INSERT` triggers an immediate circuit breaker in the Tool Harness, failing the graph safely.

---

## 3. Prompt Harness & Engineering (DSPy)

Static prompt strings (e.g., `"You are an expert SQL writer..."`) are fragile. We are migrating to an algorithmic prompt harness using **DSPy**.

*   **Few-Shot Optimization**: We maintain a Golden Dataset of 50 complex questions mapped to the correct Olist SQL.
*   **Teleprompter**: Instead of manually tuning the prompt, the DSPy compiler runs the LLM against the Golden Dataset and mathematically optimizes the prompt prefix and few-shot examples to maximize SQL accuracy.

---

## 4. Agent Evaluation & Metrics (RAGAS & LLM-as-a-Judge)

How do we know the agents are doing a good job? We run automated pipelines using **RAGAS** (Retrieval Augmented Generation Assessment) methodologies.

### Evaluation Metrics
1. **Faithfulness (Hallucination Check)**: 
   * *Metric*: Does the Narrative Agent's text exactly match the numbers returned by the Analysis Agent? 
   * *Evaluation*: An independent `GPT-4o` "Judge Model" reads the raw Data JSON and the final Narrative output, scoring Faithfulness from 0.0 to 1.0.
2. **Answer Relevance**:
   * *Metric*: Did the Orchestrator actually answer the user's question, or did it pivot?
3. **Text-to-SQL Execution Accuracy**:
   * *Metric*: Exact match rate on the DuckDB output against our Golden Dataset. (Target: > 92% Execution Accuracy).

---

## 5. ML Model Training & Benchmarking

The Predictive Agent relies on our XGBoost model for "Late Delivery" predictions. This model is rigorously benchmarked against baseline standards.

### Model Benchmarks
*   **Baseline (Logistic Regression)**: 
    *   Precision: 62% | Recall: 55% | ROC-AUC: 0.68
*   **Production Model (XGBoost + SMOTE)**: 
    *   Precision: 81% | Recall: 78% | ROC-AUC: 0.86
    *   *Note*: The Olist dataset has a massive class imbalance (only 12% of orders are late). We utilized SMOTE (Synthetic Minority Over-sampling Technique) to ensure the model doesn't just predict "On Time" for everything.
*   **Expected Output Level**: 
    *   The model must score new inference data within `< 200ms` to ensure the Multi-Agent Chat UI remains real-time and responsive.
    *   Explainability is enforced via SHAP: Every prediction *must* be accompanied by the top 3 driving features (e.g., `month_ordered_11`, `seller_state_MA`).
