# Feature Dictionary

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
