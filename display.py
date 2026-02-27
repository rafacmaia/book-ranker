from rich import box
from rich.console import Console
from rich.table import Table

import state
from db import get_opponent_counts

LINE_LENGTH = 96  # 96 Keep it to an even number
MENU_OPTIONS = "5"
INITIAL_BATCH_SIZE = 100
BATCH_SIZE = 50

TEST_MESSAGE = (
    f"{' ' * (LINE_LENGTH // 2 - 13)}" f"\033[1;31m⚠️ RUNNING IN TEST MODE ⚠️\033[1;0m"
)

MAIN_MENU = f"""\033[1;34m MAIN MENU {'–' * (LINE_LENGTH - 11)}\033[0m
 1. Play
 2. View Rankings
 3. Import New Books
 4. Export Rankings
 5. Quit"""

GAME_MENU = f"""
\033[1;34m BOOK ARENA {'–' * (LINE_LENGTH - 12)}\033[0m
 Let's rank some books!
 Books will face-off in random matches to craft the ultimate book ranking.
 Options:
   1 → Selects book #1
   2 → Selects book #2
   b → Back to main menu
   q → Quits program
 Let's get started!"""

CONFIDENCE_EXPLANATION = """ \033[3mConfidence levels\033[0m:
    🔴 Very Low   — Early data, ranking mostly based on initial rating
    🟠 Low        — Some data, broad tier is likely correct (top/mid/bottom)
    🟡 Moderate   — General position is fairly reliable, exact rank still shifting
    🟢 High       — Position is well established, likely within ~10 spots
    ✅  Very High  — Locked in, unlikely to shift significantly"""


def view_rankings(verbose=False):
    """Print the top-ranked books in the system, based on their Elo scores, with an
    option to view more books.
    """
    ranked_books = sorted(state.books, key=lambda book: book.elo, reverse=True)
    opp_counts = get_opponent_counts()
    batch_end = INITIAL_BATCH_SIZE

    print(
        f"\n\033[1;32m {'–' * (LINE_LENGTH // 2 - 9)} "
        f"CURRENT RANKINGS "
        f"{'–' * (LINE_LENGTH // 2 - 10)}\033[0m",
    )

    print(CONFIDENCE_EXPLANATION)

    print_table(ranked_books, 0, batch_end, opp_counts, verbose)

    while True:
        if batch_end < state.book_count:
            print(f"{' ' * (LINE_LENGTH - 23)}\033[33mn → See next {BATCH_SIZE}\033[0m")
        print(
            f"\033[0m{' ' * (LINE_LENGTH - 23)}? → Confidence explained\n"
            f"\033[0m{' ' * (LINE_LENGTH - 23)}b → Main menu\n"
            f"{' ' * (LINE_LENGTH - 23)}e → Export rankings\n"
            f"{' ' * (LINE_LENGTH - 23)}q → Quit\033[0m"
        )
        choice = input(f"{' ' * (LINE_LENGTH - 5)}\033[33m> \033[0m").strip().lower()

        while choice not in ("?", "b", "e", "q"):
            if batch_end < state.book_count and choice == "n":
                break
            choice = input(
                f"{' ' * (LINE_LENGTH - 41)}"
                f"\033[31m⚠️ Invalid choice, please try again > \033[0m"
            )

        if choice == "n":
            batch_end += BATCH_SIZE
            print_table(
                ranked_books, batch_end - BATCH_SIZE, batch_end, opp_counts, verbose
            )
        elif choice == "?":
            print(CONFIDENCE_EXPLANATION)
            print()
        else:
            return choice


def print_table(books, start, end, opp_counts, verbose=False):
    table = Table(box=box.HORIZONTALS, border_style="blue", width=LINE_LENGTH + 1)
    table.add_column("#", justify="center", style="bold green", header_style="green")
    table.add_column("TITLE", justify="left", header_style="bold green")
    table.add_column("AUTHOR", justify="left", header_style="bold green")
    table.add_column("CONFIDENCE", justify="left", header_style="bold green")

    if verbose:
        table.add_column("ELO RATING", justify="left", header_style="bold green")

    for i, book in enumerate(books[start:end], start=start + 1):
        con_score = confidence_score(opp_counts.get(book.id, 0))
        confidence = confidence_label(con_score)

        # DEBUG MODE: Print actual confidence value instead of label
        if state.debug:
            confidence = str(round(con_score, 2))

        if verbose:
            table.add_row(str(i), book.title, book.author, confidence, str(book.elo))
        else:
            table.add_row(str(i), book.title, book.author, confidence)

    Console().print(table)


def confidence_score(unique_opp_count):
    """Return a confidence score based on the number of unique opponents faced.

    Use a weighted combination of absolute and relative scores. Absolute score is enough
    to give a general position within the rankings. Relative score gives a more precise
    positioning.
    """
    # Guard to prevent division by zero if there are zero or one books in the system.
    if state.book_count <= 1:
        return 0

    absolute_cap = state.book_count * 0.15
    absolute_score = min(unique_opp_count / absolute_cap, 1)
    relative_score = unique_opp_count / (state.book_count - 1)

    return absolute_score * 0.55 + relative_score * 0.45


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


def calculate_rankings_confidence():
    opp_counts = get_opponent_counts()
    con_scores = [confidence_score(opp_counts.get(book.id, 0)) for book in state.books]
    state.rankings_confidence = sum(con_scores) / len(con_scores)


def progress_bar(pct, width):
    filled = round(pct * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    pct_str = f"{pct * 100:3.0f}%"

    # Make sure labels have an odd number of chars to fit the display better.
    if pct < 0.2:
        label = "🔴 JUST STARTING"
    elif pct < 0.4:
        label = "🟠 COOKING"
    elif pct < 0.6:
        label = "🟡 GETTING THERE"
    elif pct < 0.8:
        label = "🟢 WE'RE CLOSE"
    elif pct < 0.95:
        label = "✅ LOCKED IN"
    else:
        label = "✨ COMPLETE! ✨"

    return f"{bar} {pct_str}  {label}"
