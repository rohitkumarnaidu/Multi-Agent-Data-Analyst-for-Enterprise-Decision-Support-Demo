# Phase 9: Power BI Setup Guide

To create the final BI Dashboard for enterprise decision support, we have exported denormalized datasets from our DuckDB warehouse into standard CSVs.

## Data Source Files
Run `python pipeline/05_export_powerbi.py` to generate these files in the `powerbi/` directory:
1. `orders_master_export.csv`
2. `order_items_export.csv`
3. `model_features_export.csv`

## Power BI Integration Steps
1. Open Power BI Desktop.
2. Click **Get Data** > **Text/CSV**.
3. Import `orders_master_export.csv`.
4. Click **Get Data** > **Text/CSV**.
5. Import `order_items_export.csv`.
6. Open the **Model View** (relationship tab) on the left sidebar.
7. Drag a relationship line between `order_id` in the master table and `order_id` in the items table. (1-to-Many relationship).

## Recommended Visualizations to Build

### 1. The Executive Overview (Top Level)
- **KPI Cards**: Total Revenue, Total Orders, Average Delivery Days, Overall Late Delivery Rate (%).
- **Map Visual**: Plot `customer_state` against `is_late` to visualize the geographic penalty in the North/Northeast.

### 2. The Logistics & ML Drilldown
- **Line Chart**: Orders placed by `month_ordered` over time, overlaying the count of Late Deliveries. This clearly visualizes the Black Friday (November) failure point.
- **Bar Chart**: Late Delivery Rate by `seller_state`.
- **Scatter Plot**: `total_freight` on the X-axis, `review_score` on the Y-axis (to prove the insight that high freight costs paired with late deliveries destroy customer satisfaction).

### 3. Agent Integration
- Instead of using native Power BI Q&A, you can instruct executives to use our **Streamlit Chat UI** (`http://localhost:8501`) which sits on top of this exact same dataset but uses a sophisticated multi-agent pipeline capable of autonomous ML scoring!
