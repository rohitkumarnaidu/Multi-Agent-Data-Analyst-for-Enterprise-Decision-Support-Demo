import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

def main():
    print("--- Phase 5: Build Model Features ---")
    
    con = duckdb.connect('data/olist.duckdb')
    
    # 1. SQL to extract features with no data leakage
    # We use window functions to calculate the seller's historical late rate
    # strictly from orders prior to the current order's purchase timestamp.
    query = """
    WITH order_seller AS (
        -- Get the primary seller and product per order to maintain 1-row-per-order
        SELECT order_id, MIN(seller_id) as seller_id, MIN(product_id) as product_id
        FROM clean_order_items
        GROUP BY order_id
    ),
    seller_history AS (
        -- Calculate running totals for each seller over time (excluding current row)
        SELECT 
            o.order_id,
            o.order_purchase_timestamp,
            os.seller_id,
            o.is_late,
            SUM(o.is_late) OVER (
                PARTITION BY os.seller_id 
                ORDER BY o.order_purchase_timestamp
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS prior_late_orders,
            COUNT(o.order_id) OVER (
                PARTITION BY os.seller_id 
                ORDER BY o.order_purchase_timestamp
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS prior_total_orders
        FROM orders_master o
        JOIN order_seller os ON o.order_id = os.order_id
        WHERE o.is_delivered = 1
    )
    SELECT 
        o.order_id,
        o.is_late,
        o.customer_state,
        o.seller_state,
        p.product_weight_g,
        p.product_volume_cm3,
        o.total_freight AS freight_value,
        o.total_price AS price,
        o.freight_to_price_ratio,
        o.order_to_approval_hrs,
        o.day_of_week_ordered,
        o.month_ordered,
        COALESCE(sh.prior_late_orders / NULLIF(sh.prior_total_orders, 0), 0.0) AS seller_recent_late_rate
    FROM orders_master o
    JOIN order_seller os ON o.order_id = os.order_id
    JOIN clean_products p ON os.product_id = p.product_id
    JOIN seller_history sh ON o.order_id = sh.order_id
    WHERE o.is_delivered = 1
      AND o.order_estimated_delivery_date IS NOT NULL
    """
    
    df = con.execute(query).df()
    con.close()
    
    # 2. Impute NaNs for numerical features
    num_cols = df.select_dtypes(include=[np.number]).columns.drop('is_late', errors='ignore')
    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
            
    # 3. Print Leakage & Audit Stats
    print("\n[AUDIT] Target Class Balance:")
    late_pct = df['is_late'].mean() * 100
    print(f"Total Rows: {len(df)}")
    print(f"Late: {df['is_late'].sum()} ({late_pct:.2f}%) | On-Time: {len(df) - df['is_late'].sum()} ({100 - late_pct:.2f}%)")
    
    print("\n[AUDIT] NaN Check:")
    print(df.isnull().sum())
    
    # Show example of seller history calculation for a specific seller
    print("\n[AUDIT] Seller History Check (Spot Check):")
    spot_check = df[['order_id', 'seller_recent_late_rate', 'is_late']].sample(2, random_state=42)
    print(spot_check)
    
    # 4. Export Parquet
    out_dir = Path('features')
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'model_features.parquet'
    df.to_parquet(out_path, index=False)
    print(f"\nSaved features to {out_path}")
    
    # 5. Write Feature Dictionary
    dict_content = """# Feature Dictionary

| Column Name | Description | Source / Derivation |
|---|---|---|
| `order_id` | Unique identifier for the order | `orders_master` |
| `is_late` | Target Variable (1 = Delivered after estimated date, 0 = On time) | `orders_master` |
| `customer_state` | State of the customer | `orders_master` |
| `seller_state` | State of the seller | `orders_master` |
| `product_weight_g` | Weight of the primary product in the order (grams) | `clean_products` |
| `product_volume_cm3` | Volume of the primary product (cm3) | `clean_products` |
| `freight_value` | Total freight paid for the order | `orders_master` |
| `price` | Total price of the items in the order | `orders_master` |
| `freight_to_price_ratio` | `freight_value` / `price` | `orders_master` |
| `order_to_approval_hrs` | Hours between order placement and payment approval | `orders_master` |
| `day_of_week_ordered` | Day of week order was placed (0=Monday, 6=Sunday) | `orders_master` |
| `month_ordered` | Month order was placed (1-12) | `orders_master` |
| `seller_recent_late_rate` | Historical late delivery rate of the seller, computed ONLY using orders placed prior to the current order | Computed via Window Function |

## Leakage Check
No features in this dataset depend on post-purchase information (like actual delivery date or review scores). All features are strictly knowable at or slightly after the time of payment approval, well before delivery occurs. Never-delivered (cancelled) orders are completely excluded from this dataset via the `WHERE is_delivered = 1` clause.
"""
    with open('features/feature_dictionary.md', 'w') as f:
        f.write(dict_content)
    print("Saved features/feature_dictionary.md")

if __name__ == "__main__":
    main()
