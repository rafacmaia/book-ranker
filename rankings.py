from rich import box
from rich.console import Console
from rich.table import Table

import state
from constants import (
    LINE_LENGTH,
    INITIAL_BATCH_SIZE,
    BATCH_SIZE,
    HEADER,
    SUBHEADER,
    RANKINGS_HEADER,
    CONFIDENCE_TIERS,
)
from scoring import (
    confidence_score,
    get_k,
    cluster_density,
    confidence_summary,
)
from utils import PROMPT, style


def view_rankings(verbose=False):
    """Print the top-ranked books in the system, based on their Elo scores, with an
    option to view more books.
    """
    ranked_books = sorted(state.books, key=lambda book: book.elo, reverse=True)
    batch_end = INITIAL_BATCH_SIZE

    print()
    print(RANKINGS_HEADER)
    print(" Your library:      ", style(f"{len(state.books)} Books", "bold green"))
    print(confidence_summary(state.rankings_confidence, "bold green"))
    input(
        style(f"\n{PROMPT}\033[33mPress Enter to view rankings... ", styling=SUBHEADER)
    )
    print()

    print_table(ranked_books, 0, batch_end, verbose)

    while True:
        if batch_end < len(state.books):
            print(
                f"{' ' * (LINE_LENGTH - 22)}"
                f"{style(f"n → See next {BATCH_SIZE}", styling=SUBHEADER)}"
            )
        print(
            f"{' ' * (LINE_LENGTH - 22)}? → Confidence tiers\n"
            f"{' ' * (LINE_LENGTH - 22)}b → Main menu\n"
            f"{' ' * (LINE_LENGTH - 22)}e → Export rankings\n"
            f"{' ' * (LINE_LENGTH - 22)}q → Quit"
        )

        choice = input(f"{' ' * (LINE_LENGTH - 8)}{PROMPT}").strip().lower()

        while choice not in ("?", "b", "e", "q"):
            if batch_end < len(state.books) and choice == "n":
                break
            choice = input(
                f"{' ' * (LINE_LENGTH - 40)}"
                f"{style("Invalid choice, please try again", "red")}{PROMPT}"
            )

        if choice == "n":
            batch_end += BATCH_SIZE
            print_table(ranked_books, batch_end - BATCH_SIZE, batch_end, verbose)
        elif choice == "?":
            print(CONFIDENCE_TIERS)
        else:
            return choice


def print_table(books, start, end, verbose=False):
    table = Table(
        box=box.HORIZONTALS, border_style="bright_blue", width=LINE_LENGTH + 1
    )
    table.add_column("#", justify="center", style=HEADER, header_style=HEADER)
    table.add_column("TITLE", justify="left", header_style=HEADER)
    table.add_column("AUTHOR", justify="left", header_style=HEADER)
    table.add_column("CONFIDENCE", justify="left", header_style=HEADER)

    if verbose:
        table.add_column("ELO", justify="left", header_style=HEADER)
        table.add_column("K", justify="left", header_style=HEADER)
        table.add_column("DENSITY", justify="left", header_style=HEADER)

    for i, b in enumerate(books[start:end], start=start + 1):
        con_score = confidence_score(b)
        confidence = confidence_label(con_score)

        # DEBUG MODE: Print actual confidence value instead of label
        if state.debug:
            confidence = str(round(con_score, 2))

        if verbose:
            score = f"{con_score:.2f}"
            k = str(get_k(b))
            density = f"{cluster_density(b):.1f}"
            table.add_row(str(i), b.title, b.author, score, str(b.elo), k, density)
        else:
            table.add_row(str(i), b.title, b.author, confidence)

    Console().print(table)


def confidence_label(confidence):
    if confidence < 0.1:
        return "🔴 Very Low"
    elif confidence < 0.3:
        return "🟠 Low"
    elif confidence < 0.6:
        return "🟡 Moderate"
    elif confidence < 0.8:
        return "🟢 High"
    else:
        return "✅ Very High"
