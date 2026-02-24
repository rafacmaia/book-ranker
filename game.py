import os
import random
import shutil
import sys

import state

from db import save_comparison, get_unique_opponent_count
from display import GAME_MENU, LINE_WIDTH
from datetime import datetime


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def get_k(unique_opponents):
    pct = unique_opponents / (state.book_count - 1)
    if pct < 0.20:
        return 40
    elif pct < 0.40:
        return 30
    else:
        return 20


def calculate_elo(winner, loser):
    unique_opponents = get_unique_opponent_count()
    winner_k = get_k(unique_opponents.get(winner.id, 0))
    loser_k = get_k(unique_opponents.get(winner.id, 0))

    expected_w = expected_score(winner.elo, loser.elo)
    expected_l = expected_score(loser.elo, winner.elo)
    new_winner_elo = round(winner.elo + winner_k * (1 - expected_w))
    new_loser_elo = round(loser.elo + loser_k * (0 - expected_l))
    return new_winner_elo, new_loser_elo


def resolve_comparison(winner, loser):
    new_winner_elo, new_loser_elo = calculate_elo(winner, loser)
    save_comparison(winner.id, loser.id)
    winner.update_elo(new_winner_elo)
    loser.update_elo(new_loser_elo)


def run():
    print(GAME_MENU)

    match_count = 1
    book_a, book_b = select_opponents()
    while True:
        print(
            f"\n\033[1;34m{' ' * (LINE_WIDTH - 6 - len(str(match_count)))}–– {match_count} ––\033[0m"
        )
        print(f"\033[1;33m Which means more to you?\033[0m")
        print(f"   \033[1;33m1.\033[0m {book_a}")
        print(f"   \033[1;33m2.\033[0m {book_b}")
        choice = input("\033[1;33m > \033[0m").strip().lower()

        if choice == "q":
            quit_game()
        elif choice == "b":
            break
        elif choice == "1":
            resolve_comparison(winner=book_a, loser=book_b)
        elif choice == "2":
            resolve_comparison(winner=book_b, loser=book_a)
        else:
            print(
                "\033[1;31m ⚠️ Invalid choice - try '1', '2', 'b', or 'q' to quit.\033[0m"
            )
            continue

        book_a, book_b = select_opponents()
        match_count += 1


def select_opponents():
    """Select two books using weighted random selection favoring low-confidence books."""
    opponent_count = get_unique_opponent_count()
    weights = [
        1 - (opponent_count.get(book.id, 0) / (state.book_count - 1))
        for book in state.books
    ]

    # Avoid zero weights so books always have a minimum chance of being selected
    weights = [max(w, 0.1) for w in weights]

    book_a = random.choices(state.books, weights=weights, k=1)[0]
    remaining = [b for b in state.books if b.id != book_a.id]
    remaining_weights = [w for b, w in zip(state.books, weights) if b.id != book_a.id]
    book_b = random.choices(remaining, weights=remaining_weights, k=1)[0]

    return book_a, book_b


def quit_game():
    backup_db()
    backup_cleanup()
    print(
        f"\033[1;32m\n {'–' * (LINE_WIDTH // 2 - 16)} 📚Goodbye! Keep on reading 📚 {'–' * (LINE_WIDTH // 2 - 15)}\033[0m"
    )
    sys.exit()


def backup_db():
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

    shutil.copy("data/books.db", backup_path)


def backup_cleanup(keep=5):
    backup_dir = "backup"
    backups = sorted(os.listdir(backup_dir))
    for old in backups[:-keep]:
        os.remove(os.path.join(backup_dir, old))
