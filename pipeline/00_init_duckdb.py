# -*- coding: utf-8 -*-
import os, sys
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
"""
pipeline/00_init_duckdb.py
==========================
Phase 0 — Step 7: Load all 9 Olist raw CSVs into DuckDB.

Creates the database at ./data/olist.duckdb with raw_* tables.

Usage:
    python pipeline/00_init_duckdb.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import duckdb
from loguru import logger
from rich.console import Console
from rich.table import Table

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", "./data/olist.duckdb"))
RAW_DIR     = Path(os.getenv("RAW_DATA_DIR", "./raw"))

# Maps: DuckDB table name → CSV filename
RAW_TABLE_MAP = {
    "raw_orders":              "olist_orders_dataset.csv",
    "raw_order_items":         "olist_order_items_dataset.csv",
    "raw_order_payments":      "olist_order_payments_dataset.csv",
    "raw_order_reviews":       "olist_order_reviews_dataset.csv",
    "raw_customers":           "olist_customers_dataset.csv",
    "raw_sellers":             "olist_sellers_dataset.csv",
    "raw_products":            "olist_products_dataset.csv",
    "raw_geolocation":         "olist_geolocation_dataset.csv",
    "raw_category_translation":"product_category_name_translation.csv",
}

# Expected minimum row counts for basic sanity
MIN_ROW_COUNTS = {
    "raw_orders":               90_000,
    "raw_order_items":         100_000,
    "raw_order_payments":       90_000,
    "raw_order_reviews":        90_000,
    "raw_customers":            90_000,
    "raw_sellers":               3_000,
    "raw_products":             30_000,
    "raw_geolocation":         900_000,
    "raw_category_translation":     50,
}

console = Console()


# ── Main ──────────────────────────────────────────────────────────────────────

def init_duckdb():
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))
    logger.info(f"DuckDB connected: {DUCKDB_PATH}")
    return con


def load_tables(con: duckdb.DuckDBPyConnection):
    results = []
    for table_name, csv_file in RAW_TABLE_MAP.items():
        csv_path = RAW_DIR / csv_file
        if not csv_path.exists():
            logger.error(f"CSV not found: {csv_path}  — Run 00_download_data.py first.")
            raise FileNotFoundError(csv_path)

        logger.info(f"Loading {csv_file} → {table_name} ...")
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=True)
        """)

        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        col_count = len(con.execute(f"DESCRIBE {table_name}").fetchall())
        size_mb   = csv_path.stat().st_size / 1_048_576

        ok = row_count >= MIN_ROW_COUNTS.get(table_name, 0)
        status = "[OK]" if ok else "[WARN]"
        results.append((status, table_name, row_count, col_count, f"{size_mb:.1f} MB"))
        logger.success(f"  {status} {table_name}: {row_count:,} rows, {col_count} cols")

    return results


def print_summary(results):
    table = Table(title="DuckDB Raw Tables — Load Summary", show_lines=True)
    table.add_column("Status",     style="bold")
    table.add_column("Table",      style="cyan")
    table.add_column("Rows",       justify="right", style="green")
    table.add_column("Columns",    justify="right")
    table.add_column("CSV Size",   justify="right")
    for row in results:
        table.add_row(*[str(c) for c in row])
    console.print(table)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Phase 0 — Step 7: DuckDB Initialization")
    logger.info("=" * 60)

    con = init_duckdb()
    results = load_tables(con)
    con.close()

    print_summary(results)
    logger.success(f"DuckDB ready at: {DUCKDB_PATH}")
    logger.success("Proceed to: python pipeline/00_validate_setup.py")
