import os
import shutil
import sys
from datetime import datetime

import state
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db.books_repo import get_all
from db.connection import init_db
from game import run_game
from leaderboard import (
    view_leaderboard,
)
from library_management import add_books, process_import, reset_handler
from services.scoring_service import calculate_progress
from ui import (
    ACCENT,
    BACKUPS_LIMIT,
    CSV_INSTRUCTIONS,
    GOODBYE,
    LINE_WIDTH,
    MAIN_MENU,
    MAIN_OPTIONS,
    ONBOARDING,
    PRIMARY,
    PROMPT,
    SECONDARY,
    TEST_MESSAGE,
    TITLE,
    rule,
    style,
)
from utils import (
    header,
    library_summary,
    press_enter,
    progress_bar,
    prompt,
)


def startup():
    """Print the startup message and display the main menu.

    If no books are in the system, prompt the user to import from a CSV.
    """
    state.books = get_all()

    os.system("cls" if os.name == "nt" else "clear")
    print("\n" + TITLE)

    # Warn if running in test mode, which uses a separate test database
    if "test" in state.db_path:
        print(TEST_MESSAGE)

    # First run, no books in the system - prompt for CSV import
    first_run = not state.books
    if first_run:
        print(ONBOARDING)
        print(CSV_INSTRUCTIONS)

        while not state.books:
            filepath = csv_reader(
                prompt=f"\n {style('CSV file path (q to quit): ', SECONDARY)}",
                back_key="q",
            )
            if filepath == "q":
                quit_game(state.books, state.db_path)
            new_books, interrupted = import_from_csv(filepath, state.books)
            process_import(new_books, state.books, interrupted)

        print()

    state.progress = calculate_progress(state.books)
    main_menu(first_run)


def main_menu(first_run=False):
    """Display the main menu and handle user input."""
    while True:
        if not first_run:
            confidence_progress = f"  PROGRESS: {progress_bar(state.progress, 20)}  "
            line = rule((LINE_WIDTH - len(confidence_progress) - 1) // 2, ACCENT)
            print(f" {line}{style(confidence_progress, ACCENT)}{line}")

        print(header("MAIN MENU"))
        print(MAIN_MENU)

        choice = prompt(
            options=MAIN_OPTIONS,
            error_message=f"Nope, I can only read options 1-{MAIN_OPTIONS[-1]}.",
        )
        next_action = ""

        if choice == "1":
            next_action = run_game(state.books)
            state.progress = calculate_progress(state.books)
        elif choice in ("2", "2 -v"):
            next_action = view_leaderboard(state.books, verbose="-v" in choice)
        elif choice == "3":
            add_books(state.books)
            state.progress = calculate_progress(state.books)
        elif choice == "4":
            export_leaderboard(state.books)
        elif choice == "5":
            next_action = reset_handler(state.books, state.db_path)
            if next_action == "q":
                state.books = []
                state.progress = calculate_progress(state.books)
        elif choice in ["6", "q"]:
            quit_game(state.books, state.db_path)

        if next_action == "q":
            quit_game(state.books, state.db_path)
        if next_action == "e":
            export_leaderboard(state.books)

        first_run = False
        print()
        # Warn if running in test mode, which uses a separate test database
        if state.db_path == "data/test.db":
            print(TEST_MESSAGE)


def export_leaderboard(books):
    print(header("EXPORT LEADERBOARD", new_line=True))
    print(library_summary(len(books), calculate_progress(books), PRIMARY))

    print()
    choice = prompt(
        p=f"{PROMPT}Proceed with export (y/n)? ",
        error_message="Sorry, I can only understand 'y' or 'n'.",
    )

    if choice == "y":
        export_to_csv(books)
        press_enter(new_line=False)


# --- QUITTING AND BACKUPS  ---


def quit_game(books, db_path):
    """Quit the program and perform any necessary backups."""
    if books:
        backup_db(db_path)
        backup_cleanup(BACKUPS_LIMIT, db_path)
    print("\n" + GOODBYE + "\n")
    sys.exit()


def backup_db(db_path):
    """Back up the current database."""
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)

    current_db = os.path.splitext(os.path.basename(db_path))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{current_db}_{timestamp}.db")

    shutil.copy(db_path, backup_path)


def backup_cleanup(limit, db_path):
    """Only keep the last N backups for the current database."""
    backup_dir = "backup"
    current_db = os.path.splitext(os.path.basename(db_path))[0]

    all_backups = sorted(os.listdir(backup_dir))
    relevant_backups = [f for f in all_backups if f.startswith(f"backup_{current_db}_")]

    for db in relevant_backups[:-limit]:
        os.remove(os.path.join(backup_dir, db))


if __name__ == "__main__":
    if "--beta" in sys.argv:
        state.db_path = "data/beta.db"
    if "--demo1" in sys.argv:
        state.db_path = "data/demo1.db"
    if "--demo2" in sys.argv:
        state.db_path = "data/demo2.db"
    if "--test" in sys.argv:
        state.db_path = "data/test.db"

    init_db(state.db_path)
    startup()
