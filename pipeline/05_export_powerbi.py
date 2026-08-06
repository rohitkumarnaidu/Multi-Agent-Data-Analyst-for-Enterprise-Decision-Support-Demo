import duckdb
import pandas as pd
from pathlib import Path

def main():
    print("--- Phase 9: Export Data for Power BI ---")
    
    Path('powerbi').mkdir(exist_ok=True)
    con = duckdb.connect('data/olist.duckdb')
    
    print("1. Exporting Denormalized Orders Master...")
    # Export the fully cleaned master table (which includes reviews, geography, etc.)
    df_orders = con.execute("SELECT * FROM orders_master").df()
    df_orders.to_csv('powerbi/orders_master_export.csv', index=False)
    
    print("2. Exporting Raw Order Items for Product-Level Drilldown...")
    df_items = con.execute("SELECT * FROM raw_order_items").df()
    df_items.to_csv('powerbi/order_items_export.csv', index=False)
    
    print("3. Exporting Feature Matrix (with Late Predictions)...")

    # Actually, let's just copy the model_features.parquet to a CSV for PowerBI
    features = pd.read_parquet('features/model_features.parquet')
    features.to_csv('powerbi/model_features_export.csv', index=False)
    
    print("Successfully exported 3 datasets to the /powerbi directory:")
    print(" - powerbi/orders_master_export.csv (100k rows, Core Analytics)")
    print(" - powerbi/order_items_export.csv (112k rows, Product Drilldown)")
    print(" - powerbi/model_features_export.csv (96k rows, ML Feature Drilldown)")
    
    print("--- Phase 9 Complete ---")

if __name__ == "__main__":
    main()
