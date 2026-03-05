import csv
import os
from datetime import datetime

import constants
import state
from models import Book
from utils import PROMPT


def csv_reader(prompt=" CSV file path: ", options=None):
    if options is None:
        options = ["q"]

    print(prompt)
    while True:
        filepath = input(PROMPT).strip()
        if filepath in options:
            return filepath

        if not (filepath and os.path.exists(filepath)):
            print(f"{PROMPT}\033[31mInvalid path. Please try again.\033[0m")
            continue

        if not filepath.endswith(".csv"):
            print(
                f"{PROMPT}\033[31mThat doesn't look like a CSV."
                " Please provide the full path to your CSV file.\033[0m"
            )
            continue

        return import_from_csv(filepath)


def import_from_csv(filepath):
    """Import books from a CSV, skipping any already in the system.

    Return count of new books imported.
    """
    existing_books = {(b.title.lower(), b.author.lower()) for b in state.books}
    new_books = 0
    interrupted = False

    try:
        with open(filepath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [field.lower().strip() for field in reader.fieldnames]
            for row in reader:
                if len(state.books) + new_books >= constants.BOOK_LIMIT:
                    interrupted = True
                    return new_books, interrupted

                title = row["title"].strip()
                author = row["author"].strip()

                try:
                    rating = float(row["rating"].strip())
                    if not 0 <= rating <= 10:
                        raise ValueError(
                            f"Rating must be between 0 and 10, got {rating}"
                        )
                except ValueError as e:
                    print()
                    print(
                        f" \033[31mSkipping '{title}' by '{author}'\n"
                        f"   - invalid rating: {e}.\033[0m "
                    )
                    print()
                    continue

                if (title.lower(), author.lower()) not in existing_books:
                    Book(title, author, rating).save()
                    new_books += 1

    except FileNotFoundError:
        print(
            f"{PROMPT}\033[31mError! Couldn't find file at:\033[0m "
            f"\n {PROMPT}{filepath}"
        )
        return 0, interrupted
    except KeyError as e:
        print(
            f"{PROMPT}\033[31mError! Missing column \033[33m{e}\033[31m in CSV file. Expected columns:"
            f" \033[33m title\033[31m,\033[33m author\033[31m,\033[33m rating\033[31m."
        )
        return 0, interrupted

    return new_books, interrupted


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

    print(f"{PROMPT}✓ Rankings exported to:\033[32m {filepath}\033[0m")
