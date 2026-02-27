import csv
import os
from datetime import datetime

import state
from models import Book


def import_from_csv(filepath):
    """Import books from a CSV, skipping any already in the system.

    Return count of new books imported.
    """
    existing_books = {(b.title.lower(), b.author.lower()) for b in Book.load_all()}
    new_books = 0

    try:
        with open(filepath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [field.lower().strip() for field in reader.fieldnames]
            for row in reader:
                title = row["title"].strip()
                author = row["author"].strip()

                if (title.lower(), author.lower()) not in existing_books:
                    Book(title, author, float(row["rating"].strip())).save()
                    new_books += 1

    except FileNotFoundError:
        print(f" Error! Couldn't find file at: '{filepath}'")
        return 0
    except KeyError as e:
        print(
            f" Error! Missing column '{e}' in CSV file."
            f" Expected columns: 'title', 'author', 'rating'."
        )
        return 0
    except ValueError as e:
        print(
            f" Error! Invalid rating value: {e}."
            f" Ensure 'rating' is a number from 1 to 10, inclusive."
        )
        return 0

    return new_books


def export_to_csv():
    """Export all books with their current rankings, to a CSV file."""
    os.makedirs("exports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join("exports", f"book_rankings_{timestamp}.csv")

    # Check if the file already exists, if so, append a number to the end
    if os.path.exists(filepath):
        base = filepath.replace(".csv", "")
        counter = 2
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}.csv"
            counter += 1

    ranked_books = sorted(state.books, key=lambda b: b.elo, reverse=True)

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Title", "Author", "Rating", "Score"])
        for i, book in enumerate(ranked_books, start=1):
            writer.writerow([i, book.title, book.author, book.rating, book.elo])

    print(f" \033[33m>\033[0m ✓ Rankings exported to:\033[32m {filepath}\033[33m")
