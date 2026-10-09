import sqlite3

DATABASE = "trades.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id TEXT UNIQUE NOT NULL,
            client TEXT NOT NULL,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()