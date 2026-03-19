import os
import shutil
import sys
from datetime import datetime

import constants
import state
import theme
from constants import (
    EMPTY_IMPORT,
    EMPTY_LIBRARY,
    EXPORT_HEADER,
    GOODBYE,
    IMPORT_HEADER,
    IMPORT_INTERRUPTED,
    LIMIT_REACHED,
    LIMIT_WARNING,
    MAIN_MENU,
    QUIT_OPTION,
    TEST_MESSAGE,
    TITLE,
)
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db import init_db
from game import run_game
from leaderboard import (
    view_leaderboard,
)
from models import Book
from rich.console import Console
from scoring import calculate_progress
from theme import ACCENT, LINE_LENGTH, PROMPT, SECONDARY
from utils import (
    format_book,
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
        print(EMPTY_LIBRARY)

        while not state.books:
            print()
            response = csv_reader(prompt=" CSV file path (q to quit): ", back_key="q")
            if response == "q":
                quit_game()
            process_import(response)

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

        print(MAIN_MENU)
        print()

        choice = prompt(
            {"1", "2", "2 -v", "3", "4", "q", QUIT_OPTION},
            error_message=f"Nope, I can only read options 1-{QUIT_OPTION}.",
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
        elif choice in [QUIT_OPTION, "q"]:
            quit_game()

        if next_action == "q":
            quit_game()
        if next_action == "e":
            export_leaderboard()

        print()
        # Warn if running in test mode, which uses a separate test database
        if state.db_path == "data/test.db":
            print(TEST_MESSAGE)


def add_books():
    print()
    print(IMPORT_HEADER)

    if len(state.books) >= constants.BOOK_LIMIT:
        print(LIMIT_REACHED)
        press_enter()
        return
    print(" Please provide the path to your CSV book log to sync new books.")
    print()

    response = csv_reader(prompt=" CSV file path (b to go back): ", back_key="b")
    if response == "b":
        return

    process_import(response)


def process_import(filepath):
    """Process result form csv import, display results and relevant messages."""
    first_import = not state.books
    new_books, interrupted = import_from_csv(filepath)
    added = len(new_books)

    if added > 0:
        state.books = Book.load_all()

        suffix = "!" if first_import else ":"
        plural = "s" if added > 1 else ""
        print(f"{PROMPT}Imported {added} book{plural}{suffix}")

        if not first_import:
            for i, book in enumerate(new_books, start=1):
                print(
                    f"     {style(f'{i}.', SECONDARY)}"
                    f" {format_book(book, LINE_LENGTH - 9)}"
                )

        if interrupted:
            print(IMPORT_INTERRUPTED)
        elif len(state.books) >= constants.BOOK_LIMIT:
            print(LIMIT_WARNING)

        press_enter(new_line=False)
    else:
        print(EMPTY_IMPORT)


def export_leaderboard():
    print()
    print(EXPORT_HEADER)
    print(leaderboard_summary(state.current_progress, theme.PRIMARY))

    print()
    print(" Proceed with export (y/n)?")
    choice = prompt({"y", "n"}, "Sorry, I can only understand 'y' or 'n'.")

    if choice == "y":
        export_to_csv()
        press_enter(new_line=False)


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
    for old in backups[: -constants.BACKUPS_LIMIT]:
        os.remove(os.path.join(backup_dir, old))


if __name__ == "__main__":
    if "--test" in sys.argv:
        # state.db_path = "data/test.db"
        state.db_path = "data/test2.db"
    if "--debug" in sys.argv:
        state.debug = True

    init_db()
    state.books = Book.load_all()
    startup()
