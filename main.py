import os
import shutil
import sys
from datetime import datetime

from rich.console import Console

import state
from book_intake import add_books, process_import
from constants import (
    BACKUPS_LIMIT,
    MAIN_MENU,
    MAIN_OPTIONS,
    TEST_MESSAGE,
)
from csv_handler import csv_reader, export_to_csv, import_from_csv
from db.books_repo import get_all
from db.connection import init_db
from game import run_game
from leaderboard import (
    view_leaderboard,
)
from messages import (
    CSV_INSTRUCTIONS,
    GOODBYE,
    ONBOARDING,
    TITLE,
)
from services.scoring_service import calculate_progress
from theme import ACCENT, ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import (
    header,
    library_summary,
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
    state.books = get_all()

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
            filepath = csv_reader(
                prompt=f"\n {style('CSV file path (q to quit): ', SECONDARY)}",
                back_key="q",
            )
            if filepath == "q":
                quit_game()
            new_books, interrupted = import_from_csv(filepath, state.books)
            process_import(new_books, interrupted)

        print()

    state.progress = calculate_progress(state.books)
    main_menu(first_run)


def main_menu(first_run=False):
    """Display the main menu and handle user input."""
    while True:
        if not first_run:
            confidence_progress = f"  PROGRESS: {progress_bar(state.progress, 20)}  "

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
            reset_handler()
        elif choice in ["6", "q"]:
            quit_game()

        if next_action == "q":
            quit_game()
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
        export_to_csv(state.books)

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
    state.progress = calculate_progress(state.books)

    return True, None


# --- QUITTING AND BACKUPS  ---


def quit_game():
    """Quit the program and perform any necessary backups."""
    if state.books:
        backup_db(state.db_path)
        backup_cleanup(BACKUPS_LIMIT, state.db_path)
    print("\n" + GOODBYE + "\n")
    sys.exit()


def backup_db(filepath):
    """Back up the current database."""
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)

    current_db = os.path.splitext(os.path.basename(filepath))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{current_db}_{timestamp}.db")

    shutil.copy(state.db_path, backup_path)


def backup_cleanup(limit, filepath):
    """Only keep the last N backups for the current database."""
    backup_dir = "backup"
    current_db = os.path.splitext(os.path.basename(filepath))[0]

    all_backups = sorted(os.listdir(backup_dir))
    relevant_backups = [f for f in all_backups if f.startswith(f"backup_{current_db}_")]

    for db in relevant_backups[:-limit]:
        os.remove(os.path.join(backup_dir, db))


if __name__ == "__main__":
    if "--test" in sys.argv:
        # state.db_path = "data/test.db"
        state.db_path = "data/test2.db"
    if "--demo1" in sys.argv:
        state.db_path = "data/demo1.db"
    if "--demo2" in sys.argv:
        state.db_path = "data/demo2.db"

    init_db(state.db_path)
    startup()
