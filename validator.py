#Responsibility:
#Enforce SQL safety
#Prevent destructive operations
#Keep validation separate from UI and model

FORBIDDEN_KEYWORDS = ["drop", "delete", "update", "insert", "alter"]


def validate_sql(sql_query):
    cleaned_query = sql_query.strip().lower()

    # Must start with SELECT
    if not cleaned_query.startswith("select"):
        return False, "Only SELECT queries are allowed."

    # Block dangerous keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in cleaned_query:
            return False, f"Query contains forbidden keyword: {keyword.upper()}"

    return True, None