from db import get_connection


class Book:
    elo_min = 800
    elo_max = 1200

    def __init__(self, title, author, rating, elo=None, book_id=None):
        self.id = book_id
        self.title = title
        self.author = author
        self.rating = rating
        self.elo = elo if elo is not None else rating_to_elo(rating)
        self.opponents = {}  # {opp_id: times_matched}

    def save(self):
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO books (title, author, rating, elo) VALUES (?, ?, ?, ?)",
                (self.title, self.author, self.rating, self.elo),
            )
            self.id = cursor.lastrowid

    def update_elo(self, new_elo):
        self.elo = new_elo
        with get_connection() as conn:
            conn.execute("UPDATE books SET elo = ? WHERE id = ?", (self.elo, self.id))

        if self.elo < Book.elo_min:
            Book.elo_min = self.elo
        if self.elo > Book.elo_max:
            Book.elo_max = self.elo

    def record_opponent(self, opponent_id):
        self.opponents[opponent_id] = self.opponents.get(opponent_id, 0) + 1

    @classmethod
    def load_all(cls):
        with get_connection() as conn:
            cursor = conn.execute("SELECT title, author, rating, elo, id FROM books")
            rows = cursor.fetchall()

        books = []
        for row in rows:
            books.append(
                cls(
                    title=row["title"],
                    author=row["author"],
                    rating=row["rating"],
                    elo=row["elo"],
                    book_id=row["id"],
                )
            )
            if row["elo"] < cls.elo_min:
                cls.elo_min = row["elo"]
            if row["elo"] > cls.elo_max:
                cls.elo_max = row["elo"]

        book_map = {b.id: b for b in books}
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT winner_id, loser_id FROM comparisons
                """)
            for row in cursor.fetchall():
                w_id, l_id = row["winner_id"], row["loser_id"]
                book_map[w_id].record_opponent(l_id)
                book_map[l_id].record_opponent(w_id)

        return books

    def __repr__(self):
        return f"{self.title}, by {self.author}"


def rating_to_elo(rating):
    """Maps a rating (1-10) to an initial Elo score.

    If scores are still within the initial 800-1200 range, use that default mapping.
    Otherwise, adjust the lower and upper bounds to match the current bounds.
    """
    elo_min = Book.elo_min if Book.elo_min < 800 else 800
    elo_max = Book.elo_max if Book.elo_max > 1200 else 1200
    return round(elo_min + (rating - 1) * ((elo_max - elo_min) / 9))
