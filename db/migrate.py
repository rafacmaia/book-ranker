"""
Database migration script for Book Brawl.

Safe to run multiple times — all changes are guarded with existence checks.

Usage:
    python db/migrate.py
    python db/migrate.py --db data/demo1.db    # migrate a specific database
"""

import sqlite3
import sys

DB_PATH = "data/book_brawl.db"


def get_columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def get_tables(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return [row[0] for row in rows]


def get_indexes(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
    return [row[0] for row in rows]


def migrate(db_path):
    conn = sqlite3.connect(db_path)
    tables = get_tables(conn)
    indexes = get_indexes(conn)

    print(f"Migrating: {db_path}")

    # --- 1. Create user table if it doesn't exist
    if "user" not in tables:
        conn.execute("""
            CREATE TABLE user (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    NOT NULL UNIQUE,
                email     TEXT    NOT NULL UNIQUE,
                clerk_id  TEXT    NOT NULL UNIQUE
            )
        """)
        print("  ✓ Created user table")

    # --- 2. Rename books → book (if old name still exists)
    if "books" in tables and "book" not in tables:
        conn.execute("ALTER TABLE books RENAME TO book")
        print("  ✓ Renamed books → book")
        tables = get_tables(conn)  # refresh table list

    # --- 3. Rename comparisons → comparison (if old name still exists)
    if "comparisons" in tables and "comparison" not in tables:
        conn.execute("ALTER TABLE comparisons RENAME TO comparison")
        print("  ✓ Renamed comparisons → comparison")

    # --- 4. Make rating nullable (DEFAULT NULL instead of NOT NULL).
    # SQLite doesn't support ALTER COLUMN, so we recreate the table with the new
    # definition and copy all existing data over.
    book_columns = get_columns(conn, "book")
    if "user_id" not in book_columns:
        # Recreate book table with both changes at once: user_id added, rating nullable.
        conn.execute("""
            CREATE TABLE book_new (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER REFERENCES user(id),
                title    TEXT    NOT NULL,
                author   TEXT    NOT NULL,
                rating   REAL    DEFAULT NULL,
                elo      INTEGER DEFAULT 1000,
                UNIQUE (user_id, title, author)
            )
        """)
        # Copy existing data — user_id will be NULL for all existing rows (expected)
        conn.execute("""
            INSERT INTO book_new (id, title, author, rating, elo)
            SELECT id, title, author, rating, elo FROM book
        """)
        conn.execute("DROP TABLE book")
        conn.execute("ALTER TABLE book_new RENAME TO book")
        print("  ✓ Rebuilt book table: rating now nullable, user_id added")
    else:
        # user_id already exists — check if rating is still NOT NULL and fix if so.
        # PRAGMA table_info returns notnull=1 if the column has NOT NULL constraint.
        rating_info = next(
            row for row in conn.execute("PRAGMA table_info(book)") if row[1] == "rating"
        )
        if rating_info[3] == 1:  # notnull flag
            conn.execute("""
                CREATE TABLE book_new (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id  INTEGER REFERENCES user(id),
                    title    TEXT    NOT NULL,
                    author   TEXT    NOT NULL,
                    rating   REAL    DEFAULT NULL,
                    elo      INTEGER DEFAULT 1000,
                    UNIQUE (user_id, title, author)
                )
            """)
            conn.execute("""
                INSERT INTO book_new (id, user_id, title, author, rating, elo)
                SELECT id, user_id, title, author, rating, elo FROM book
            """)
            conn.execute("DROP TABLE book")
            conn.execute("ALTER TABLE book_new RENAME TO book")
            print("  ✓ Rebuilt book table: rating now nullable")

    # --- 5. Add user_id to comparison if missing
    if "user_id" not in get_columns(conn, "comparison"):
        conn.execute(
            "ALTER TABLE comparison ADD COLUMN user_id INTEGER REFERENCES user(id)"
        )
        print(
            "  ✓ Added user_id to comparison (nullable — existing rows have no user yet)"
        )

    # --- 6. Add indexes if missing
    if "idx_book_user" not in indexes:
        conn.execute("CREATE INDEX idx_book_user ON book(user_id)")
        print("  ✓ Created index: idx_book_user")

    if "idx_comparison_user" not in indexes:
        conn.execute("CREATE INDEX idx_comparison_user ON comparison(user_id)")
        print("  ✓ Created index: idx_comparison_user")

    if "idx_comparison_winner" not in indexes:
        conn.execute("CREATE INDEX idx_comparison_winner ON comparison(winner_id)")
        print("  ✓ Created index: idx_comparison_winner")

    if "idx_comparison_loser" not in indexes:
        conn.execute("CREATE INDEX idx_comparison_loser ON comparison(loser_id)")
        print("  ✓ Created index: idx_comparison_loser")

    conn.commit()
    conn.close()
    print("Migration complete.\n")


if __name__ == "__main__":
    db_path = DB_PATH
    for arg in sys.argv[1:]:
        if arg.startswith("--db"):
            db_path = (
                arg.split("=")[-1] if "=" in arg else sys.argv[sys.argv.index(arg) + 1]
            )

    migrate(db_path)
