import state
from constants import BOOK_LIMIT, DEFAULT_RATING
from csv_handler import csv_reader, import_from_csv
from db.books_repo import insert
from messages import (
    CSV_INSTRUCTIONS,
    EMPTY_IMPORT,
    IMPORT_MENU,
    LIMIT_REACHED,
    LIMIT_WARNING,
    import_interrupted,
)
from models import Book
from theme import DIVIDER, ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import format_book, header, press_enter, prompt, rule, style


def add_books(books):
    """Add new books to the library either through a CSV import or manual entry."""
    print(header("IMPORT NEW BOOKS", new_line=True))

    if len(books) >= BOOK_LIMIT:
        print(LIMIT_REACHED)
        press_enter()
        return

    while True:
        print(IMPORT_MENU)
        choice = prompt(options=["1", "2", "b"])

        if choice == "1":
            new_books = _manual_entry(books)
            process_import(new_books, method="manual")
            break
        elif choice == "2":
            print(f"\n {rule(LINE_LENGTH - 1, DIVIDER)}")
            print(" Please provide the path to your CSV file to sync new books.")
            print(CSV_INSTRUCTIONS)

            filepath = csv_reader(
                prompt=f"\n {style('CSV file path (b to go back):', SECONDARY)} ",
                back_key="b",
            )
            if filepath == "b":
                print(f"\n {rule(LINE_LENGTH - 1, DIVIDER)}")
                continue

            print(f"\n {style('Processing file...', SECONDARY)}")
            new_books, interrupted = import_from_csv(filepath, books)
            print()
            process_import(new_books, interrupted, method="CSV")
            break
        elif choice == "b":
            return


def _manual_entry(books):
    """Add new books to the library one at a time via user input."""
    existing_books = {(b.title.lower(), b.author.lower()) for b in books}
    new_books = []

    while True:
        count = len(new_books) + 1

        print()
        print(
            f" {rule((LINE_LENGTH - 5 - len(str(count))), DIVIDER)}"
            f" {style(count, DIVIDER)}"
            f" {rule(2, DIVIDER)}"
        )

        title = input(style(" Title:  ", SECONDARY)).strip()
        author = input(style(" Author: ", SECONDARY)).strip()

        if (title.lower(), author.lower()) in existing_books:
            print(style(" Book already in the system!", ERROR))
            continue

        rating = None
        while True:
            raw_rating = input(style(" Rating (0-10, ↵ to skip): ", SECONDARY)).strip()

            try:
                if raw_rating:
                    rating = float(raw_rating)
                    if not 0 <= rating <= 10:
                        raise ValueError()
            except ValueError:
                error_message = (
                    "Nope, rating must be between 0 and 10 (decimals allowed)."
                )
                print(f"{PROMPT}{error_message}")
                continue

            break

        rating = rating if raw_rating else DEFAULT_RATING
        book = Book(title, author, rating)

        print(style("\n Adding: ", SECONDARY))
        print(f"  {style('–', SECONDARY)} {format_book(book, LINE_LENGTH - 5)}")
        if raw_rating:
            print(f"  - Rating: {rating}")

        print()
        confirm = prompt(p=f"{PROMPT}Confirm (y/n)? ")

        if confirm == "y":
            insert(book)
            new_books.append(book)
            existing_books.add((title.lower(), author.lower()))

        if len(books) + len(new_books) >= BOOK_LIMIT:
            print(f"\ {rule(LINE_LENGTH - 1, DIVIDER)}")
            return new_books

        next_action = prompt(p=f"{PROMPT}Add another book (y/n)? ")

        if next_action == "n":
            print()
            if len(new_books) > 0:
                print(f" {rule(LINE_LENGTH - 1, DIVIDER)}")
            return new_books


def process_import(new_books, interrupted=False, method="CSV"):
    """Process import/new entries, display results and relevant messages."""
    first_import = not state.books
    added = len(new_books)

    if added > 0:
        state.books.extend(new_books)

        verb = "Imported" if method == "CSV" else "Added"
        plural = "s" if added > 1 else ""
        suffix = "!" if first_import or added > 100 else ":"
        message = style(f"✓ {verb} {added} book{plural}{suffix}", PRIMARY)

        print(f"{PROMPT}{message}")

        if not first_import and added <= 100:
            for i, book in enumerate(new_books, start=1):
                print(
                    f"     {style(f'{i}.', SECONDARY)}"
                    f" {format_book(book, LINE_LENGTH - 9)}"
                )

        if interrupted:
            print(import_interrupted(added))
        elif len(state.books) >= BOOK_LIMIT and not first_import:
            print(LIMIT_WARNING)

        press_enter()
    elif added == 0 and method == "CSV":
        if not interrupted:
            print(EMPTY_IMPORT + "\n")
        if not first_import:
            press_enter(new_line=False)
