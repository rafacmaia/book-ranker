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


def save_comparison(winner, loser):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO comparisons (winner_id, loser_id) VALUES (?, ?)",
            (winner, loser),
        )


def get_opponent_counts():
    """Return a dictionary of book_id -> count of unique opponents."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT book_id, COUNT(DISTINCT opponent_id) AS unique_opponents
            FROM (
                SELECT winner_id as book_id, loser_id as opponent_id FROM comparisons
                UNION ALL
                SELECT loser_id as book_id, winner_id as opponent_id FROM comparisons
            )
            GROUP BY book_id
        """)
        rows = cursor.fetchall()

    return {row["book_id"]: row["unique_opponents"] for row in rows}


def get_past_opponents(book):
    """Return a dictionary of opponent_id -> times matched against book."""
    with get_connection() as conn:
        cursor = conn.execute(
            f"""
            SELECT opponent_id, COUNT(opponent_id) AS matches_played 
            FROM (
                SELECT winner_id as book_id, loser_id as opponent_id FROM comparisons
                UNION ALL
                SELECT loser_id as book_id, winner_id as opponent_id FROM comparisons
            )
            WHERE book_id = ?
            GROUP BY opponent_id
        """,
            (book.id,),
        )
        rows = cursor.fetchall()

    return {row["opponent_id"]: row["matches_played"] for row in rows}
