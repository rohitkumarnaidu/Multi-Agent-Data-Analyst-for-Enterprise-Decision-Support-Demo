# Phase 1 — Raw Data Profile

*Generated: 2026-08-06 12:26*

## Table Shapes

| Table | Rows | Cols | PK Dupes | High-Null Columns |
|---|---|---|---|---|
| `raw_orders` | 99,441 | 8 | 0 | None |
| `raw_order_items` | 112,650 | 7 | N/A | None |
| `raw_order_payments` | 103,886 | 5 | N/A | None |
| `raw_order_reviews` | 99,224 | 7 | 789 | review_comment_title: 88.3%, review_comment_message: 58.7% |
| `raw_customers` | 99,441 | 5 | 0 | None |
| `raw_sellers` | 3,095 | 4 | 0 | None |
| `raw_products` | 32,951 | 9 | 0 | None |
| `raw_geolocation` | 1,000,163 | 5 | N/A | None |
| `raw_category_translation` | 71 | 2 | 0 | None |

## Date Range

- Orders span: **2016-09-04** → **2018-10-17**

## Join Coverage

| Join | Left Keys | Matched | Coverage | Status |
|---|---|---|---|---|
| Orders → Items | 99,441 | 98,666 | 99.2% | ✅ |
| Orders → Payments | 99,441 | 99,440 | 100.0% | ✅ |
| Orders → Reviews | 99,441 | 98,673 | 99.2% | ✅ |
| Orders → Customers | 99,441 | 99,441 | 100.0% | ✅ |
| Items → Sellers | 3,095 | 3,095 | 100.0% | ✅ |
| Items → Products | 32,951 | 32,951 | 100.0% | ✅ |

## Observations

- `order_delivered_customer_date` has nulls for cancelled/undelivered orders — expected
- `review_comment_title` and `review_comment_message` are mostly null — optional fields
- `product_category_name` has small null% — will fill via translation join in Phase 3
- `product_weight_g` and dimensions have small null% — will fill with category median in Phase 3
- Geolocation has duplicates per zip (multiple coordinates) — will average in Phase 3