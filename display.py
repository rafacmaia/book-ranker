from rich import box
from rich.console import Console
from rich.table import Table

import state
from ranking import confidence_score, get_k, cluster_density

LINE_LENGTH = 96  # 96 Keep it to an even number
MENU_OPTIONS = "5"
INITIAL_BATCH_SIZE = 50
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
    batch_end = INITIAL_BATCH_SIZE

    print(
        f"\n\033[1;32m {'–' * (LINE_LENGTH // 2 - 9)} "
        f"CURRENT RANKINGS "
        f"{'–' * (LINE_LENGTH // 2 - 10)}\033[0m",
    )

    print(CONFIDENCE_EXPLANATION)

    print_table(ranked_books, 0, batch_end, verbose)

    while True:
        if batch_end < state.b_count:
            print(f"{' ' * (LINE_LENGTH - 23)}\033[33mn → See next {BATCH_SIZE}\033[0m")
        print(
            f"\033[0m{' ' * (LINE_LENGTH - 23)}? → Confidence explained\n"
            f"\033[0m{' ' * (LINE_LENGTH - 23)}b → Main menu\n"
            f"{' ' * (LINE_LENGTH - 23)}e → Export rankings\n"
            f"{' ' * (LINE_LENGTH - 23)}q → Quit\033[0m"
        )
        choice = input(f"{' ' * (LINE_LENGTH - 5)}\033[33m> \033[0m").strip().lower()

        while choice not in ("?", "b", "e", "q"):
            if batch_end < state.b_count and choice == "n":
                break
            choice = input(
                f"{' ' * (LINE_LENGTH - 41)}"
                f"\033[31m⚠️ Invalid choice, please try again > \033[0m"
            )

        if choice == "n":
            batch_end += BATCH_SIZE
            print_table(ranked_books, batch_end - BATCH_SIZE, batch_end, verbose)
        elif choice == "?":
            print(CONFIDENCE_EXPLANATION)
            print()
        else:
            return choice


def print_table(books, start, end, verbose=False):
    table = Table(box=box.HORIZONTALS, border_style="blue", width=LINE_LENGTH + 1)
    table.add_column("#", justify="center", style="bold green", header_style="green")
    table.add_column("TITLE", justify="left", header_style="bold green")
    table.add_column("AUTHOR", justify="left", header_style="bold green")
    table.add_column("CONFIDENCE", justify="left", header_style="bold green")

    if verbose:
        table.add_column("ELO RATING", justify="left", header_style="bold green")
        table.add_column("K", justify="left", header_style="bold green")
        table.add_column("STABILITY", justify="left", header_style="bold green")

    for i, book in enumerate(books[start:end], start=start + 1):
        con_score = confidence_score(book)
        confidence = confidence_label(con_score)

        # DEBUG MODE: Print actual confidence value instead of label
        if state.debug:
            confidence = str(round(con_score, 2))

        if verbose:
            elo = str(book.elo)
            k = str(get_k(book))
            density = f"{1 - cluster_density(book):.2f}"
            table.add_row(str(i), book.title, book.author, confidence, elo, k, density)
        else:
            table.add_row(str(i), book.title, book.author, confidence)

    Console().print(table)


def confidence_label(confidence):
    if confidence < 0.15:
        return "🔴 Very Low"
    elif confidence < 0.3:
        return "🟠 Low"
    elif confidence < 0.6:
        return "🟡 Moderate"
    elif confidence < 0.8:
        return "🟢 High"
    else:
        return "✅ Very High"


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
