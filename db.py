#Responsibility:
#Database connection
#Schema extraction

import sqlite3

def get_connection():
    return sqlite3.connect("database.db")


def get_schema(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema_description = ""

    for table in tables:
        table_name = table[0]
        schema_description += f"\nTable: {table_name}\nColumns:\n"

        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        for col in columns:
            col_name = col[1]
            col_type = col[2]
            schema_description += f"- {col_name} ({col_type})\n"

    return schema_description