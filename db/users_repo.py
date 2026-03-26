from db.connection import get_connection


def get_by_clerk_id(clerk_id):
    """Get a user by their Clerk ID. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM user WHERE clerk_id = ?", (clerk_id,)
        ).fetchone()

        return dict(row) if row else None


def insert(clerk_id, email, username):
    """Insert a new user record. Returns the new user's ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO user (clerk_id, email, username) VALUES (?, ?, ?)",
            (clerk_id, email, username),
        )
        return cursor.lastrowid
