import os
import shutil
import sys
from datetime import datetime

import state
from csv_handler import import_from_csv, export_to_csv
from db import init_db
from display import (
    view_rankings,
    progress_bar,
    calculate_rankings_confidence,
    MAIN_MENU,
    LINE_LENGTH,
    TEST_MESSAGE,
    MENU_OPTIONS,
)
from game import run_game
from models import Book


def startup():
    """Print the startup message and display the main menu.

    If no books are in the system, prompt the user to import from a CSV.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"\n\033[1;32m{'–' * (LINE_LENGTH // 2 - 7)} "
        f"BOOK RANKER "
        f"{'–' * (LINE_LENGTH // 2 - 6)}\033[0m"
    )

    if state.db_path == "data/test.db":
        print(TEST_MESSAGE)

    # First run, no books in the system - prompt for CSV import
    if state.book_count == 0:
        print(
            " Your library is empty!\n"
            " Please provide the path to a CSV file of your book log to get started.\n"
            " It should have the following columns: 'title', 'author', 'rating'.\n"
        )
        csv_reader()
        state.books = Book.load_all()
        state.book_count = len(state.books)
    else:
        calculate_rankings_confidence()

    main_menu()


def main_menu():
    """Display the main menu and handle user input."""
    while True:
        rankings_progress = (
            f" CONFIDENCE: {progress_bar(state.rankings_confidence, 20)} "
        )
        padding = (LINE_LENGTH - len(rankings_progress) - 1) // 2
        print(f" \033[1;33m{'–' * padding}{rankings_progress}{'–' * padding}\033[0m")

        print(MAIN_MENU)

        if state.db_path == "data/test.db":
            print(TEST_MESSAGE)

        choice = input("\n\033[1;33m > \033[0m").strip()
        next_action = ""

        if choice == "1":
            next_action = run_game()
            calculate_rankings_confidence()
        elif choice in ("2", "2 -v"):
            next_action = view_rankings("-v" in choice)
        elif choice == "3":
            add_books()
        elif choice == "4":
            export_to_csv()
        elif choice == MENU_OPTIONS:
            quit_game()
        else:
            print(
                f"\033[31m Invalid choice, "
                f"I can only read options 1-{MENU_OPTIONS}.\033[0m"
            )

        if next_action == "q":
            quit_game()
        if next_action == "e":
            export_to_csv()

        print()


def add_books():
    print(" Please provide the path to your CSV book log to sync new books.")
    csv_reader()
    state.books = Book.load_all()
    state.book_count = len(state.books)


def csv_reader():
    while True:
        filepath = input(" CSV file path (b to go back): ").strip()
        if filepath == "b":
            print()
            break

        if not (filepath and os.path.exists(filepath)):
            print(" Invalid path. Please try again.\n")
            continue

        if not filepath.endswith(".csv"):
            print(
                " That doesn't look like a CSV."
                " Please provide the full path to your CSV file.\n"
            )
            continue

        count = import_from_csv(filepath)
        if count > 0:
            print(f" Imported {count} books!")
            print()
            return
        else:
            print(" No books imported. Please check your file and try again.\n")


# --- QUITTING AND BACKUPS  ---


def quit_game():
    backup_db()
    backup_cleanup()
    print(
        f"\n\033[1;32m{'–' * (LINE_LENGTH // 2 - 15)} "
        f"📚 Goodbye! Keep on reading 📚 "
        f"{'–' * (LINE_LENGTH // 2 - 16)}\033[0m\n"
    )
    sys.exit()


def backup_db():
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

    shutil.copy(state.db_path, backup_path)


def backup_cleanup(keep=5):
    """Only keep the last N backups."""
    backup_dir = "backup"
    backups = sorted(os.listdir(backup_dir))
    for old in backups[:-keep]:
        os.remove(os.path.join(backup_dir, old))


if __name__ == "__main__":
    if "--test" in sys.argv:
        state.db_path = "data/test.db"
    if "--debug" in sys.argv:
        state.debug = True

    init_db()
    state.books = Book.load_all()
    state.book_count = len(state.books)
    startup()
