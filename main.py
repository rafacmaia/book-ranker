import os

from db import init_db
from display import print_rankings, MAIN_MENU
import state

from models import Book
from importer import import_from_csv
from game import run, quit_game


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
                " That doesn't look like a CSV file. Please provide the full path to your CSV file.\n"
            )
            continue

        count = import_from_csv(filepath)
        if count > 0:
            print(f" Imported {count} books!")
            print()
            return
        else:
            print(" No books imported. Please check your file and try again.\n")


def startup():
    print(f"\n\033[1;32m{'–' * 40} BOOK RANKER {'–' * 40}\033[0m")
    # print(f"\033[1;32m{'|'*37}\033[0m")
    # print("\033[1;32m–––––––––––––––––––––––––––––––––––––\033[0m")

    # First run, no books in the system - prompt for CSV import
    if state.book_count == 0:
        print(" Your library is empty!")
        print(" Please provide the path to a CSV file of your book log to get started.")
        print(" It should have the following columns: 'title', 'author', 'rating'.\n")
        csv_reader()
        state.books = Book.load_all()
        state.book_count = len(state.books)

    main_menu()


def main_menu():
    while True:
        print(MAIN_MENU)

        choice = input("\n\033[1;33m > \033[0m").strip()
        if choice == "1":
            run()
        elif choice == "2":
            print_rankings()
        elif choice == "2 -v":
            print_rankings(verbose=True)
        elif choice == "3":
            print(" Please provide the path to your CSV book log to sync new books.")
            csv_reader()
            state.books = Book.load_all()
            state.book_count = len(state.books)
        elif choice == "4":
            quit_game()
        else:
            print(" Invalid choice, I can only read options 1-4.")

        print()


if __name__ == "__main__":
    init_db()
    state.books = Book.load_all()
    state.book_count = len(state.books)
    startup()
