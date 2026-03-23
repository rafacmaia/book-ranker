import csv
import os
from datetime import datetime

import state
from constants import BOOK_LIMIT, DEFAULT_RATING
from models import Book
from theme import ERROR, PROMPT
from utils import style


def csv_reader(prompt=" CSV file path: ", back_key="q"):
    print(prompt)
    while True:
        filepath = input(PROMPT).strip()
        if filepath == back_key:
            return filepath

        if not (filepath and os.path.exists(filepath)):
            print(f"{PROMPT}{style('Invalid path. Please try again.', ERROR)}")
            continue

        if not filepath.endswith(".csv"):
            error_message = (
                "That doesn't look like a CSV. "
                "Please provide the full path to a CSV file."
            )
            print(f"{PROMPT}{style(error_message, ERROR)}")
            continue

        return filepath


def import_from_csv(filepath):
    """Import books from a CSV, skipping any already in the system.

    Return count of new books imported.
    """
    new_books = []
    interrupted = False

    try:
        with open(filepath, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                return new_books, interrupted

            reader.fieldnames = [field.lower().strip() for field in reader.fieldnames]
            new_books, interrupted = process_rows(reader, new_books, interrupted)

    except FileNotFoundError:
        print(f" {PROMPT}{style("ERROR! Couldn't find file at:", ERROR)}")
        print(f" {PROMPT}{filepath}")
        interrupted = True
        return new_books, interrupted
    except KeyError as e:
        err_msg = style(
            f"ERROR! Missing column \033[33m{e}\033[31m in CSV file. ", ERROR
        )
        print(f"{PROMPT}{err_msg}")
        interrupted = True
        return new_books, interrupted

    return new_books, interrupted


def process_rows(reader, new_books, interrupted):
    existing_books = {(b.title.lower(), b.author.lower()) for b in state.books}
    skipped_rows = 0

    for i, row in enumerate(reader, start=2):
        if len(state.books) + len(new_books) >= BOOK_LIMIT:
            interrupted = True
            return new_books, interrupted

        title = row["title"].strip()
        author = row["author"].strip()
        raw_rating = (row.get("rating") or "").strip()

        if not (title and author):
            continue
        if not title or not author:
            print(
                style(
                    f" Skipping row {i}: '{title if title else ' '}' by "
                    f"'{author if author else ' '}' – missing title or author",
                    ERROR,
                )
            )

        try:
            rating = float(raw_rating) if raw_rating else DEFAULT_RATING
            if not 0 <= rating <= 10:
                raise ValueError(f" Rating must be between 0 and 10, got {rating}")
        except ValueError as e:
            print(
                style(
                    f" Skipping '{title}' by '{author}' – invalid rating: {e}",
                    ERROR,
                )
            )
            continue

        if (title.lower(), author.lower()) not in existing_books:
            book = Book(title, author, rating)
            book.save()
            new_books.append(book)
            existing_books.add((title.lower(), author.lower()))
        else:
            skipped_rows += 1

    if skipped_rows:
        print(
            f" Skipped {skipped_rows} book{'s' if skipped_rows > 1 else ''}"
            f" already in the system."
        )
    return new_books, interrupted


def export_to_csv():
    """Export all books with their current rankings, to a CSV file."""
    os.makedirs("exports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join("exports", f"book_brawl_{timestamp}.csv")

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
        writer.writerow(["Rank", "Title", "Author", "Rating"])
        for i, book in enumerate(ranked_books, start=1):
            writer.writerow([i, book.title, book.author, book.rating])

    print(f"{PROMPT}✓ Leaderboard exported to:\033[32m {filepath}\033[0m")
