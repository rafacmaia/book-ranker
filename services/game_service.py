import random

from db.comparisons_repo import insert as insert_comparison
from services.scoring_service import absolute_score, calculate_elo, confidence_score


def select_opponents(books):
    """Select two books using weighted random selection.

    Favor low-confidence books (i.e., books with fewer unique matches played), books
    that have been matched against each other less often, and books with similar Elo
    scores, to maximize information gained from each match.
    """
    # Calculate weights based on confidence level.
    weights = [sampling_weight(book, books) for book in books]

    book_a = random.choices(books, weights=weights, k=1)[0]

    # Calculate weights for book_b candidates based on the selected book_a
    candidates = opponent_weights(book_a, books)
    candidate_books = [b for b, w in candidates]
    candidate_weights = [w for b, w in candidates]

    book_b = random.choices(candidate_books, weights=candidate_weights, k=1)[0]

    return book_a, book_b


def sampling_weight(book, books):
    """Calculate selection weight based on confidence level and absolute_score.

    Ensures a minimum weight of 0.1. Absolute_score is used to highly prioritize newer
    book entries with very few matches.
    """
    if len(books) <= 1:
        return 1

    # Boost scales with library size and absolute_score: larger collections
    # require higher boosts to make a difference, and lower absolute_score
    # requires a higher boost to get early data in.
    early_boost = (len(books) * 0.1) * (1 - absolute_score(book, books))
    confidence_weight = 1 - confidence_score(book, books)
    return max(0.1, confidence_weight, early_boost)


def opponent_weights(book_a, books):
    """Adjust weights for book_b selection based on the selected book_a.

    Prioritize rarer pairings and books with similar Elo scores.
    """
    candidates = []
    for b in books:
        if b.id != book_a.id:
            # Increase the multiplier to penalize rematches more
            rematch_penalty = 1 + 2 * book_a.opponents.get(b.id, 0)

            # Decrease the divisor to prioritize similar score ranges
            elo_gap_penalty = 1 + abs(book_a.elo - b.elo) / 150

            # Calculate the base weight based on confidence level
            w = max(0.1, 1 - confidence_score(b, books))
            adjusted_weight = max(0.1, w / rematch_penalty / elo_gap_penalty)

            candidates.append((b, adjusted_weight))

    return candidates


def resolve_comparison(book_a, book_b, selection, books):
    """Update book records after a match is resolved.

    Update Elo scores, persist match, and update book opponents and wins.
    """
    winner = book_a if selection == "1" else book_b
    loser = book_b if selection == "1" else book_a

    new_winner_elo, new_loser_elo = calculate_elo(winner, loser, books)
    insert_comparison(winner.id, loser.id)

    winner.update_elo(new_winner_elo)
    loser.update_elo(new_loser_elo)

    winner.record_opponent(loser.id)
    loser.record_opponent(winner.id)

    winner.record_won_over(loser.id)
