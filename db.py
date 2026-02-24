import sqlite3
import state


def get_connection():
    return sqlite3.connect(state.db_path)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            author  TEXT NOT NULL,
            rating  REAL NOT NULL,
            elo     INTEGER DEFAULT 1000
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparisons  (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            winner_id   INTEGER NOT NULL,
            loser_id    INTEGER NOT NULL,
            timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (winner_id) REFERENCES books(id),
            FOREIGN KEY (loser_id) REFERENCES books(id)
        )
    """)

    conn.commit()
    conn.close()


def save_comparison(winner, loser):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO comparisons (winner_id, loser_id) VALUES (?, ?)",
        (winner, loser),
    )
    conn.commit()
    conn.close()


def get_unique_opponent_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT book_id, COUNT(DISTINCT opponent_id) AS unique_opponents
        FROM (
            SELECT winner_id as book_id, loser_id as opponent_id FROM comparisons
            UNION ALL
            SELECT loser_id as book_id, winner_id as opponent_id FROM comparisons
        )
        GROUP BY book_id
    """)
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}
