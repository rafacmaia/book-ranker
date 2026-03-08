from rich import box
from rich.console import Console
from rich.table import Table

import state
from constants import (
    BATCH_SIZE,
    CONFIDENCE_TIERS,
    HEADER,
    INITIAL_BATCH_SIZE,
    LINE_LENGTH,
    RANKINGS_HEADER,
    SUBHEADER,
)
from scoring import (
    absolute_score,
    confidence_score,
    confidence_summary,
    get_k,
    local_score,
    stability_score,
)
from utils import PROMPT, style


def view_rankings(verbose=False):
    """Print the top-ranked books in the system, based on their Elo scores, with an
    option to view more books.
    """
    ranked_books = rank_books()
    batch_end = INITIAL_BATCH_SIZE

    print()
    print(RANKINGS_HEADER)

    # Print informational summary of the user's library and current confidence level
    print(" Your library:      ", style(f"{len(state.books)} Books", HEADER))
    print(confidence_summary(state.rankings_confidence, HEADER))
    input(f"\n{PROMPT}{style('Press Enter to view rankings...', SUBHEADER)} ")
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
    sorted_books = sorted(state.books, key=lambda book: book.elo, reverse=True)

    ranked_books = []
    previous_rank = 0
    for i, b in enumerate(sorted_books, start=1):
        rank = str(i) if i == 1 or sorted_books[i - 2].elo != b.elo else previous_rank

        previous_rank = rank

        is_tied = (i != len(sorted_books) and b.elo == sorted_books[i].elo) or (
            i > 1 and sorted_books[i - 2].elo == b.elo
        )

        if is_tied:
            rank += "~"

        ranked_books.append((rank, b))

    return ranked_books


def print_table(books, start, end, verbose=False):
    table = Table(
        box=box.HORIZONTALS, border_style="bright_blue", width=LINE_LENGTH + 1
    )

    add_columns(table, verbose)
    add_rows(table, books, start, end, verbose)

    Console().print(table)


def add_columns(table, verbose):
    table.add_column("#", justify="center", style=HEADER, header_style=HEADER)
    table.add_column("TITLE", justify="left", header_style=HEADER)
    table.add_column("AUTHOR", justify="left", header_style=HEADER)
    table.add_column("CONFIDENCE", justify="left", header_style=HEADER)

    if verbose:
        table.add_column("ELO", justify="left", header_style=HEADER)
        table.add_column("K", justify="left", header_style=HEADER)
        table.add_column("ABS", justify="left", header_style=HEADER)
        table.add_column("LOC", justify="left", header_style=HEADER)
        table.add_column("STA", justify="left", header_style=HEADER)


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
            f"{style(f'↵ → See next {BATCH_SIZE}', styling=SUBHEADER)}"
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
