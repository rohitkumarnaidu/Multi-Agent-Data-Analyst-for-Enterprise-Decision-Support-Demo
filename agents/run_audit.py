import subprocess
import os

questions = [
    "What are the top 3 product categories by total sales revenue in our historical data?",
    "Predict the late delivery risk for a new order with these specs: Weight 1200g, Volume 2500cm3, Freight 22.5, Price 89.9, Freight ratio 0.25, Approval hrs 1.5, ordered on Wednesday (2) in November (11), seller late rate 0.12, Customer state MG, Seller state SP.",
    "What is the historical average freight value for the top 5 customer states? Please generate a bar chart for this data.",
    "How does the late delivery rate compare between orders placed in Q1 versus Q4? Use the database to find out.",
    "Can you provide the late delivery rate for orders placed in the year 2050?"
]

def run_cmd(cmd, env=None):
    print(f"\nExecuting: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, capture_output=True)
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
    return stdout + "\n" + stderr

def main():
    os.makedirs('reports', exist_ok=True)
    transcript = "# Phase 6b Audit & Verification Transcript\n\n"
    
    # 1. Run 5 Demo Questions
    transcript += "## 1. Five Demo Questions from SCOPE.md\n"
    for i, q in enumerate(questions, 1):
        transcript += f"\n### Question {i}: {q}\n"
        transcript += "```\n"
        out = run_cmd([".\\venv_312\\Scripts\\python", "agents/crew.py", q])
        transcript += out
        transcript += "\n```\n"
        
    # 2. SQL Parity Test (Independent Verification)
    transcript += "\n## 2. SQL Parity Test\n"
    transcript += "Re-running a raw DuckDB query outside the agent to confirm numbers match Q1.\n"
    transcript += "```python\n"
    import duckdb
    try:
        con = duckdb.connect('data/olist.duckdb', read_only=True)
        df = con.execute("""
            SELECT product_category_name_english, SUM(price) as total_revenue
            FROM clean_order_items oi
            JOIN clean_products p ON oi.product_id = p.product_id
            GROUP BY product_category_name_english
            ORDER BY total_revenue DESC
            LIMIT 3;
        """).df()
        con.close()
        transcript += str(df) + "\n"
    except Exception as e:
        transcript += f"Error running parity test: {str(e)}\n"
    transcript += "```\n"
    
    # 3. Fallback Test
    transcript += "\n## 3. Fallback Test (Missing API Key)\n"
    transcript += "Running Q1 with OPENAI_API_KEY explicitly removed to test graceful degradation.\n"
    transcript += "```\n"
    env = os.environ.copy()
    if "OPENAI_API_KEY" in env:
        del env["OPENAI_API_KEY"]
    out = run_cmd([".\\venv_312\\Scripts\\python", "agents/crew.py", questions[0]], env=env)
    transcript += out
    transcript += "\n```\n"
    
    # Save Transcript
    with open('reports/audit_transcript.md', 'w', encoding='utf-8') as f:
        f.write(transcript)
        
    print("\nAudit complete! Transcript saved to reports/audit_transcript.md")

if __name__ == "__main__":
    main()
