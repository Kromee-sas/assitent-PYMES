import re

def validate_sql(query):
    """Validates the generated SQL query before execution."""
    blocked_keywords = ["DELETE", "UPDATE", "INSERT", "DROP", "ALTER"]
    
    # Ensure only SELECT statements are allowed
    if not query.strip().upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # Block dangerous SQL keywords
    if any(keyword in query.upper() for keyword in blocked_keywords):
        return False, f"Restricted keyword detected in query: {query}"
    
    # Prevent wildcard `SELECT *`
    if "SELECT *" in query.upper():
        return False, "Wildcard queries are not allowed. Please specify columns."

    return True, "Query is valid."