from db import get_connection

def rating_to_elo(rating):
    """Maps a rating from 1 to 10 to an Elo rating from 800 to 1200"""
    return round(800 + (rating - 1) * (400 / 9))

class Book:
    def __init__(self, title, author, rating, elo=None, id=None):
        self.title = title
        self.author = author
        self.rating = rating
        self.id = id
        self.elo = elo if elo is not None else rating_to_elo(rating)

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, rating, elo) VALUES (?, ?, ?, ?)",
            (self.title, self.author, self.rating, self.elo),
        )
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def update_elo(self, new_elo):
        self.elo = new_elo
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET elo = ? WHERE id = ?", (self.elo, self.id))
        conn.commit()
        conn.close()

    @classmethod
    def load_all(cls):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, rating, elo FROM books")
        rows = cursor.fetchall()
        conn.close()
        return [
            cls(title=r[1], author=r[2], rating=r[3], id=r[0], elo=r[4]) for r in rows
        ]

    @classmethod
    def seed(cls, books_data):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        conn.close()

        if count == 0:
            for title, author, rating in books_data:
                cls(title, author, rating).save()
            print(f"Seeded {len(books_data)} books.\n")

    def __repr__(self):
        return f"{self.title}, by {self.author}"
