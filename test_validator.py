from validator import validate_sql


def test_select_is_allowed():
    ok, _ = validate_sql("SELECT region, SUM(revenue) FROM sales GROUP BY region")
    assert ok


def test_cte_with_is_allowed():
    ok, _ = validate_sql("WITH t AS (SELECT 1 AS x) SELECT * FROM t")
    assert ok


def test_column_named_like_keyword_is_not_blocked():
    # Regression: 'updated_at' previously tripped the UPDATE substring check.
    for col in ["updated_at", "deleted_flag", "insert_date", "altered_by"]:
        ok, msg = validate_sql(f"SELECT {col} FROM customers")
        assert ok, f"{col} should be allowed, got: {msg}"


def test_destructive_statements_blocked():
    for q in [
        "DROP TABLE customers",
        "DELETE FROM sales",
        "UPDATE sales SET revenue = 0",
        "INSERT INTO sales VALUES (1)",
        "ALTER TABLE sales ADD COLUMN x INT",
    ]:
        ok, _ = validate_sql(q)
        assert not ok, f"{q} should be blocked"


def test_stacked_statements_blocked():
    ok, msg = validate_sql("SELECT 1; DROP TABLE customers")
    assert not ok
    assert "Multiple" in msg


def test_trailing_semicolon_is_tolerated():
    ok, _ = validate_sql("SELECT * FROM sales;")
    assert ok
