import os

from config import BOOK_LIMIT, DEFAULT_RATING
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db.books_repo import insert
from models import Book
from ui import (
    CSV_INSTRUCTIONS,
    DIVIDER,
    EMPTY_IMPORT,
    ERROR,
    IMPORT_MENU,
    LIMIT_WARNING,
    LINE_WIDTH,
    MANUAL_INSTRUCTIONS,
    ONBOARDING,
    ONBOARDING_MENU,
    PRIMARY,
    PROMPT,
    SECONDARY,
    import_interrupted,
    limit_reached,
    rule,
    style,
)
from utils import format_book, header, press_enter, prompt

# ====== ADDING BOOKS


def onboarding(books):
    """Handle the onboarding process of adding books for the first time."""
    print(ONBOARDING)

    while not books:
        print(ONBOARDING_MENU)
        choice = prompt(options=["1", "2", "q"])

        if choice == "q":
            return False
        elif choice == "1":
            new_books = _manual_entry(books)
            _process_import(new_books, books, method="manual")
            print()
        elif choice == "2":
            print(CSV_INSTRUCTIONS)

            filepath = csv_reader(
                prompt=f"\n {style('CSV file path (b to go back): ', SECONDARY)}",
                back_key="b",
            )

            if filepath == "b":
                print("\n" + rule(LINE_WIDTH - 1, DIVIDER))
                continue

            new_books, interrupted = import_from_csv(filepath, books)
            _process_import(new_books, books, interrupted)

            print()

    return True


def add_books(books):
    """Add new books to the library either through a CSV import or manual entry."""
    print(header("BOOK ENTRY", new_line=True))

    if len(books) >= BOOK_LIMIT:
        print(limit_reached(BOOK_LIMIT))
        press_enter()
        return

    while True:
        print(IMPORT_MENU)
        choice = prompt(options=["1", "2", "b"])

        if choice == "b":
            return
        elif choice == "1":
            new_books = _manual_entry(books)
            _process_import(new_books, books, method="manual")
            break
        elif choice == "2":
            print(CSV_INSTRUCTIONS)

            filepath = csv_reader(
                prompt=f"\n {style('CSV file path (b to go back):', SECONDARY)} ",
                back_key="b",
            )

            if filepath == "b":
                print(f"\n {rule(LINE_WIDTH - 1, DIVIDER)}")
                continue

            print(f"\n {style('Processing file...', SECONDARY)}")
            new_books, interrupted = import_from_csv(filepath, books)

            print()
            _process_import(new_books, books, interrupted, method="CSV")
            break


def _manual_entry(books):
    """Add new books to the library one at a time via user input."""
    existing_books = {(b.title.lower(), b.author.lower()) for b in books}
    new_books = []

    print(MANUAL_INSTRUCTIONS)
    press_enter(message="Press Enter to start... ")

    while True:
        count = len(new_books) + 1

        print()
        print(
            f" {rule((LINE_WIDTH - 5 - len(str(count))), DIVIDER)}"
            f" {style(count, DIVIDER)}"
            f" {rule(2, DIVIDER)}"
        )

        title = input(style(" Title:  ", SECONDARY)).strip()

        if not title:
            print(f"\n {rule(LINE_WIDTH - 1, DIVIDER)}")
            return new_books

        author = input(style(" Author: ", SECONDARY)).strip()

        if (title.lower(), author.lower()) in existing_books:
            print(style(" Book already in the system!", ERROR))
            continue

        rating = None
        while True:
            raw_rating = input(style(" Rating (1-10, ↵ to skip): ", SECONDARY)).strip()

            try:
                if raw_rating:
                    rating = float(raw_rating)
                    if not 1 <= rating <= 10:
                        raise ValueError()
            except ValueError:
                error_message = "Nope, rating must be between 1 and 10 (decimals allowed), or blank."
                print(f"{PROMPT}{error_message}")
                continue

            break

        rating = rating if raw_rating else DEFAULT_RATING
        book = Book(title, author, rating)

        print(style("\n Adding:", SECONDARY), format_book(book, LINE_WIDTH - 9))
        if raw_rating:
            print(f" {style('Rating:', SECONDARY)} {rating}")

        print()
        confirm = prompt(p=f"{PROMPT}{style('Confirm (y/n)? ', SECONDARY)}")

        if confirm == "y":
            insert(book)
            new_books.append(book)
            existing_books.add((title.lower(), author.lower()))

        if len(books) + len(new_books) >= BOOK_LIMIT:
            print(f"\ {rule(LINE_WIDTH - 1, DIVIDER)}")
            return new_books


def _process_import(new_books, books, interrupted=False, method="CSV"):
    """Process import/new entries, display results and relevant messages."""
    first_import = not books
    added = len(new_books)

    if added > 0:
        books.extend(new_books)

        verb = "Imported" if method == "CSV" else "Added"
        plural = "s" if added > 1 else ""
        suffix = "!" if first_import or added > 100 else ":"
        message = style(f"✓ {verb} {added} book{plural}{suffix}", PRIMARY)

        print(f"{PROMPT}{message}")

        if not first_import and added <= 100:
            for i, book in enumerate(new_books, start=1):
                print(
                    f"     {style(f'{i}.', SECONDARY)}"
                    f" {format_book(book, LINE_WIDTH - 9)}"
                )

        if interrupted:
            print(import_interrupted(added))
        elif len(books) >= BOOK_LIMIT and not first_import:
            print(LIMIT_WARNING)

        press_enter()
    elif added == 0 and method == "CSV":
        if not interrupted:
            print(EMPTY_IMPORT + "\n")
        if not first_import:
            press_enter(new_line=False)


# ====== LIBRARY RESET


def reset_handler(books, db_path):
    print(header("FACTORY RESET", new_line=True))
    print(" This will delete all data and trigger a complete program reset.")
    print(style(" This cannot be undone. All data will be lost.", ERROR))

    print()
    export_choice = prompt(
        p=f"{PROMPT}Would you like to export the leaderboard before resetting (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if export_choice == "y":
        export_to_csv(books)

    print()
    reset_choice = prompt(
        p=f"{PROMPT}{style('Final warning:', ERROR)} Proceed with complete factory reset (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if reset_choice == "y":
        success, error = _reset(db_path)
        _process_reset(success, error)
        return "q"
    else:
        return None


def _reset(db_path):
    try:
        os.remove(db_path)
    except OSError as e:
        return False, str(e)

    return True, None


def _process_reset(success, error):
    if success:
        print(
            f"{PROMPT}✓ Reset complete. Restart the app to start book brawling again."
        )
        press_enter(message="Press Enter to quit... ", new_line=False)
    else:
        print(f"{PROMPT}{style(f'Reset failed: {error}.', ERROR)}")
        press_enter(
            message="Please try again. Press Enter for the main menu... ",
            new_line=False,
        )
