"""
pipeline/00_validate_setup.py
=============================
Phase 0 — Step 8: Full environment + data validation.

Checks:
  - Python version
  - All required packages importable
  - .env file present with required keys
  - All 9 raw CSVs present
  - DuckDB file exists with all 9 raw tables
  - Prints a clean Phase 0 Complete summary

Usage:
    python pipeline/00_validate_setup.py
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


# ── Config ────────────────────────────────────────────────────────────────────
REQUIRED_PACKAGES = [
    "pandas", "numpy", "duckdb", "pyarrow",
    "sklearn", "xgboost", "imblearn", "shap", "joblib",
    "fastapi", "uvicorn", "pydantic",
    "streamlit",
    "matplotlib", "seaborn", "plotly",
    "dotenv", "kaggle", "tqdm", "loguru", "rich",
]

REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "KAGGLE_USERNAME",
    "KAGGLE_KEY",
    "DUCKDB_PATH",
    "RAW_DATA_DIR",
]

EXPECTED_CSVs = [
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

EXPECTED_TABLES = [
    "raw_orders", "raw_order_items", "raw_order_payments",
    "raw_order_reviews", "raw_customers", "raw_sellers",
    "raw_products", "raw_geolocation", "raw_category_translation",
]


# ── Check Functions ───────────────────────────────────────────────────────────

def check_python():
    v = sys.version_info
    ok = v.major == 3 and v.minor >= 11
    return ok, f"{v.major}.{v.minor}.{v.micro}"


def check_packages():
    results = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
            results.append((True, pkg, "OK"))
        except ImportError as e:
            results.append((False, pkg, str(e)))
    return results


def check_env():
    from dotenv import load_dotenv
    load_dotenv()
    results = []
    for key in REQUIRED_ENV_KEYS:
        val = os.getenv(key)
        ok  = val is not None and val != "" and "your_" not in val.lower()
        results.append((ok, key, "Set ✓" if ok else "Missing or placeholder ✗"))
    return results


def check_csvs():
    from dotenv import load_dotenv
    load_dotenv()
    raw_dir = Path(os.getenv("RAW_DATA_DIR", "./raw"))
    results = []
    for fname in EXPECTED_CSVs:
        path = raw_dir / fname
        exists = path.exists()
        size   = f"{path.stat().st_size/1_048_576:.1f} MB" if exists else "—"
        results.append((exists, fname, size))
    return results


def check_duckdb():
    from dotenv import load_dotenv
    load_dotenv()
    import duckdb
    db_path = Path(os.getenv("DUCKDB_PATH", "./data/olist.duckdb"))
    if not db_path.exists():
        return [(False, t, "DB file missing") for t in EXPECTED_TABLES]
    con = duckdb.connect(str(db_path))
    existing = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    results = []
    for table in EXPECTED_TABLES:
        if table in existing:
            count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            results.append((True, table, f"{count:,} rows"))
        else:
            results.append((False, table, "Table missing"))
    con.close()
    return results


# ── Report ────────────────────────────────────────────────────────────────────

def render_table(title, columns, rows):
    t = Table(title=title, show_lines=True)
    t.add_column("Status", style="bold", width=8)
    for col in columns:
        t.add_column(col)
    for ok, *rest in rows:
        icon = "✅" if ok else "❌"
        t.add_row(icon, *rest)
    console.print(t)
    return all(ok for ok, *_ in rows)


if __name__ == "__main__":
    console.rule("[bold cyan]Phase 0 Validation")
    all_ok = True

    # Python
    ok, version = check_python()
    rprint(f"Python version: {version} — {'[green]✅ OK[/]' if ok else '[red]❌ Need 3.11+[/]'}")
    all_ok &= ok

    # Packages
    pkg_results = check_packages()
    all_ok &= render_table("Python Packages", ["Package", "Status"], pkg_results)

    # Env keys
    env_results = check_env()
    all_ok &= render_table(".env Keys", ["Key", "Status"], env_results)

    # CSVs
    csv_results = check_csvs()
    all_ok &= render_table("Raw CSV Files", ["Filename", "Size"], csv_results)

    # DuckDB
    db_results = check_duckdb()
    all_ok &= render_table("DuckDB Tables", ["Table", "Row Count"], db_results)

    # Final verdict
    console.rule()
    if all_ok:
        rprint("[bold green]\n  🎉 Phase 0 Complete! All checks passed. Ready for Phase 1 (Data Cleaning).\n")
    else:
        rprint("[bold red]\n  ⚠️  Some checks failed. Fix the issues above before proceeding.\n")
