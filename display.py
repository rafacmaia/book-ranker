import state

from rich.console import Console
from rich.table import Table
from rich import box

from db import get_unique_opponent_count

INITIAL_BATCH_SIZE = 50
BATCH_SIZE = 50
LINE_WIDTH = 98  # Keep it an even number

MAIN_MENU = f"""\033[1;34m MAIN MENU {'–' * (LINE_WIDTH - 11)}\033[0m
 1. Play
 2. View Rankings
 3. Import New Books
 4. Quit"""

GAME_MENU = f"""
\033[1;34m BOOK ARENA {'–' * (LINE_WIDTH - 12)}\033[0m
 Let's rank some books!
 Books will face-off in random matches to craft the ultimate book ranking.
 Options:
   1 → Selects book #1
   2 → Selects book #2
   b → Back to main menu
   q → Quits program
 Let's get started!"""


def print_rankings(verbose=False):
    ranked_books = sorted(state.books, key=lambda book: book.elo, reverse=True)
    batch_end = INITIAL_BATCH_SIZE

    print(
        f"\n\033[1;32m {'–' * (LINE_WIDTH // 2 - 9)} CURRENT RANKINGS {'–' * (LINE_WIDTH // 2 - 10)}\033[0m",
    )
    print_table(ranked_books, 0, batch_end, verbose)

    while batch_end < state.book_count:
        selection = input(
            f"{' ' * (LINE_WIDTH - 25)}\033[1;33m See next {BATCH_SIZE} (y/n) > \033[0m"
        )
        if selection.lower() == "y":
            batch_end += BATCH_SIZE
            print_table(ranked_books, batch_end - BATCH_SIZE, batch_end, verbose)
        else:
            break


def print_table(books, start, end, verbose=False):
    opponent_counts = get_unique_opponent_count()

    table = Table(
        box=box.HORIZONTALS,
        border_style="blue",
    )

    table.add_column(
        "#", justify="center", style="bold green", header_style="green", width=4
    )
    table.add_column("TITLE", justify="left", header_style="bold green", width=43)
    table.add_column("AUTHOR", justify="left", header_style="bold green", width=28)
    table.add_column("CONFIDENCE", justify="left", header_style="bold green")
    if verbose:
        table.add_column("ELO RATING", justify="left", header_style="bold green")

    for i, book in enumerate(books[start:end], start=start + 1):
        confidence = confidence_label(
            opponent_counts.get(book.id, 0) / (len(books) - 1)
        )
        if verbose:
            table.add_row(str(i), book.title, book.author, confidence, str(book.elo))
        else:
            table.add_row(str(i), book.title, book.author, confidence)

    console = Console()
    console.print(table)


def confidence_label(confidence):
    if confidence < 0.10:
        return "🔴 Very Low"
    elif confidence < 0.25:
        return "🟠 Low"
    elif confidence < 0.5:
        return "🟡 Moderate"
    elif confidence < 0.75:
        return "🟢 High"
    else:
        return "✅ Very High"
