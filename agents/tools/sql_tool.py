import duckdb
from langchain.tools import tool

@tool("Execute DuckDB SQL Query")
def execute_sql(query: str) -> str:
    """
    Executes a SELECT SQL query against the Olist DuckDB database and returns the results.
    The database contains tables like `orders_master`, `clean_products`, etc.
    Always write valid DuckDB SQL syntax.
    """
    try:
        # Security: Prevent destructive commands
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
        if any(keyword in query.upper() for keyword in forbidden):
            return "Error: Only SELECT queries are allowed."
            
        con = duckdb.connect('data/olist.duckdb', read_only=True)
        df = con.execute(query).df()
        con.close()
        
        # Return as a markdown table string for the LLM to easily read
        if df.empty:
            return "Query executed successfully, but returned 0 rows."
        return df.to_markdown(index=False)
        
    except Exception as e:
        return f"SQL Error: {str(e)}"
