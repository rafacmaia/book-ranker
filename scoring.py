import state
from models import Book
from utils import style, progress_bar

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


def calculate_rankings_confidence():
    if not state.books:
        state.rankings_confidence = 0
        return
    con_scores = [confidence_score(book) for book in state.books]
    state.rankings_confidence = sum(con_scores) / len(con_scores)


def confidence_score(book):
    """Return a confidence score indicating the certainty of a book's ranking.

    Use a weighted combination of absolute number of opponents faced, number of
    similarly scored opponents faced, and local density in overall rankings to account
    for, respectively, overall confidence, local confidence, and stability.
    """
    # Guard to prevent division by zero when there are 0-1 books in the system.
    if len(state.books) <= 1:
        return 0

    # Absolute score emphasizes that the first batch of matches should carry a lot of
    # weight to quickly reach an overall placement.
    absolute_cap = max(len(state.books) * 0.10, 10)
    absolute_score = min(len(book.opponents) / absolute_cap, 1)

    # Local score emphasizes that matches against books with similar Elo scores should
    # carry more weight to quickly refine placement within the rankings.
    relevant_opponents = relevant_opp_faced = 0
    for opp in state.books:
        if opp.id != book.id and 0.34 <= expected_score(book.elo, opp.elo) <= 0.66:
            relevant_opponents += 1
            if opp.id in book.opponents:
                relevant_opp_faced += 1
    local_score = relevant_opp_faced / relevant_opponents if relevant_opponents else 0

    # Density score accounts for the local density of Elo scores in the overall
    # rankings. High cluster density indicates a high chance of ranks easily shifting.
    density_score = 1 - cluster_density(book)

    return absolute_score * 0.35 + local_score * 0.45 + density_score * 0.20


def cluster_density(book):
    tight_neighbors = sum(
        1 for opp in state.books if opp.id != book.id and abs(book.elo - opp.elo) < 28
    )

    upper_proximity = max(0, 1 - (Book.elo_max - book.elo) / 28)
    lower_proximity = max(0, 1 - (book.elo - Book.elo_min) / 28)
    edge_factor = 1 + max(upper_proximity, lower_proximity)

    return min((tight_neighbors * edge_factor) / 10, 1)


def confidence_summary(pct, color="bold green"):
    summary = f" Current confidence: {style(progress_bar(pct, 25), color)}\n"

    if pct < 0.2:
        summary += " Not much data yet, ranking mostly based on initial ratings."
    elif pct < 0.4:
        summary += (
            " Still early stages, but broad tiers (top/mid/bottom) likely correct."
        )
    elif pct < 0.6:
        summary += " General positions are fairly reliable, exact ranks still shifting."
    elif pct < 0.8:
        summary += " Positions are well established, likely within ~10 spots."
    elif pct < 0.95:
        summary += " Rankings are locked in, unlikely to shift significantly."
    else:
        summary += " Absolute ranking of all books established!"

    return summary
