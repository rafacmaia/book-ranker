import os
import shutil
import sys
from datetime import datetime

from rich.console import Console

import constants
import state
from constants import (
    ACCENT,
    EMPTY_IMPORT,
    EMPTY_LIBRARY,
    EXPORT_HEADER,
    GOODBYE,
    IMPORT_HEADER,
    IMPORT_INTERRUPTED,
    LIMIT_REACHED,
    LIMIT_WARNING,
    LINE_LENGTH,
    MAIN_MENU,
    QUIT_OPTION,
    SUBHEADER,
    TEST_MESSAGE,
    TITLE,
)
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db import init_db
from game import run_game
from models import Book
from rankings import (
    view_rankings,
)
from scoring import calculate_rankings_confidence
from utils import PROMPT, progress_bar, prompt, rankings_summary, rule, style

console = Console(width=LINE_LENGTH)


def startup():
    """Print the startup message and display the main menu.

    If no books are in the system, prompt the user to import from a CSV.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print(TITLE)

    # Warn if running in test mode, which uses a separate test database
    if state.db_path == "data/test.db":
        print(TEST_MESSAGE)

    # First run, no books in the system - prompt for CSV import
    if not state.books:
        print(EMPTY_LIBRARY)
        response = csv_reader(prompt=" CSV file path (q to quit): ", back_key="q")
        if response == "q":
            quit_game()
        import_from_csv(response)
        state.books = Book.load_all()
        print()
    else:
        calculate_rankings_confidence()

    main_menu()


def main_menu():
    """Display the main menu and handle user input."""
    while True:
        confidence_progress = (
            f"  CONFIDENCE: {progress_bar(state.rankings_confidence, 20)}  "
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
            {"1", "2", "2 -v", "3", "4", QUIT_OPTION},
            f"Invalid choice, I can only read options 1-{QUIT_OPTION}.",
        )
        next_action = ""

        if choice == "1":
            next_action = run_game()
            calculate_rankings_confidence()
        elif choice in ("2", "2 -v"):
            next_action = view_rankings("-v" in choice)
        elif choice == "3":
            add_books()
            calculate_rankings_confidence()
        elif choice == "4":
            export_rankings()
        elif choice == QUIT_OPTION:
            quit_game()

        if next_action == "q":
            quit_game()
        if next_action == "e":
            export_rankings()

        print()
        # Warn if running in test mode, which uses a separate test database
        if state.db_path == "data/test.db":
            print(TEST_MESSAGE)


def add_books():
    print()
    print(IMPORT_HEADER)

    if len(state.books) >= constants.BOOK_LIMIT:
        print(LIMIT_REACHED)
        return
    print(" Please provide the path to your CSV book log to sync new books.")
    print()

    response = csv_reader(prompt=" CSV file path (b to go back): ", back_key="b")
    if response == "b":
        return

    added, interrupted = import_from_csv(response)

    if added > 0:
        print(f"{PROMPT}Imported {added} book{'s' if added > 1 else ''}!")
        state.books = Book.load_all()
    else:
        print(EMPTY_IMPORT)
        input(
            f"{PROMPT}{style('Press Enter to return to the main menu... ', SUBHEADER)}"
        )

    if interrupted:
        print(IMPORT_INTERRUPTED)
    elif len(state.books) >= constants.BOOK_LIMIT:
        print(LIMIT_WARNING)


def export_rankings():
    print()
    print(EXPORT_HEADER)
    print(rankings_summary(state.rankings_confidence, constants.HEADER))

    print()
    print(" Proceed with export (y/n)?")
    choice = prompt({"y", "n"}, "Sorry, I can only understand 'y' or 'n'.")

    if choice == "y":
        export_to_csv()
        input(
            f"{PROMPT}{style('Press Enter to return to the main menu... ', SUBHEADER)}"
        )


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
