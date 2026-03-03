import sqlite3

import state


def get_connection():
    conn = sqlite3.connect(state.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title   TEXT NOT NULL,
                author  TEXT NOT NULL,
                rating  REAL NOT NULL,
                elo     INTEGER DEFAULT 1000
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS comparisons  (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                winner_id   INTEGER NOT NULL,
                loser_id    INTEGER NOT NULL,
                timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (winner_id) REFERENCES books(id),
                FOREIGN KEY (loser_id) REFERENCES books(id)
            )
        """)


def save_comparison(winner_id, loser_id):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO comparisons (winner_id, loser_id) VALUES (?, ?)",
            (winner_id, loser_id),
        )
