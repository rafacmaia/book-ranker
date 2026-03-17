from rich import box
from rich.console import Console
from rich.table import Table

import state
from constants import (
    BATCH_SIZE,
    CONFIDENCE_TIERS,
    INITIAL_BATCH_SIZE,
    RANKINGS_HEADER,
)
from scoring import (
    absolute_score,
    confidence_score,
    get_k,
    local_score,
    stability_score,
)
from theme import LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import press_enter, rankings_summary, style


def view_rankings(verbose=False):
    """Print the top-ranked books in the system, based on their Elo scores, with an
    option to view more books.
    """
    ranked_books = rank_books()
    batch_end = INITIAL_BATCH_SIZE

    print()
    print(RANKINGS_HEADER)

    # Print informational summary of the user's library and current confidence level
    print(rankings_summary(state.rankings_confidence, PRIMARY))
    press_enter('Press Enter to view rankings...')
    print()

    print_table(ranked_books, 0, batch_end, verbose)

    while True:
        next_action = rankings_menu(batch_end)

        if next_action == "":
            batch_end += BATCH_SIZE
            print_table(ranked_books, batch_end - BATCH_SIZE, batch_end, verbose)
        elif next_action == "?":
            print(CONFIDENCE_TIERS)
        else:
            return next_action


def rank_books():
    """Rank all books based on their Elo score.

    Ties are broken by head-to-head comparisons (i.e., number of wins against other
    tied books), then by initial user rating.
    """
    elo_sort = sorted(state.books, key=lambda b: b.elo, reverse=True)

    ranked = []
    i = 0
    rank = 0
    while i < len(elo_sort):
        tied_group = [elo_sort[i]]
        while i + 1 < len(elo_sort) and elo_sort[i + 1].elo == elo_sort[i].elo:
            i += 1
            tied_group.append(elo_sort[i])

        rank += 1

        if len(tied_group) == 1:
            ranked.append((str(rank), tied_group[0]))
        else:
            ranked.extend(tiebreak(tied_group, rank))

        rank += len(tied_group) - 1
        i += 1

    return ranked


def tiebreak(tied_group, rank):
    """Sort a tied group by head-to-head wins, then initial user rating"""
    tiebreak_scores = {b.id: head_to_head_score(b, tied_group) for b in tied_group}
    tied_group.sort(key=lambda b: (tiebreak_scores[b.id], b.rating), reverse=True)

    ranked = []
    current_rank = rank
    for j, book in enumerate(tied_group):
        tied_to_prev = (
            j > 0
            and tiebreak_scores[tied_group[j - 1].id] == tiebreak_scores[book.id]
            and book.rating == tied_group[j - 1].rating
        )
        tied_to_next = (
            j < len(tied_group) - 1
            and tiebreak_scores[tied_group[j + 1].id] == tiebreak_scores[book.id]
            and book.rating == tied_group[j + 1].rating
        )

        display_rank = (
            f"{current_rank}~" if tied_to_next or tied_to_prev else str(current_rank)
        )
        ranked.append((display_rank, book))

        if not tied_to_next:
            current_rank += 1

    return ranked


def head_to_head_score(book, tied_books):
    tied_opponents = {b.id for b in tied_books if b.id != book.id}
    wins = sum(book.won_over.get(opp_id, 0) for opp_id in tied_opponents)
    return wins


def print_table(books, start, end, verbose=False):
    table = Table(
        box=box.HORIZONTALS, border_style="bright_blue", width=LINE_LENGTH + 1
    )

    add_columns(table, verbose)
    add_rows(table, books, start, end, verbose)

    Console().print(table)


def add_columns(table, verbose):
    table.add_column("#", justify="left", style=PRIMARY, header_style=PRIMARY)
    table.add_column("TITLE", justify="left", header_style=PRIMARY)
    table.add_column("AUTHOR", justify="left", header_style=PRIMARY)
    table.add_column("CONFIDENCE", justify="left", header_style=PRIMARY)

    if verbose:
        table.add_column("ELO", justify="left", header_style=PRIMARY)
        table.add_column("K", justify="left", header_style=PRIMARY)
        table.add_column("ABS", justify="left", header_style=PRIMARY)
        table.add_column("LOC", justify="left", header_style=PRIMARY)
        table.add_column("STA", justify="left", header_style=PRIMARY)


def add_rows(table, books, start, end, verbose):
    for rank, b in books[start:end]:
        con_score = confidence_score(b)
        confidence = confidence_label(con_score)

        # DEBUG MODE: Print actual confidence value instead of label
        if state.debug:
            confidence = str(round(con_score, 2))

        if verbose:
            table.add_row(
                str(rank),
                b.title,
                b.author,
                f"{con_score:.2f}",
                str(b.elo),
                str(get_k(b)),
                f"{absolute_score(b):.2f}",
                f"{local_score(b):.2f}",
                f"{stability_score(b):.2f}",
            )
        else:
            table.add_row(str(rank), b.title, b.author, confidence)


def confidence_label(confidence):
    if confidence < 0.1:
        return "🔴 Very Low"
    elif confidence < 0.3:
        return "🟠 Low"
    elif confidence < 0.6:
        return "🟡 Moderate"
    elif confidence < 0.85:
        return "🟢 High"
    else:
        return "✅  Very High"


def rankings_menu(batch_end):
    if batch_end < len(state.books):
        print(
            f"{' ' * (LINE_LENGTH - 22)}"
            f"{style(f'↵ → See next {BATCH_SIZE}', styling=SECONDARY)}"
        )
    print(
        f"{' ' * (LINE_LENGTH - 22)}? → Confidence tiers\n"
        f"{' ' * (LINE_LENGTH - 22)}b → Main menu\n"
        f"{' ' * (LINE_LENGTH - 22)}e → Export rankings\n"
        f"{' ' * (LINE_LENGTH - 22)}q → Quit"
    )

    choice = input(f"{' ' * (LINE_LENGTH - 8)}{PROMPT}").strip().lower()

    while choice not in ("?", "b", "e", "q"):
        if batch_end < len(state.books) and choice == "":
            break
        choice = input(
            f"{' ' * (LINE_LENGTH - 40)}"
            f"{style('Invalid choice, please try again', 'red')}{PROMPT}"
        )

    return choice
