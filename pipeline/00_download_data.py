"""
pipeline/00_download_data.py
============================
Phase 0 — Step 6: Download the Olist Brazilian E-Commerce dataset from Kaggle.

Usage:
    python pipeline/00_download_data.py

Requirements:
    - KAGGLE_USERNAME and KAGGLE_KEY set in .env  (OR kaggle.json in ~/.kaggle/)
    - `kaggle` package installed
"""

import os
import zipfile
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DATASET_SLUG = "olistbr/brazilian-ecommerce"
RAW_DIR      = Path(os.getenv("RAW_DATA_DIR", "./raw"))

EXPECTED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def setup_kaggle_auth():
    """Set KAGGLE_USERNAME and KAGGLE_KEY from .env if not already in env."""
    username = os.getenv("KAGGLE_USERNAME")
    key      = os.getenv("KAGGLE_KEY")
    if username and key:
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"]      = key
        logger.info(f"Kaggle auth set for user: {username}")
    else:
        logger.warning(
            "KAGGLE_USERNAME / KAGGLE_KEY not found in .env. "
            "Falling back to ~/.kaggle/kaggle.json if it exists."
        )


def download_dataset():
    """Download the Olist dataset zip into raw/ via the Kaggle CLI."""
    import kaggle  # imported here so auth env vars are set first

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading dataset '{DATASET_SLUG}' → {RAW_DIR} ...")
    kaggle.api.dataset_download_files(
        DATASET_SLUG,
        path=str(RAW_DIR),
        unzip=True,
        quiet=False,
    )
    logger.success("Download complete.")


def validate_files():
    """Check all expected CSV files are present."""
    missing = [f for f in EXPECTED_FILES if not (RAW_DIR / f).exists()]
    if missing:
        logger.error(f"Missing files: {missing}")
        raise FileNotFoundError(f"Missing Olist CSVs: {missing}")

    logger.success("All 9 Olist CSV files verified in raw/")
    for f in EXPECTED_FILES:
        path = RAW_DIR / f
        size_mb = path.stat().st_size / 1_048_576
        logger.info(f"  {f:<55} {size_mb:>6.1f} MB")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Phase 0 — Step 6: Kaggle Dataset Download")
    logger.info("=" * 60)

    setup_kaggle_auth()
    download_dataset()
    validate_files()

    logger.success("Dataset ready. Proceed to: python pipeline/00_init_duckdb.py")
