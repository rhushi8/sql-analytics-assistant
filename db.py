#Responsibility:
#Database connection
#Schema extraction

import sqlite3


def get_connection(db_path="database.db"):
    return sqlite3.connect(db_path)


def get_schema(conn):
    cursor = conn.cursor()

    schema_info = ""
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    for table in tables:
        table_name = table[0]
        columns = cursor.execute(
            f"PRAGMA table_info({table_name});"
        ).fetchall()

        schema_info += f"\nTable: {table_name}\n"
        for col in columns:
            schema_info += f"- {col[1]} ({col[2]})\n"

    return schema_info