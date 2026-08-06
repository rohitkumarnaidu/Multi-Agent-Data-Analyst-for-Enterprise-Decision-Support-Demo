import duckdb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path

def main():
    print("--- Phase 5: Feature Engineering ---")
    
    # 1. Connect and Extract
    print("Extracting data from DuckDB...")
    con = duckdb.connect('data/olist.duckdb')
    
    # We only predict on orders that were actually delivered (to know the true late status)
    # We select ONLY pre-delivery features to avoid data leakage
    query = """
    SELECT 
        -- Target
        is_late,
        
        -- Engineered/Time Features
        DATE_DIFF('day', order_purchase_timestamp, order_estimated_delivery_date) AS est_delivery_days,
        day_of_week_ordered,
        month_ordered,
        order_to_approval_hrs,
        
        -- Monetary & Item Features
        total_price,
        total_freight,
        freight_to_price_ratio,
        item_count,
        total_payment,
        max_installments,
        payment_types_count,
        paid_credit_card,
        paid_boleto,
        
        -- Geographic Features
        customer_state,
        seller_state,
        same_state AS is_interstate_inverted
    FROM orders_master
    WHERE is_delivered = 1
    """
    df = con.execute(query).df()
    con.close()
    
    print(f"Loaded {len(df)} delivered orders.")
    
    # 2. Feature Creation & Cleaning
    print("Processing features...")
    # Convert 'same_state' to 'is_interstate'
    df['is_interstate'] = (df['is_interstate_inverted'] == 0).astype(int)
    df = df.drop(columns=['is_interstate_inverted'])
    
    # Handle missing values (e.g. order_to_approval_hrs could be null)
    # Median imputation for numerical
    num_cols = df.select_dtypes(include=['float64', 'int64', 'int32']).columns
    for col in num_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    
    # 3. Categorical Encoding (One-Hot)
    print("Encoding categorical features...")
    cat_cols = ['customer_state', 'seller_state']
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    # 4. Train / Test Split
    print("Splitting dataset (80/20 Stratified)...")
    X = df.drop(columns=['is_late'])
    y = df['is_late']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"  Train size: {len(X_train)} (Late rate: {y_train.mean()*100:.2f}%)")
    print(f"  Test size:  {len(X_test)} (Late rate: {y_test.mean()*100:.2f}%)")
    print(f"  Features:   {X_train.shape[1]}")
    
    # 5. Export
    print("Exporting to parquet...")
    Path('features').mkdir(exist_ok=True)
    
    X_train.to_parquet('features/X_train.parquet')
    X_test.to_parquet('features/X_test.parquet')
    # Save y as DataFrames for parquet export
    pd.DataFrame({'is_late': y_train}).to_parquet('features/y_train.parquet')
    pd.DataFrame({'is_late': y_test}).to_parquet('features/y_test.parquet')
    
    # Generate Report
    report = f"""# Phase 5: Feature Engineering Summary

## Dataset Shape
- **Total Rows**: {len(df)}
- **Train Split**: {len(X_train)} (80%)
- **Test Split**: {len(X_test)} (20%)
- **Number of Features**: {X_train.shape[1]}

## Target Distribution (Stratified)
- **Train Late Rate**: {y_train.mean()*100:.2f}%
- **Test Late Rate**: {y_test.mean()*100:.2f}%

## Features Extracted
- **Temporal**: `est_delivery_days`, `order_to_approval_hrs`, `day_of_week_ordered`, `month_ordered`
- **Financial**: `total_price`, `total_freight`, `freight_to_price_ratio`, `total_payment`, `max_installments`, `paid_credit_card`, `paid_boleto`, `payment_types_count`
- **Product**: `item_count`
- **Geographic**: `is_interstate`, `customer_state_*` (OHE), `seller_state_*` (OHE)

## Leakage Prevention
No post-purchase data (actual delivery dates, review scores, delivery days) were included in the feature set. All features represent data known exactly at the moment the order is approved.

*Parquet files saved to `features/`.*
"""
    with open('reports/phase5_features.md', 'w') as f:
        f.write(report)
        
    print("--- Phase 5 Complete ---")

if __name__ == "__main__":
    main()
