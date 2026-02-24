from db import get_connection


class Book:
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

    @classmethod
    def load_all(cls):
        with get_connection() as conn:
            cursor = conn.execute("SELECT title, author, rating, elo, id FROM books")
            rows = cursor.fetchall()

        return [
            cls(
                title=r["title"],
                author=r["author"],
                rating=r["rating"],
                elo=r["elo"],
                book_id=r["id"],
            )
            for r in rows
        ]

    def __repr__(self):
        return f"{self.title}, by {self.author}"


def rating_to_elo(rating):
    """Maps a rating from 1 to 10 to an Elo rating from 800 to 1200"""
    return round(800 + (rating - 1) * (400 / 9))
