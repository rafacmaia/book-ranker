from rich import box
from rich.console import Console
from rich.table import Table

from services.ranking_service import rank_books
from services.scoring_service import (
    calculate_progress,
    confidence_score,
    score_breakdown,
)
from ui import (
    ACCENT,
    ACCURACY_EXPLAINER,
    ACCURACY_LABELS,
    BATCH_SIZE,
    ERROR,
    INITIAL_BATCH_SIZE,
    LEADERBOARD_MENU,
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
    press_enter("Press Enter to view leaderboard... ")
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
        if verbose:
            _verbose_row(table, b, rank, books)
        else:
            con_score = confidence_score(b, books)
            confidence = _confidence_label(con_score)

            table.add_row(str(rank), b.title, b.author, confidence)


def _confidence_label(confidence):
    return next(label for tier, label in ACCURACY_LABELS if confidence <= tier)


def _verbose_row(table, b, rank, books):
    score_detailed = score_breakdown(b, books)

    table.add_row(
        str(rank),
        b.title,
        b.author,
        f"{score_detailed['confidence']:.2f}",
        str(b.elo),
        str(score_detailed["k"]),
        f"{score_detailed['absolute']:.2f}",
        f"{score_detailed['local']:.2f}",
        f"{score_detailed['stability']:.2f}",
        f"{score_detailed['sampling_weight']:.2f}",
    )


def _table_menu(batch_end, book_count):
    if batch_end < book_count:
        print(f"{' ' * (LINE_WIDTH - 19)}{LEADERBOARD_MENU[0]}")
    print(
        f"{' ' * (LINE_WIDTH - 19)}{LEADERBOARD_MENU[1]}\n"
        f"{' ' * (LINE_WIDTH - 19)}{LEADERBOARD_MENU[2]}\n"
        f"{' ' * (LINE_WIDTH - 19)}{LEADERBOARD_MENU[3]}\n"
        f"{' ' * (LINE_WIDTH - 19)}{LEADERBOARD_MENU[4]}"
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
