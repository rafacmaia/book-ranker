import random
import textwrap

import state
from db import save_comparison, get_unique_opponent_count, get_past_opponents
from display import GAME_MENU, LINE_LENGTH


def run_game():
    """Run the game's main loop.

    Select two books for comparison, prompt the user for selection between the two,
    resolve the match, and repeat until the user stops.
    """
    print(GAME_MENU)

    match_count = 1
    book_a, book_b = select_opponents()

    while True:
        print(
            f"\n\033[1;36m {'–' * (LINE_LENGTH - 5 - len(str(match_count)))}"
            f" {match_count} ––\033[0m"
        )
        print(f"\033[1;33m Which means more to you?\033[0m")
        print(f"   \033[1;33m1.\033[0m {format_book(book_a)}")
        print(f"   \033[1;33m2.\033[0m {format_book(book_b)}")
        choice = input("\033[1;33m > \033[0m").strip().lower()

        if choice == "q":
            return "q"
        elif choice == "b":
            return "b"
        elif choice == "1":
            resolve_comparison(winner=book_a, loser=book_b)
        elif choice == "2":
            resolve_comparison(winner=book_b, loser=book_a)
        else:
            print(
                "\033[1;31m ⚠️ Invalid choice - "
                "try '1', '2', 'b', or 'q' to quit.\033[0m"
            )
            continue

        book_a, book_b = select_opponents()
        match_count += 1


def select_opponents():
    """Select two books using weighted random selection.

    Favor low-confidence books, i.e., books with fewer unique matches played, and
    books that have been matched against each other less often, to maximize information
    gained from each match.
    """
    unique_opponent_count = get_unique_opponent_count()

    # Calculate weights based on confidence level, ensuring a minimum weight of 0.1
    weights = [
        max(0.1, 1 - (unique_opponent_count.get(book.id, 0) / (state.book_count - 1)))
        for book in state.books
    ]

    book_a = random.choices(state.books, weights=weights, k=1)[0]
    past_opponents = get_past_opponents(book_a)

    # DEBUG MODE: Print number of past opponents
    if state.debug:
        print(f"\nDEBUG: {book_a.title} has {len(past_opponents)} past opponents")

    # Exclude book_a from opponent selection
    remaining_book_weights = [
        (b, w) for b, w in zip(state.books, weights) if b.id != book_a.id
    ]

    # Adjust weights to account for opponents already matched against book_a
    adjusted_weights = [
        w / (1 + past_opponents.get(b.id, 0)) for (b, w) in remaining_book_weights
    ]

    book_b = random.choices(
        [b for b, w in remaining_book_weights], weights=adjusted_weights, k=1
    )[0]

    return book_a, book_b


def format_book(book):
    return textwrap.fill(str(book), width=LINE_LENGTH - 6, subsequent_indent="\t")


def resolve_comparison(winner, loser):
    new_winner_elo, new_loser_elo = calculate_elo(winner, loser)
    save_comparison(winner.id, loser.id)
    winner.update_elo(new_winner_elo)
    loser.update_elo(new_loser_elo)


def calculate_elo(winner, loser):
    unique_opponents = get_unique_opponent_count()
    winner_k = get_k(unique_opponents.get(winner.id, 0))
    loser_k = get_k(unique_opponents.get(loser.id, 0))

    expected_w = expected_score(winner.elo, loser.elo)
    expected_l = expected_score(loser.elo, winner.elo)
    new_winner_elo = round(winner.elo + winner_k * (1 - expected_w))
    new_loser_elo = round(loser.elo + loser_k * (0 - expected_l))

    return new_winner_elo, new_loser_elo


def get_k(unique_opponents):
    """Calculates and returns k value based on the percentage of unique opponents, i.e.,
    confidence level.
    """
    pct = unique_opponents / (state.book_count - 1)
    if pct < 0.20:
        return 40
    elif pct < 0.40:
        return 30
    else:
        return 20


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
