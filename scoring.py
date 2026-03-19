import state
from models import Book

# --- ELO SCORE CALCULATIONS ---


def calculate_elo(winner, loser):
    expected_w = expected_score(winner.elo, loser.elo)
    expected_l = expected_score(loser.elo, winner.elo)
    new_winner_elo = round(winner.elo + get_k(winner) * (1 - expected_w))
    new_loser_elo = round(loser.elo + get_k(loser) * (0 - expected_l))

    return new_winner_elo, new_loser_elo


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def get_k(book):
    """Calculates and returns k value based on the percentage of unique opponents, i.e.,
    confidence level.
    """
    if len(state.books) <= 1:
        return 40

    confidence = confidence_score(book)
    if confidence < 0.2:
        return 40
    elif confidence < 0.4:
        return 32
    elif confidence < 0.6:
        return 24
    elif confidence < 0.8:
        return 16
    else:
        return 10


# --- CONFIDENCE SCORE CALCULATIONS ---

ABS_SCORE_WEIGHT = 0.30
LOC_SCORE_WEIGHT = 0.45
DEN_SCORE_WEIGHT = 0.25  # density-based stability score
ABS_MIN_OPPONENTS = 8
DENSITY_WINDOW = 26


def calculate_progress():
    if not state.books:
        state.current_progress = 0
        return
    con_scores = [confidence_score(book) for book in state.books]
    state.current_progress = sum(con_scores) / len(con_scores)


def confidence_score(book):
    """Return a confidence score indicating the certainty of a book's ranking.

    Use a weighted combination of the number of opponents faced, number of faced
    opponents with similar score, and local density in overall rankings to account
    for, respectively, overall confidence, local confidence, and stability.
    """
    if len(state.books) <= 1:
        return 0

    # Absolute score boosts the first batch of matches to quickly reach an
    # overall placement.
    abs_score_weighted = absolute_score(book) * ABS_SCORE_WEIGHT

    # Local score boosts matches against books with similar Elo to refine
    # placement within the leaderboard.
    loc_score_weighted = local_score(book) * LOC_SCORE_WEIGHT

    # Density score boosts books with few neighbors with similar Elo, meaning
    # more stability. High density indicates a high chance of ranks shifting.
    den_score_weighted = stability_score(book) * DEN_SCORE_WEIGHT

    return abs_score_weighted + loc_score_weighted + den_score_weighted


def absolute_score(book):
    absolute_cap = (
        max(len(state.books) * 0.1, ABS_MIN_OPPONENTS)
        if len(state.books) > ABS_MIN_OPPONENTS
        else 1
    )

    return min(len(book.opponents) / absolute_cap, 1)


def local_score(book):
    relevant_opponents = relevant_opp_faced = 0
    for opp in state.books:
        if opp.id != book.id and 0.35 <= expected_score(book.elo, opp.elo) <= 0.65:
            relevant_opponents += 1
            if opp.id in book.opponents:
                relevant_opp_faced += 1

    return relevant_opp_faced / relevant_opponents if relevant_opponents else 1


def stability_score(book):
    tight_neighbors = sum(
        1
        for opp in state.books
        if opp.id != book.id and abs(book.elo - opp.elo) < DENSITY_WINDOW
    )

    upper_proximity = max(0, 1 - (Book.elo_max - book.elo) / DENSITY_WINDOW)
    lower_proximity = max(0, 1 - (book.elo - Book.elo_min) / DENSITY_WINDOW)
    edge_factor = 1 + max(upper_proximity, lower_proximity)

    density = min((tight_neighbors * edge_factor) / 10, 1)

    return 1 - density
