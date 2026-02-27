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

        return books

    def __repr__(self):
        return f"{self.title}, by {self.author}"


def rating_to_elo(rating):
    """Maps a rating (1-10) to an initial Elo score.

    If scores are still within the initial 800-1200 range, use that default mapping.
    Otherwise, map to the current elo_min-elo_max distribution.
    """
    if Book.elo_max <= 1200 and Book.elo_min >= 800:
        return round(800 + (rating - 1) * (400 / 9))
    else:
        return round(Book.elo_min + (rating - 1) * ((Book.elo_max - Book.elo_min) / 9))
