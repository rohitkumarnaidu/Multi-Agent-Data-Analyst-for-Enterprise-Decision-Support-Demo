# Phase 3 — Data Cleaning Summary

*Generated: 2026-08-06 12:34*

## Output Tables

| Table | Rows | Status |
|---|---|---|
| `clean_orders` | 99,441 | ✅ |
| `clean_order_items` | 112,650 | ✅ |
| `clean_payments` | 99,440 | ✅ |
| `clean_reviews` | 99,224 | ✅ |
| `clean_customers` | 99,441 | ✅ |
| `clean_sellers` | 3,095 | ✅ |
| `clean_products` | 32,951 | ✅ |
| `clean_geolocation` | 19,015 | ✅ |
| `orders_master` | 99,441 | ✅ |

## Key Stats
- **Late delivery rate** (delivered orders only): `8.11%`
- **orders_master** is the primary table for EDA + ML training

## Cleaning Actions Applied
- All date columns cast from STRING → TIMESTAMP
- `is_late` binary label derived from delivered vs estimated dates
- `is_delivered` flag added (excludes cancelled/unavailable orders from label)
- `delivery_days` and `order_to_approval_hrs` computed
- `freight_to_price_ratio` computed per order
- `same_state` flag (customer state == seller state) added
- Product nulls (weight, volume) filled with category median
- Geolocation deduplicated: one avg lat/lng per zip code
- Product category joined with English translation
- Payments aggregated per order (total, installments, payment type)
- Reviews aggregated per order (latest review per order)

## Null Status (ML-relevant columns in orders_master)
- `is_late`: 0 nulls for delivered orders ✅
- `freight_to_price_ratio`: 0 nulls ✅
- `order_to_approval_hrs`: may have minor nulls for old records
- `review_score`: ~15% null (left join — not all orders reviewed) ✅ expected