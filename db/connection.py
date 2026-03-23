import sqlite3

import state


def get_connection():
    conn = sqlite3.connect(state.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    NOT NULL UNIQUE,
                email     TEXT    NOT NULL UNIQUE,
                clerk_id  TEXT    NOT NULL UNIQUE
            )
      """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES user(id),
                title   TEXT NOT NULL,
                author  TEXT NOT NULL,
                rating  REAL DEFAULT NULL,
                elo     INTEGER DEFAULT 1000,
                UNIQUE (user_id, title, author)  -- the same book can exist for different users
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS comparison (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER   REFERENCES user(id),
                winner_id  INTEGER   NOT NULL REFERENCES book(id),
                loser_id   INTEGER   NOT NULL REFERENCES book(id),
                timestamp  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_comparison(winner_id, loser_id):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO comparison (winner_id, loser_id) VALUES (?, ?)",
            (winner_id, loser_id),
        )
