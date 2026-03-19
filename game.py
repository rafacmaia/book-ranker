import random
from collections import namedtuple

import state
from constants import (
    PIT_HEADER,
    PIT_INSTRUCTIONS,
    PIT_OPTIONS,
)
from db import save_comparison
from scoring import calculate_elo, confidence_score
from theme import ACCENT, DIVIDER, LINE_LENGTH, PRIMARY, PROMPT, REDO, SECONDARY
from utils import format_book, prompt, rule, style

PendingMatch = namedtuple("PendingMatch", ["match", "a", "b", "choice"])


def run_game():
    """Run the game's main loop.

    Select two books for comparison, prompt the user for choice between the two,
    resolve the match, and repeat until the user stops.
    """
    print(PIT_HEADER)
    print(
        f" {style(len(state.books), SECONDARY)} books entered. {style('One wins.', SECONDARY)}"
    )
    print(PIT_INSTRUCTIONS, end="")
    input()

    match_count = 1
    book_a, book_b = select_opponents()
    previous = None
    selected = True
    while True:
        if not selected:
            match_count += 1
            book_a, book_b = select_opponents()

        print_match(match_count, book_a, book_b)
        choice = prompt(PIT_OPTIONS)

        while choice == "u" and not previous:
            print(f"{PROMPT}No previous match to undo.")
            choice = prompt(PIT_OPTIONS)

        if choice == "u":
            print_match(previous.match, previous.a, previous.b, redo=True)
            new_choice = prompt(["1", "2"])
            previous = PendingMatch(previous.match, previous.a, previous.b, new_choice)
            selected = True
            continue

        if previous:
            resolve_comparison(previous.a, previous.b, previous.choice)

        if choice in ["q", "b"]:
            return choice

        previous = PendingMatch(match_count, book_a, book_b, choice)

        selected = False


def select_opponents():
    """Select two books using weighted random selection.

    Favor low-confidence books (i.e., books with fewer unique matches played), books
    that have been matched against each other less often, and books with similar Elo
    scores, to maximize information gained from each match.
    """
    # Calculate weights based on confidence level.
    weights = [sampling_weight(book) for book in state.books]

    book_a = random.choices(state.books, weights=weights, k=1)[0]

    # Exclude book_a from opponent selection
    remaining_weights = [
        (b, w) for b, w in zip(state.books, weights) if b.id != book_a.id
    ]

    # Adjust weights for book_b selection based on the selected book_a
    adjusted_weights = adjust_weights(book_a, remaining_weights)

    book_b = random.choices(
        [b for b, w in remaining_weights], weights=adjusted_weights, k=1
    )[0]

    return book_a, book_b


def sampling_weight(book):
    """Calculate selection weight based on confidence level, ensuring a minimum weight
    of 0.1, and highly prioritizing books with fewer than a threshold number of matches.
    """
    if len(state.books) <= 1:
        return 1

    total_opponents = len(state.books) - 1
    faced_opponents = len(book.opponents)

    early_boost = 10 * (0.20 ** (faced_opponents / (total_opponents * 0.1)))
    confidence_weight = 1 - confidence_score(book)
    return max(0.1, confidence_weight, early_boost)


def adjust_weights(book_a, weights):
    # Adjust weights to prioritize rarer pairings and books with similar Elo scores.
    # Rematch penalty: increase the multiplier to penalize rematches more aggressively
    # Elo gap penalty: decrease the divisor to prioritize similar score ranges
    adjusted_weights = []
    for b, w in weights:
        rematch_penalty = 1 + 2 * book_a.opponents.get(b.id, 0)
        elo_gap_penalty = 1 + abs(book_a.elo - b.elo) / 150
        adjusted_weights.append(max(0.1, w / rematch_penalty / elo_gap_penalty))

    return adjusted_weights


def print_match(match_count, book_a, book_b, redo=False):
    match_header = (
        f" {rule((LINE_LENGTH - 5 - len(str(match_count))), DIVIDER)}"
        f" {style(match_count, DIVIDER)}"
        f" {rule(2, DIVIDER)}"
    )

    redo_header = (
        f" {rule(2, REDO)}"
        f" {style('REMATCH', REDO)}"
        f" {rule((LINE_LENGTH - 16 - len(str(match_count))), REDO)}"
        f" {style(match_count, REDO)}"
        f" {rule(2, REDO)}"
    )

    match = (
        f" {style('Which means more to you?', SECONDARY)}\n"
        f"   {style('1.', SECONDARY)} {format_book(book_a)}\n"
        f"   {style('2.', SECONDARY)} {format_book(book_b)}"
    )

    header = match_header if not redo else redo_header

    print("\n" + header + "\n" + match)


def resolve_comparison(book_a, book_b, selection):
    winner = book_a if selection == "1" else book_b
    loser = book_b if selection == "1" else book_a

    new_winner_elo, new_loser_elo = calculate_elo(winner, loser)
    save_comparison(winner.id, loser.id)

    winner.update_elo(new_winner_elo)
    loser.update_elo(new_loser_elo)

    winner.record_opponent(loser.id)
    loser.record_opponent(winner.id)

    winner.record_won_over(loser.id)
