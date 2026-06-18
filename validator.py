#Responsibility:
#Enforce SQL safety
#Prevent destructive operations
#Keep validation separate from UI and model

import re

# Destructive / state-changing keywords. Matched on word boundaries so that
# legitimate identifiers like `updated_at` or `deleted_flag` are NOT blocked.
FORBIDDEN_KEYWORDS = [
    "drop", "delete", "update", "insert", "alter",
    "truncate", "replace", "create", "attach", "detach",
    "pragma", "grant", "revoke", "vacuum", "reindex",
]

_FORBIDDEN_RE = re.compile(
    r"\b(" + "|".join(FORBIDDEN_KEYWORDS) + r")\b", re.IGNORECASE
)


def validate_sql(sql_query):
    cleaned_query = sql_query.strip().rstrip(";").strip()
    lowered = cleaned_query.lower()

    # Must start with SELECT (allow a leading WITH ... SELECT CTE).
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return False, "Only SELECT queries are allowed."

    # Reject stacked/multiple statements (e.g. "SELECT 1; DROP TABLE x").
    if ";" in cleaned_query:
        return False, "Multiple SQL statements are not allowed."

    # Block destructive keywords using word boundaries.
    match = _FORBIDDEN_RE.search(cleaned_query)
    if match:
        return False, f"Query contains forbidden keyword: {match.group(1).upper()}"

    return True, None
