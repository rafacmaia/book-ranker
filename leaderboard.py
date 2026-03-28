from rich import box
from rich.console import Console
from rich.table import Table

from services.ranking_service import rank_books
from services.scoring_service import (
    absolute_score,
    calculate_progress,
    confidence_score,
    get_k,
    local_score,
    sampling_weight,
    stability_score,
)
from ui import (
    ACCENT,
    ACCURACY_EXPLAINER,
    ACCURACY_LABELS,
    BATCH_SIZE,
    ERROR,
    INITIAL_BATCH_SIZE,
    LINE_WIDTH,
    PRIMARY,
    PROMPT,
    SECONDARY,
    rule,
    style,
)
from utils import header, library_summary, press_enter


def view_leaderboard(books, verbose=False):
    """Handle the leaderboard view.

    Provides current library status, ranks books based on Elo scores, and displays
    rankings in batches.
    """
    ranked_books = rank_books(books)
    batch_end = INITIAL_BATCH_SIZE

    print(header("THE LEADERBOARD", new_line=True))

    # Print informational summary of the user's library and current confidence level
    print(library_summary(len(books), calculate_progress(books), PRIMARY))
    press_enter("Press Enter to view leaderboard...")
    print()

    _print_table(ranked_books, 0, batch_end, books, verbose)

    while True:
        next_action = _table_menu(batch_end, len(books))

        if next_action == "":
            batch_end += BATCH_SIZE
            _print_table(
                ranked_books, batch_end - BATCH_SIZE, batch_end, books, verbose
            )
        elif next_action == "?":
            print(header("Accuracy Tiers", color=ACCENT))
            print(ACCURACY_EXPLAINER)
            print(f" {rule(LINE_WIDTH - 1, ACCENT)}")
        else:
            return next_action


def _print_table(ranked_books, start, end, books, verbose=False):
    table = Table(box=box.HORIZONTALS, border_style="bright_blue", width=LINE_WIDTH + 1)

    _add_columns(table, verbose)
    _add_rows(table, ranked_books, start, end, books, verbose)

    Console().print(table)


def _add_columns(table, verbose):
    table.add_column("#", justify="left", style=PRIMARY, header_style=PRIMARY)
    table.add_column("TITLE", justify="left", header_style=PRIMARY)
    table.add_column("AUTHOR", justify="left", header_style=PRIMARY)
    table.add_column("ACCURACY", justify="left", header_style=PRIMARY)

    if verbose:
        table.add_column("ELO", justify="left", header_style=PRIMARY)
        table.add_column("K", justify="left", header_style=PRIMARY)
        table.add_column("ABS", justify="left", header_style=PRIMARY)
        table.add_column("LOC", justify="left", header_style=PRIMARY)
        table.add_column("STA", justify="left", header_style=PRIMARY)
        table.add_column("WEI", justify="left", header_style=PRIMARY)


def _add_rows(table, ranked_books, start, end, books, verbose):
    for rank, b in ranked_books[start:end]:
        con_score = confidence_score(b, books)
        confidence = _confidence_label(con_score)

        if verbose:
            table.add_row(
                str(rank),
                b.title,
                b.author,
                f"{con_score:.2f}",
                str(b.elo),
                str(get_k(b, books)),
                f"{absolute_score(b, books):.2f}",
                f"{local_score(b, books):.2f}",
                f"{stability_score(b, books):.2f}",
                f"{sampling_weight(b, books):.2f}",
            )
        else:
            table.add_row(str(rank), b.title, b.author, confidence)


def _confidence_label(confidence):
    return next(label for tier, label in ACCURACY_LABELS if confidence <= tier)


def _table_menu(batch_end, book_count):
    if batch_end < book_count:
        print(
            f"{' ' * (LINE_WIDTH - 20)}"
            f"{style(f'↵ → See next {BATCH_SIZE}', styling=SECONDARY)}"
        )
    print(
        f"{' ' * (LINE_WIDTH - 20)}? → Accuracy tiers\n"
        f"{' ' * (LINE_WIDTH - 20)}b → Main menu\n"
        f"{' ' * (LINE_WIDTH - 20)}e → Export\n"
        f"{' ' * (LINE_WIDTH - 20)}q → Quit"
    )

    choice = input(f"{' ' * (LINE_WIDTH - 8)}{PROMPT}").strip().lower()

    while choice not in ("?", "b", "e", "q"):
        if batch_end < book_count and choice == "":
            break
        choice = input(
            f"{' ' * (LINE_WIDTH - 40)}"
            f"{style('Invalid choice, please try again', ERROR)}{PROMPT}"
        )

    return choice
