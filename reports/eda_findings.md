# Phase 4: Exploratory Data Analysis Findings

The following 5 findings were computed directly from `orders_master` using `notebooks/02_eda_rubric.py`. All 5 corresponding charts have been saved to `notebooks/eda_charts/`.

### 1. Delivery Time Distribution
- **Finding:** The average delivery time is **12.5 days**.
- **Code & Output:**
  ```python
  df_time = con.execute("""
      SELECT DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date) as delivery_days
      FROM orders_master
      WHERE is_delivered = 1 AND order_delivered_customer_date IS NOT NULL
  """).df()
  df_time = df_time[df_time['delivery_days'] >= 0]
  mean_days = df_time['delivery_days'].mean()
  print(f"FINDING 1: Average delivery time is {mean_days:.1f} days.")
  # OUTPUT: FINDING 1: Average delivery time is 12.5 days.
  ```

### 2. Geographic Late Delivery Risk
- **Finding:** The worst state for late deliveries is **MA (Maranhão)**, with a **19.7%** late delivery rate.
- **Code & Output:**
  ```python
  df_state = con.execute("""
      SELECT customer_state, COUNT(*) as total, AVG(CAST(is_late AS DOUBLE)) * 100 as late_pct
      FROM orders_master
      WHERE is_delivered = 1
      GROUP BY customer_state
      HAVING total > 500
      ORDER BY late_pct DESC
  """).df()
  worst_state = df_state.iloc[0]
  print(f"FINDING 2: Worst state for late deliveries is {worst_state['customer_state']} at {worst_state['late_pct']:.1f}%.")
  # OUTPUT: FINDING 2: Worst state for late deliveries is MA at 19.7%.
  ```

### 3. Payment Method Mix
- **Finding:** The top payment method is **credit_card**, used **76,795 times**.
- **Code & Output:**
  ```python
  df_pay = con.execute("""
      SELECT payment_type, COUNT(*) as cnt
      FROM raw_order_payments
      GROUP BY payment_type
      ORDER BY cnt DESC
  """).df()
  top_pay = df_pay.iloc[0]
  print(f"FINDING 3: Top payment method is {top_pay['payment_type']} used {top_pay['cnt']} times.")
  # OUTPUT: FINDING 3: Top payment method is credit_card used 76795 times.
  ```

### 4. Review Score Distribution
- **Finding:** 5-star reviews account for **57.8% (57,002)** of all 98,673 reviews.
- **Code & Output:**
  ```python
  df_rev = con.execute("""
      SELECT review_score, COUNT(*) as cnt
      FROM orders_master
      WHERE review_score IS NOT NULL
      GROUP BY review_score
      ORDER BY review_score
  """).df()
  five_stars = df_rev[df_rev['review_score'] == 5]['cnt'].values[0]
  total_rev = df_rev['cnt'].sum()
  print(f"FINDING 4: 5-star reviews account for {five_stars/total_rev*100:.1f}% ({five_stars}) of all {total_rev} reviews.")
  # OUTPUT: FINDING 4: 5-star reviews account for 57.8% (57002) of all 98673 reviews.
  ```

### 5. Freight Value vs. Review Score
- **Finding:** Customers who gave 1-star reviews paid on average **$24.48** in freight, compared to **$20.58** for 5-star reviews.
- **Code & Output:**
  ```python
  df_freight = con.execute("""
      SELECT review_score, total_freight
      FROM orders_master
      WHERE review_score IS NOT NULL AND total_freight < 100
  """).df()
  avg_f_1 = df_freight[df_freight['review_score'] == 1]['total_freight'].mean()
  avg_f_5 = df_freight[df_freight['review_score'] == 5]['total_freight'].mean()
  print(f"FINDING 5: Avg freight value for 1-star reviews is ${avg_f_1:.2f} vs ${avg_f_5:.2f} for 5-star reviews.")
  # OUTPUT: FINDING 5: Avg freight value for 1-star reviews is $24.48 vs $20.58 for 5-star reviews.
  ```
