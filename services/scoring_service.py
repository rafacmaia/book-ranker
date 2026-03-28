from models import Book

ABS_SCORE_WEIGHT = 0.306
LOC_SCORE_WEIGHT = 0.45
DEN_SCORE_WEIGHT = 0.25  # density-based stability score

LOC_LOWER_BOUND = 0.35
LOC_UPPER_BOUND = 0.65
ABS_MIN_OPPONENTS = 8
DENSITY_WINDOW = 26
K_TIERS = [(0.25, 40), (0.5, 32), (0.75, 24), (1.0, 16)]


# ====== CONFIDENCE SCORING


def calculate_progress(books):
    """Return the average confidence score of all books."""
    if not books:
        return 0
    confidence_scores = [confidence_score(book, books) for book in books]
    return sum(confidence_scores) / len(confidence_scores)


def confidence_score(book, books):
    """Return a confidence score indicating the certainty of a book's ranking.

    Use a weighted combination of the number of opponents faced, number of faced
    opponents with similar score, and local density in overall rankings to account
    for, respectively, overall confidence, local confidence, and stability.
    """
    if len(books) < 1:
        return 0
    if len(books) == 1:
        return 1

    # Absolute score boosts the first batch of matches to speed overall placement.
    abs_score_weighted = absolute_score(book, books) * ABS_SCORE_WEIGHT

    # Local score boosts matches against books with similar Elo to refine placement.
    loc_score_weighted = local_score(book, books) * LOC_SCORE_WEIGHT

    # Density score boosts books with few neighbors with similar Elo, meaning
    # more stability. High density indicates a high chance of ranks shifting.
    den_score_weighted = stability_score(book, books) * DEN_SCORE_WEIGHT

    return abs_score_weighted + loc_score_weighted + den_score_weighted


def absolute_score(book, books):
    """Calculates a book's absolute score.

    Measures if a book has faced a minimum number of opponents, scaling with
    library size.
    """
    absolute_cap = (
        max(len(books) * 0.1, ABS_MIN_OPPONENTS)
        if len(books) > ABS_MIN_OPPONENTS
        else 1
    )

    return min(len(book.opponents) / absolute_cap, 1)


def local_score(book, books):
    """Calculates a book's local score.

    Measures how many opponents a book has faced that are similar to the book's Elo.
    """
    relevant_opponents = relevant_opp_faced = 0
    for opp in books:
        if (
            opp.id != book.id
            and LOC_LOWER_BOUND <= expected_score(book.elo, opp.elo) <= LOC_UPPER_BOUND
        ):
            relevant_opponents += 1
            if opp.id in book.opponents:
                relevant_opp_faced += 1

    return relevant_opp_faced / relevant_opponents if relevant_opponents else 1


def stability_score(book, books):
    """Calculates a book's stability score.

    Measures how many books have a close Elo to the book. High score density implies a
    higher chance for ranks to shift (i.e., lower stability in rankings).
    """
    tight_neighbors = sum(
        1
        for opp in books
        if opp.id != book.id and abs(book.elo - opp.elo) < DENSITY_WINDOW
    )

    upper_proximity = max(0, 1 - (Book.elo_max - book.elo) / DENSITY_WINDOW)
    lower_proximity = max(0, 1 - (book.elo - Book.elo_min) / DENSITY_WINDOW)
    edge_factor = 1 + max(upper_proximity, lower_proximity)

    density = min((tight_neighbors * edge_factor) / 10, 1)

    return 1 - density


# ====== ELO CALCULATION


def calculate_elo(winner, loser, books):
    """Calculates each book's new Elo scores after a match."""
    expected_w = _expected_score(winner.elo, loser.elo)
    expected_l = _expected_score(loser.elo, winner.elo)
    new_winner_elo = round(winner.elo + _get_k(winner, books) * (1 - expected_w))
    new_loser_elo = round(loser.elo + _get_k(loser, books) * (0 - expected_l))

    return new_winner_elo, new_loser_elo


def _expected_score(elo_a, elo_b):
    """Calculates the expected score of a book given the Elo of a potential opponent."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def get_k(book, books):
    """Calculates and returns k value.

    Calculation is based on the percentage of unique opponents, i.e., confidence level.
    """
    if len(books) <= 1:
        return K_TIERS[0][1]

    confidence = confidence_score(book, books)

    return next(k for threshold, k in K_TIERS if confidence <= threshold)


# --- SELECTION WEIGHT SCORING ---


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
