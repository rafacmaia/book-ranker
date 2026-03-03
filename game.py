import random
import textwrap

import state
from db import save_comparison
from display import GAME_MENU, LINE_LENGTH
from ranking import calculate_elo, confidence_score


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
        print(
            f"\033[1;33m Which means more to you?\033[0m\n"
            f"   \033[1;33m1.\033[0m {format_book(book_a)}\n"
            f"   \033[1;33m2.\033[0m {format_book(book_b)}"
        )
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

    Favor low-confidence books (i.e., books with fewer unique matches played), books
    that have been matched against each other less often, and books with similar Elo
    scores, to maximize information gained from each match.
    """
    # Calculate weights based on confidence level.
    weights = [sampling_weight(book) for book in state.books]

    book_a = random.choices(state.books, weights=weights, k=1)[0]

    # DEBUG MODE: Print number of past opponents
    if state.debug:
        print(
            f"\n\033[31mDEBUG: {book_a.title} "
            f"-- {len(book_a.opponents)} past opponents "
            f"-- {sampling_weight(book_a):.2f} weight\033[0m"
        )

    # Exclude book_a from opponent selection
    remaining_book_weights = [
        (b, w) for b, w in zip(state.books, weights) if b.id != book_a.id
    ]

    # Adjust weights to prioritize rarer pairings and books with similar Elo scores.
    # Rematch penalty: increase the multiplier to penalize rematches more aggressively
    # Elo gap penalty: decrease the divisor to prioritize similar score ranges
    adjusted_weights = []
    for b, w in remaining_book_weights:
        rematch_penalty = 1 + 2 * book_a.opponents.get(b.id, 0)
        elo_gap_penalty = 1 + abs(book_a.elo - b.elo) / 150
        adjusted_weights.append(max(0.1, w / rematch_penalty / elo_gap_penalty))

    book_b = random.choices(
        [b for b, w in remaining_book_weights], weights=adjusted_weights, k=1
    )[0]

    return book_a, book_b


def sampling_weight(book):
    """Calculate selection weight based on confidence level, ensuring a minimum weight
    of 0.1, and highly prioritizing books with fewer than a threshold number of matches.
    """
    if state.b_count <= 1:
        return 1

    total_opponents = state.b_count - 1
    faced_opponents = len(book.opponents)

    early_boost = 2.5 * (0.4 ** (faced_opponents / (total_opponents * 0.1)))
    confidence_weight = 1 - confidence_score(book)
    return max(0.1, confidence_weight, early_boost)


def format_book(book):
    return textwrap.fill(str(book), width=LINE_LENGTH - 6, subsequent_indent="\t")


def resolve_comparison(winner, loser):
    new_winner_elo, new_loser_elo = calculate_elo(winner, loser)
    save_comparison(winner.id, loser.id)

    winner.update_elo(new_winner_elo)
    loser.update_elo(new_loser_elo)

    winner.record_opponent(loser.id)
    loser.record_opponent(winner.id)
