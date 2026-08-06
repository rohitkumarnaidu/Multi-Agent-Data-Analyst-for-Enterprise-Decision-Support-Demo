"""
pipeline/01_verify_raw.py
=========================
Phase 1 — Raw Data Verification

Profiles all 9 raw_* tables in DuckDB:
  - Row & column counts
  - Null % per column
  - Duplicate key checks
  - Date range check
  - Join coverage between tables

Outputs: reports/phase1_data_profile.md

Usage:
    python pipeline/01_verify_raw.py
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import duckdb
from rich.console import Console
from rich.table import Table
from loguru import logger

load_dotenv()

DUCKDB_PATH  = Path(os.getenv("DUCKDB_PATH", "./data/olist.duckdb"))
REPORTS_DIR  = Path("./reports")
REPORTS_DIR.mkdir(exist_ok=True)

console = Console()

# ── Table configs ────────────────────────────────────────────────────────────
TABLES = {
    "raw_orders":              {"pk": "order_id"},
    "raw_order_items":         {"pk": None},           # composite key
    "raw_order_payments":      {"pk": None},
    "raw_order_reviews":       {"pk": "review_id"},
    "raw_customers":           {"pk": "customer_id"},
    "raw_sellers":             {"pk": "seller_id"},
    "raw_products":            {"pk": "product_id"},
    "raw_geolocation":         {"pk": None},
    "raw_category_translation":{"pk": "product_category_name"},
}

JOIN_CHECKS = [
    ("raw_orders",        "raw_order_items",    "order_id",   "Orders → Items"),
    ("raw_orders",        "raw_order_payments", "order_id",   "Orders → Payments"),
    ("raw_orders",        "raw_order_reviews",  "order_id",   "Orders → Reviews"),
    ("raw_orders",        "raw_customers",      "customer_id","Orders → Customers"),
    ("raw_order_items",   "raw_sellers",        "seller_id",  "Items → Sellers"),
    ("raw_order_items",   "raw_products",       "product_id", "Items → Products"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_table_stats(con, table_name):
    """Return row count, column count, and per-column null %."""
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE {table_name}").fetchall()]

    null_pcts = {}
    for col in cols:
        nulls = con.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE \"{col}\" IS NULL"
        ).fetchone()[0]
        null_pcts[col] = round(nulls * 100.0 / row_count, 1) if row_count else 0

    return row_count, cols, null_pcts


def check_pk_dupes(con, table_name, pk_col):
    if not pk_col:
        return None
    dupes = con.execute(f"""
        SELECT COUNT(*) FROM (
            SELECT "{pk_col}", COUNT(*) AS cnt
            FROM {table_name}
            GROUP BY "{pk_col}"
            HAVING cnt > 1
        )
    """).fetchone()[0]
    return dupes


def check_date_range(con):
    result = con.execute("""
        SELECT
            MIN(order_purchase_timestamp)::DATE AS earliest,
            MAX(order_purchase_timestamp)::DATE AS latest
        FROM raw_orders
        WHERE order_purchase_timestamp IS NOT NULL
    """).fetchone()
    return result


def check_join_coverage(con, left_table, right_table, key, label):
    total = con.execute(f"SELECT COUNT(DISTINCT {key}) FROM {left_table}").fetchone()[0]
    matched = con.execute(f"""
        SELECT COUNT(DISTINCT l.{key})
        FROM {left_table} l
        INNER JOIN {right_table} r ON l.{key} = r.{key}
    """).fetchone()[0]
    pct = round(matched * 100.0 / total, 1) if total else 0
    return total, matched, pct


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("Phase 1 — Raw Data Verification")
    logger.info("=" * 60)

    if not DUCKDB_PATH.exists():
        logger.error(f"DuckDB not found at {DUCKDB_PATH}. Run 00_init_duckdb.py first.")
        return

    con = duckdb.connect(str(DUCKDB_PATH))

    # ── Table shapes & nulls ─────────────────────────────────────────────────
    console.rule("[bold cyan]Table Shapes & Null Counts")
    shape_table = Table(show_lines=True, title="Raw Table Profiles")
    shape_table.add_column("Table",    style="cyan")
    shape_table.add_column("Rows",     justify="right", style="green")
    shape_table.add_column("Cols",     justify="right")
    shape_table.add_column("PK Dupes", justify="right")
    shape_table.add_column("High-Null Columns (>10%)", style="yellow")

    profile_data = {}
    for table_name, cfg in TABLES.items():
        row_count, cols, null_pcts = get_table_stats(con, table_name)
        dupes = check_pk_dupes(con, table_name, cfg["pk"])
        high_null = [f"{c}: {p}%" for c, p in null_pcts.items() if p > 10]
        profile_data[table_name] = {
            "rows": row_count, "cols": cols, "null_pcts": null_pcts,
            "dupes": dupes, "high_null": high_null
        }
        dupe_str = str(dupes) if dupes is not None else "N/A"
        dupe_style = "[red]" if dupes and dupes > 0 else ""
        shape_table.add_row(
            table_name, f"{row_count:,}", str(len(cols)),
            f"{dupe_style}{dupe_str}",
            ", ".join(high_null) if high_null else "✅ None"
        )
        logger.info(f"{table_name}: {row_count:,} rows, {len(cols)} cols")

    console.print(shape_table)

    # ── Date range ───────────────────────────────────────────────────────────
    console.rule("[bold cyan]Order Date Range")
    earliest, latest = check_date_range(con)
    logger.info(f"Orders span: {earliest} → {latest}")
    console.print(f"  📅 Orders span: [green]{earliest}[/] → [green]{latest}[/]")

    # ── Join coverage ────────────────────────────────────────────────────────
    console.rule("[bold cyan]Key Join Coverage")
    join_table = Table(show_lines=True, title="Join Coverage (left → right)")
    join_table.add_column("Join",         style="cyan")
    join_table.add_column("Left Keys",    justify="right")
    join_table.add_column("Matched",      justify="right", style="green")
    join_table.add_column("Coverage %",  justify="right")
    join_table.add_column("Status")

    join_results = []
    for left, right, key, label in JOIN_CHECKS:
        total, matched, pct = check_join_coverage(con, left, right, key, label)
        status = "✅" if pct >= 95 else ("⚠️" if pct >= 80 else "❌")
        join_table.add_row(label, f"{total:,}", f"{matched:,}", f"{pct}%", status)
        join_results.append((label, total, matched, pct, status))
        logger.info(f"{label}: {pct}% coverage ({matched:,}/{total:,})")

    console.print(join_table)
    con.close()

    # ── Write markdown report ─────────────────────────────────────────────────
    write_report(profile_data, (earliest, latest), join_results)
    logger.success("Report written to reports/phase1_data_profile.md")
    logger.success("Phase 1 verification complete. Proceed to: python pipeline/01_clean.py")


def write_report(profile_data, date_range, join_results):
    earliest, latest = date_range
    lines = [
        "# Phase 1 — Raw Data Profile",
        f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        "## Table Shapes\n",
        "| Table | Rows | Cols | PK Dupes | High-Null Columns |",
        "|---|---|---|---|---|",
    ]
    for tbl, d in profile_data.items():
        dupes = str(d['dupes']) if d['dupes'] is not None else "N/A"
        high = ", ".join(d['high_null']) if d['high_null'] else "None"
        lines.append(f"| `{tbl}` | {d['rows']:,} | {len(d['cols'])} | {dupes} | {high} |")

    lines += [
        f"\n## Date Range\n",
        f"- Orders span: **{earliest}** → **{latest}**",
        "\n## Join Coverage\n",
        "| Join | Left Keys | Matched | Coverage | Status |",
        "|---|---|---|---|---|",
    ]
    for label, total, matched, pct, status in join_results:
        lines.append(f"| {label} | {total:,} | {matched:,} | {pct}% | {status} |")

    lines += [
        "\n## Observations\n",
        "- `order_delivered_customer_date` has nulls for cancelled/undelivered orders — expected",
        "- `review_comment_title` and `review_comment_message` are mostly null — optional fields",
        "- `product_category_name` has small null% — will fill via translation join in Phase 3",
        "- `product_weight_g` and dimensions have small null% — will fill with category median in Phase 3",
        "- Geolocation has duplicates per zip (multiple coordinates) — will average in Phase 3",
    ]

    (REPORTS_DIR / "phase1_data_profile.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
