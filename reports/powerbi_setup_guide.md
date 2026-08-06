# Phase 9: End-to-End Power BI Dashboard Construction Guide

This guide details exactly where to click, what fields to drag, and how to configure every single visual in Power BI Desktop to build the Multi-Agent Data Analyst dashboard.

## Part 1: Data Import & Modeling

1. **Launch Power BI Desktop**.
2. On the Home ribbon, click **Get Data** > **Text/CSV**.
3. Navigate to the `powerbi/` folder in your project directory and select `orders_master_export.csv`. Click **Load**.
4. Click **Get Data** > **Text/CSV** again and select `order_items_export.csv`. Click **Load**.
5. On the far left sidebar, click the **Model View** icon (it looks like three interconnected squares).
6. You will see both tables. Drag the `order_id` column from `order_items_export` and drop it directly on top of the `order_id` column in `orders_master_export`. 
7. A line should appear with a `*` on the items side and a `1` on the master side, indicating a successful Many-to-One relationship.

---

## Part 2: Page 1 - The Executive Overview

Click the **Report View** icon on the far left sidebar (it looks like a bar chart) to return to the blank canvas.

### Visual 1: Total Orders (KPI Card)
1. In the **Visualizations** pane on the right, click the **Card** visual icon (it has a '123' on it).
2. In the **Data** pane on the far right, expand `orders_master_export`.
3. Drag `order_id` into the **Fields** box in the Visualizations pane.
4. Click the small down arrow next to `order_id` in the Fields box and select **Count (Distinct)**.
5. *(Optional)*: In the Visualizations pane, click the **Format your visual** tab (paintbrush icon), go to Category Label, and rename it "Total Distinct Orders".

### Visual 2: Overall Late Rate (KPI Card)
1. Click empty space on the canvas to deselect the first card.
2. Click the **Card** visual icon again.
3. Drag `is_late` from `orders_master_export` into the Fields box.
4. Click the down arrow next to `is_late` and select **Average**.
5. Click the **Format your visual** tab (paintbrush icon) > **Callout value**. Change the display format to **Percentage** (or click the `%` icon in the Measure tools ribbon at the top).

### Visual 3: Average Freight Cost (KPI Card)
1. Click empty space on the canvas, then click the **Card** visual icon.
2. Drag `total_freight` from `orders_master_export` into the Fields box.
3. Click the down arrow and select **Average**.
4. Click the `$` icon in the Measure tools ribbon at the top to format as currency.

### Visual 4: The Geography Penalty (Map)
1. Click empty space on the canvas.
2. Click the **Map** visual icon (looks like a globe).
3. Drag `customer_state` into the **Location** field.
4. Drag `is_late` into the **Bubble size** field.
5. Click the down arrow next to `is_late` and select **Average**.
6. *Insight*: You will visually see massive bubbles over states like MA and AL, indicating severe logistical failures in the North/Northeast.

### Visual 5: The Seasonal Breaking Point (Line Chart)
1. Click empty space on the canvas.
2. Click the **Line Chart** visual icon.
3. Drag `month_ordered` to the **X-axis**. (Ensure it sorts properly from 1 to 12. If it sums them, click the down arrow and select "Don't summarize").
4. Drag `order_id` to the **Y-axis**, and set it to **Count (Distinct)**.
5. Drag `is_late` to the **Secondary Y-axis**, and set it to **Sum**.
6. *Insight*: This highlights the massive spike in both volume and late deliveries during Month 11 (Black Friday).

---

## Part 3: Page 2 - Logistics & ML Drill-Down

At the bottom left of the screen, click the **`+`** icon to add a new page (Page 2).

### Visual 1: The "Bad Actor" Sellers (Matrix)
1. Click the **Matrix** visual icon (looks like a blue table with bold headers).
2. Drag `seller_id` from the `order_items_export` table into the **Rows** field.
3. Drag `is_late` from `orders_master_export` into the **Values** field, and set it to **Average** (Format as Percentage).
4. Drag `order_id` into the **Values** field, and set it to **Count (Distinct)**.
5. Click the column header for your `is_late` average on the actual visual to sort it descending. This bubbles the worst-performing sellers to the top.

### Visual 2: Freight vs Satisfaction Trap (Scatter Plot)
1. Click empty space on the canvas.
2. Click the **Scatter chart** visual icon.
3. Drag `order_id` to the **Values** field.
4. Drag `total_freight` to the **X-axis** field (Set to **Average**).
5. Drag `review_score` to the **Y-axis** field (Set to **Average**).
6. *Insight*: Look for the cluster of 1-star reviews—they correlate heavily with higher average freight costs, proving that customers heavily penalize delays when they pay a premium for shipping.

### Visual 3: Payment Delay Impact (Column Chart)
1. Click empty space on the canvas.
2. Click the **Clustered Column Chart** visual icon.
3. Drag `order_to_approval_hrs` into the **X-axis** field. (If it has too many unique values, you may need to right-click the field in the Data pane and create a "New Group" to bin them into buckets of 12 hours).
4. Drag `is_late` into the **Y-axis** field (Set to **Average**).
5. *Insight*: This clearly demonstrates that as approval hours increase, the probability of the order being late skyrockets, eating into the seller's fulfillment window.
