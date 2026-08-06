# Phase 5: Feature Engineering Summary

## Dataset Shape
- **Total Rows**: 96470
- **Train Split**: 77176 (80%)
- **Test Split**: 19294 (20%)
- **Number of Features**: 61

## Target Distribution (Stratified)
- **Train Late Rate**: 8.11%
- **Test Late Rate**: 8.11%

## Features Extracted
- **Temporal**: `est_delivery_days`, `order_to_approval_hrs`, `day_of_week_ordered`, `month_ordered`
- **Financial**: `total_price`, `total_freight`, `freight_to_price_ratio`, `total_payment`, `max_installments`, `paid_credit_card`, `paid_boleto`, `payment_types_count`
- **Product**: `item_count`
- **Geographic**: `is_interstate`, `customer_state_*` (OHE), `seller_state_*` (OHE)

## Leakage Prevention
No post-purchase data (actual delivery dates, review scores, delivery days) were included in the feature set. All features represent data known exactly at the moment the order is approved.

*Parquet files saved to `features/`.*
