import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Setup
sns.set_theme(style="whitegrid")
con = duckdb.connect('data/olist.duckdb')
out_dir = 'notebooks/eda_charts'

print("--- EDA SCRIPT START ---")

# 1. Delivery time distribution (histogram)
df_time = con.execute("""
    SELECT DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date) as delivery_days
    FROM orders_master
    WHERE is_delivered = 1 AND order_delivered_customer_date IS NOT NULL
""").df()
df_time = df_time[df_time['delivery_days'] >= 0] # clean bad dates
plt.figure(figsize=(10,6))
sns.histplot(df_time['delivery_days'], bins=50, kde=True)
plt.xlim(0, 60)
plt.title('Delivery Time Distribution (Days)')
plt.savefig(f"{out_dir}/1_delivery_time_dist.png")
plt.close()
mean_days = df_time['delivery_days'].mean()
print(f"FINDING 1: Average delivery time is {mean_days:.1f} days.")

# 2. Late-delivery rate by customer state (bar chart)
df_state = con.execute("""
    SELECT customer_state, COUNT(*) as total, AVG(CAST(is_late AS DOUBLE)) * 100 as late_pct
    FROM orders_master
    WHERE is_delivered = 1
    GROUP BY customer_state
    HAVING total > 500
    ORDER BY late_pct DESC
""").df()
plt.figure(figsize=(12,6))
sns.barplot(data=df_state, x='customer_state', y='late_pct')
plt.title('Late Delivery Rate by State')
plt.savefig(f"{out_dir}/2_late_by_state.png")
plt.close()
worst_state = df_state.iloc[0]
print(f"FINDING 2: Worst state for late deliveries is {worst_state['customer_state']} at {worst_state['late_pct']:.1f}%.")

# 3. Payment method mix (bar/pie chart)
df_pay = con.execute("""
    SELECT payment_type, COUNT(*) as cnt
    FROM raw_order_payments
    GROUP BY payment_type
    ORDER BY cnt DESC
""").df()
plt.figure(figsize=(8,8))
plt.pie(df_pay['cnt'], labels=df_pay['payment_type'], autopct='%1.1f%%')
plt.title('Payment Method Mix')
plt.savefig(f"{out_dir}/3_payment_mix.png")
plt.close()
top_pay = df_pay.iloc[0]
print(f"FINDING 3: Top payment method is {top_pay['payment_type']} used {top_pay['cnt']} times.")

# 4. Review score distribution (bar chart)
df_rev = con.execute("""
    SELECT review_score, COUNT(*) as cnt
    FROM orders_master
    WHERE review_score IS NOT NULL
    GROUP BY review_score
    ORDER BY review_score
""").df()
plt.figure(figsize=(8,6))
sns.barplot(data=df_rev, x='review_score', y='cnt')
plt.title('Review Score Distribution')
plt.savefig(f"{out_dir}/4_review_dist.png")
plt.close()
five_stars = df_rev[df_rev['review_score'] == 5]['cnt'].values[0]
total_rev = df_rev['cnt'].sum()
print(f"FINDING 4: 5-star reviews account for {five_stars/total_rev*100:.1f}% ({five_stars}) of all {total_rev} reviews.")

# 5. Freight value vs review score (box plot)
df_freight = con.execute("""
    SELECT review_score, total_freight
    FROM orders_master
    WHERE review_score IS NOT NULL AND total_freight < 100
""").df()
plt.figure(figsize=(10,6))
sns.boxplot(data=df_freight, x='review_score', y='total_freight')
plt.title('Freight Value vs Review Score')
plt.savefig(f"{out_dir}/5_freight_vs_review.png")
plt.close()
avg_f_1 = df_freight[df_freight['review_score'] == 1]['total_freight'].mean()
avg_f_5 = df_freight[df_freight['review_score'] == 5]['total_freight'].mean()
print(f"FINDING 5: Avg freight value for 1-star reviews is ${avg_f_1:.2f} vs ${avg_f_5:.2f} for 5-star reviews.")

con.close()
print("--- EDA SCRIPT COMPLETE ---")
