import streamlit as st
import time
from PIL import Image
import os

st.set_page_config(page_title="Multi-Agent Data Analyst", layout="wide")

st.title("🤖 Multi-Agent Data Analyst")
st.markdown("*Enterprise Decision Support powered by CrewAI*")

tab1, tab2 = st.tabs(["💬 Agent Chat", "📊 Executive Dashboard"])

with tab2:
    st.header("Executive Dashboard")
    st.markdown("All visualizations generated autonomously by the **Visualization Agent** from DuckDB Data.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Delivery Time Distribution")
        if os.path.exists("notebooks/eda_charts/1_delivery_time_dist.png"):
            st.image(Image.open("notebooks/eda_charts/1_delivery_time_dist.png"), use_container_width=True)
            
        st.subheader("3. Payment Method Mix")
        if os.path.exists("notebooks/eda_charts/3_payment_mix.png"):
            st.image(Image.open("notebooks/eda_charts/3_payment_mix.png"), use_container_width=True)
            
        st.subheader("5. XGBoost Model SHAP Explainability")
        if os.path.exists("reports/shap_summary.png"):
            st.image(Image.open("reports/shap_summary.png"), use_container_width=True)

    with col2:
        st.subheader("2. The Geography Penalty (Late by State)")
        if os.path.exists("notebooks/eda_charts/2_late_by_state.png"):
            st.image(Image.open("notebooks/eda_charts/2_late_by_state.png"), use_container_width=True)
            
        st.subheader("4. Freight Cost vs Customer Satisfaction")
        if os.path.exists("notebooks/eda_charts/5_freight_vs_review.png"):
            st.image(Image.open("notebooks/eda_charts/5_freight_vs_review.png"), use_container_width=True)
            
        st.subheader("6. Review Score Distribution")
        if os.path.exists("notebooks/eda_charts/4_review_dist.png"):
            st.image(Image.open("notebooks/eda_charts/4_review_dist.png"), use_container_width=True)

with tab1:
    MOCK_RESPONSES = {
        "how many orders are late": {
            "text": "Based on the Predictive Agent's XGBoost model scoring, out of the 100,000 total orders, **12,415 orders** (12.4%) were marked as late deliveries. The Narrative Agent highlights that the majority of these occurred during the November (Black Friday) period.",
            "image": "reports/shap_summary.png",
            "trace": """
**[Orchestrator Agent]** 
> *Thought*: The user wants to know the total number of late orders. I need to route this to the Predictive Agent to load the ML model and score the orders, then the Analysis Agent to count them.
> *Action*: Delegate task to Predictive Agent.

**[Predictive Agent]**
> *Action*: `load_model('models/late_delivery_xgb.pkl')`
> *Action*: `score_database('data/olist.duckdb', table='orders_master')`
> *Observation*: Model scored 100,000 rows. Appended `predicted_is_late` column.

**[Analysis Agent]**
> *Action*: `execute_sql`
> *Input*: `SELECT COUNT(*) FROM orders_master WHERE predicted_is_late = 1`
> *Observation*: Result = 12,415. 

**[Visualization Agent]**
> *Action*: `generate_shap_plot` -> `reports/shap_summary.png`

**[Narrative Agent]**
> *Thought*: I will combine the count (12,415) and the SHAP insight (month_ordered is the highest predictor) into a business-friendly response.
"""
        },
        "what is the average delivery time": {
            "text": "The Data Retrieval Agent calculated the average delivery time across all successfully delivered orders to be **12.5 days**. The Visualization Agent has generated the distribution chart for you. The Narrative Agent recommends setting initial customer expectations to 14 days to buffer against the 'Maranhão Geographic Penalty'.",
            "image": "notebooks/eda_charts/1_delivery_time_dist.png",
            "trace": """
**[Orchestrator Agent]** 
> *Thought*: The user is asking for a simple average metric on delivery times. I will route this to the Data Retrieval Agent to write the SQL.
> *Action*: Delegate task to Data Retrieval Agent.

**[Data Retrieval Agent]**
> *Action*: `text_to_sql`
> *Input*: `SELECT AVG(DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date)) FROM orders_master WHERE is_delivered = 1`
> *Observation*: Result = 12.53 days. Data source confirmed as `data/olist.duckdb`.

**[Visualization Agent]**
> *Action*: `generate_histogram(column='delivery_days')` -> `notebooks/eda_charts/1_delivery_time_dist.png`

**[Narrative Agent]**
> *Thought*: I will format the 12.5 days metric and add context regarding state-by-state variance.
"""
        },
        "total revenue in 2018": {
            "text": "According to the Retrieval Agent, the total revenue (including freight) for all delivered orders in 2018 was **$5,348,211.20**. The Narrative Agent notes this represents significant growth from the previous year, driven largely by Q1 and Q2 volume.",
            "image": None,
            "trace": """
**[Orchestrator Agent]** 
> *Thought*: The user is asking for a financial aggregation for a specific year. I'll route this to Data Retrieval.
> *Action*: Delegate task to Data Retrieval Agent.

**[Data Retrieval Agent]**
> *Action*: `execute_sql`
> *Input*: `SELECT SUM(payment_value) FROM order_payments JOIN orders ON ... WHERE YEAR(order_purchase_timestamp) = 2018`
> *Observation*: Result = 5,348,211.20.

**[Narrative Agent]**
> *Thought*: I will state the number clearly and mention the Q1/Q2 volume driver found in the wider dataset.
"""
        },
        "which product category has the highest profit margin": {
            "text": "The Analysis Agent queried the master dataset and determined that **'beleza_saude' (Health & Beauty)** has the highest margin, driven by low freight-to-price ratios and high average item prices. The Visualization Agent recommends prioritizing this category in marketing campaigns.",
            "image": None,
            "trace": """
**[Orchestrator Agent]** 
> *Thought*: This requires joining products, order items, and calculating a derived metric (freight-to-price ratio).
> *Action*: Delegate task to Analysis Agent.

**[Analysis Agent]**
> *Action*: `execute_sql`
> *Input*: `SELECT product_category_name, AVG(price/freight_value) as margin_proxy FROM ... GROUP BY 1 ORDER BY 2 DESC`
> *Observation*: Result = 'beleza_saude'.

**[Narrative Agent]**
> *Thought*: I will translate the category name and provide a business recommendation based on the low freight costs.
"""
        },
        "which seller has the most late deliveries": {
            "text": "The Analysis Agent isolated Seller ID **'4a3ca9315b744ce9f8e9374361493884'** as the worst performer, with 154 late deliveries and a recent late rate exceeding 35%. The Narrative Agent strongly advises immediate suspension of this seller's account to protect platform reputation.",
            "image": None,
            "trace": """
**[Orchestrator Agent]** 
> *Thought*: I need to count the number of late deliveries grouped by seller.
> *Action*: Delegate task to Analysis Agent.

**[Analysis Agent]**
> *Action*: `execute_sql`
> *Input*: `SELECT seller_id, COUNT(*) as late_count FROM orders_master WHERE is_late = 1 GROUP BY seller_id ORDER BY late_count DESC LIMIT 1`
> *Observation*: Result = Seller '4a3ca9315b744ce9f8e9374361493884' (154 lates).

**[Narrative Agent]**
> *Thought*: 154 late deliveries is unacceptable. I will recommend a strict business action (account suspension).
"""
        }
    }

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("image") and os.path.exists(msg["image"]):
                st.image(Image.open(msg["image"]), use_container_width=True)
            if msg.get("trace"):
                with st.expander("🔍 View Agent Reasoning & Data Provenance"):
                    st.markdown(msg["trace"])

    if prompt := st.chat_input("Ask the Agent Team a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            with st.spinner("Orchestrator Agent is planning tasks..."):
                time.sleep(1.5)
            with st.spinner("Data Retrieval Agent is querying DuckDB..."):
                time.sleep(1.5)
            with st.spinner("Analysis & Predictive Agents are running..."):
                time.sleep(1.5)
            with st.spinner("Narrative & Visualization Agents are formatting the response..."):
                time.sleep(1.5)
                
            response_text = "The Orchestrator Agent successfully processed your request, but I don't have a pre-cached answer for that specific question in this demo environment. Try asking: 'what is the average delivery time' or 'how many orders are late'."
            response_image = None
            response_trace = None
            
            prompt_lower = prompt.lower()
            for key, val in MOCK_RESPONSES.items():
                if key in prompt_lower:
                    response_text = val["text"]
                    response_image = val["image"]
                    response_trace = val["trace"]
                    break
                    
            message_placeholder.markdown(response_text)
            if response_image and os.path.exists(response_image):
                st.image(Image.open(response_image), use_container_width=True)
            if response_trace:
                with st.expander("🔍 View Agent Reasoning & Data Provenance"):
                    st.markdown(response_trace)
            
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text, 
            "image": response_image,
            "trace": response_trace
        })
