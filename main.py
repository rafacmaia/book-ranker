import os
import shutil
import sys
from datetime import datetime

from rich.console import Console

import state
from constants import (
    BACKUPS_LIMIT,
    BOOK_LIMIT,
    DEFAULT_RATING,
    MAIN_MENU,
    MAIN_OPTIONS,
    TEST_MESSAGE,
)
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db.connection import init_db
from game import run_game
from leaderboard import (
    view_leaderboard,
)
from messages import (
    CSV_INSTRUCTIONS,
    EMPTY_IMPORT,
    GOODBYE,
    IMPORT_INTERRUPTED,
    IMPORT_MENU,
    LIMIT_REACHED,
    LIMIT_WARNING,
    ONBOARDING,
    TITLE,
)
from models import Book
from scoring import calculate_progress
from theme import ACCENT, DIVIDER, ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import (
    format_book,
    header,
    leaderboard_summary,
    press_enter,
    progress_bar,
    prompt,
    rule,
    style,
)

console = Console(width=LINE_LENGTH)


def startup():
    """Print the startup message and display the main menu.

    If no books are in the system, prompt the user to import from a CSV.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print(TITLE)

    # Warn if running in test mode, which uses a separate test database
    if "test" in state.db_path:
        print(TEST_MESSAGE)

    # First run, no books in the system - prompt for CSV import
    first_run = not state.books
    if first_run:
        print(ONBOARDING)
        print(CSV_INSTRUCTIONS)

        while not state.books:
            filepath = csv_reader(prompt="\n CSV file path (q to quit): ", back_key="q")
            if filepath == "q":
                quit_game()
            new_books, interrupted = import_from_csv(filepath)
            process_import(new_books, interrupted)

        print()

    calculate_progress()
    main_menu(first_run)


def main_menu(first_run=False):
    """Display the main menu and handle user input."""
    while True:
        if not first_run:
            confidence_progress = (
                f"  PROGRESS: {progress_bar(state.current_progress, 20)}  "
            )

            padding = (LINE_LENGTH - len(confidence_progress) - 1) // 2
            print(
                f" {rule(padding, ACCENT)}"
                f"{style(confidence_progress, ACCENT)}"
                f"{rule(padding, ACCENT)}"
            )

        print(header("MAIN MENU"))
        print(MAIN_MENU)

        choice = prompt(
            options=MAIN_OPTIONS,
            error_message=f"Nope, I can only read options 1-{MAIN_OPTIONS[-1]}.",
        )
        next_action = ""

        if choice == "1":
            next_action = run_game()
            calculate_progress()
        elif choice in ("2", "2 -v"):
            next_action = view_leaderboard(verbose="-v" in choice)
        elif choice == "3":
            add_books()
            calculate_progress()
        elif choice == "4":
            export_leaderboard()
        elif choice == "5":
            reset_handler()
        elif choice in ["6", "q"]:
            quit_game()

        if next_action == "q":
            quit_game()
        if next_action == "e":
            export_leaderboard()

        first_run = False
        print()
        # Warn if running in test mode, which uses a separate test database
        if state.db_path == "data/test.db":
            print(TEST_MESSAGE)


def add_books():
    print(header("IMPORT NEW BOOKS", new_line=True))

    if len(state.books) >= BOOK_LIMIT:
        print(LIMIT_REACHED)
        press_enter()
        return

    while True:
        print(IMPORT_MENU)
        choice = prompt(options=["1", "2", "b"])

        if choice == "1":
            new_books = manual_entry()
            process_import(new_books, method="manual")
            break
        elif choice == "2":
            print(f"\n {rule(LINE_LENGTH - 1, DIVIDER)}")
            print(" Please provide the path to your CSV file to sync new books.")
            print(CSV_INSTRUCTIONS)

            filepath = csv_reader(
                prompt="\n CSV file path (b to go back): ", back_key="b"
            )
            if filepath == "b":
                print(f"\n {rule(LINE_LENGTH - 1, DIVIDER)}")
                continue

            print("\n Processing file...")
            new_books, interrupted = import_from_csv(filepath)
            print()
            process_import(new_books, interrupted, method="CSV")
            break
        elif choice == "b":
            return


def manual_entry():
    existing_books = {(b.title.lower(), b.author.lower()) for b in state.books}
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
        print(f"  - {format_book(book, LINE_LENGTH - 5)}")
        if raw_rating:
            print(f"  - Rating: {rating}")

        print()
        confirm = prompt(p=f"{PROMPT}Confirm (y/n)? ")

        if confirm == "y":
            book.save()
            new_books.append(book)
            existing_books.add((title.lower(), author.lower()))

        if len(state.books) + len(new_books) >= BOOK_LIMIT:
            print(f"\ {rule(LINE_LENGTH - 1, DIVIDER)}")
            return new_books

        next_action = prompt(p=f"{PROMPT}Add another book (y/n)? ")

        if next_action == "n":
            print()
            if len(new_books) > 0:
                print(f" {rule(LINE_LENGTH - 1, DIVIDER)}")
            return new_books


def process_import(new_books, interrupted=False, method="CSV"):
    """Process result form csv import, display results and relevant messages."""
    first_import = not state.books
    added = len(new_books)

    if added > 0:
        state.books.extend(new_books)

        verb = "Imported" if method == "CSV" else "Added"
        plural = "s" if added > 1 else ""
        suffix = "!" if first_import or added > 100 else ":"

        print(f"{PROMPT}{verb} {added} book{plural}{suffix}")

        if not first_import and added <= 100:
            for i, book in enumerate(new_books, start=1):
                print(
                    f"     {style(f'{i}.', SECONDARY)}"
                    f" {format_book(book, LINE_LENGTH - 9)}"
                )

        if interrupted:
            print()
            print(IMPORT_INTERRUPTED)
        elif len(state.books) >= BOOK_LIMIT and not first_import:
            print()
            print(LIMIT_WARNING)

        press_enter()
    elif added == 0 and method == "CSV" and not interrupted:
        print(EMPTY_IMPORT)
        if not first_import:
            press_enter()


def export_leaderboard():
    print(header("EXPORT LEADERBOARD", new_line=True))
    print(leaderboard_summary(state.current_progress, PRIMARY))

    print()
    choice = prompt(
        p=f"{PROMPT}Proceed with export (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if choice == "y":
        export_to_csv()
        press_enter(new_line=False)


def reset_handler():
    print(header("FACTORY RESET", new_line=True))
    print(" This will delete all data and trigger a complete program reset.")
    print(style(" This cannot be undone. All data will be lost.", ERROR))

    print()
    export_choice = prompt(
        p=f"{PROMPT}Would you like to export the leaderboard before resetting (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if export_choice == "y":
        export_to_csv()

    print()
    reset_choice = prompt(
        p=f"{PROMPT}{style('Final warning:', ERROR)} Proceed with complete factory reset (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if reset_choice == "y":
        success, error = reset()
        if success:
            print(
                f"{PROMPT}✓ Reset complete. Restart the app to start book brawling again."
            )
            press_enter(message="Press Enter to quit... ", new_line=False)
            quit_game()
        else:
            print(f"{PROMPT}{style(f'Reset failed: {error}.', ERROR)}")
            press_enter(
                message="Please try again. Press Enter for the main menu... ",
                new_line=False,
            )


def reset():
    try:
        os.remove(state.db_path)
    except OSError as e:
        return False, str(e)

    state.books = []
    calculate_progress()

    return True, None


# --- QUITTING AND BACKUPS  ---


def quit_game():
    if state.books:
        backup_db()
        backup_cleanup()
    print()
    print(GOODBYE)
    print()
    sys.exit()


def backup_db():
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

    shutil.copy(state.db_path, backup_path)


def backup_cleanup():
    """Only keep the last N backups."""
    backup_dir = "backup"
    backups = sorted(os.listdir(backup_dir))
    for old in backups[:-BACKUPS_LIMIT]:
        os.remove(os.path.join(backup_dir, old))


if __name__ == "__main__":
    if "--debug" in sys.argv:
        state.debug = True
    if "--test" in sys.argv:
        # state.db_path = "data/test.db"
        state.db_path = "data/test2.db"
    if "--demo1" in sys.argv:
        state.db_path = "data/demo1.db"
    if "--demo2" in sys.argv:
        state.db_path = "data/demo2.db"

    init_db()
    state.books = Book.load_all()
    startup()
