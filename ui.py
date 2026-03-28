# ====== CONFIG CONSTANTS

LINE_WIDTH = 86  # Keep it to an even number

BACKUPS_LIMIT = 5

PROGRESS_TIERS = [0.20, 0.45, 0.65, 0.85, 0.95, 1.00]
ACCURACY_TIERS = [0.10, 0.30, 0.65, 0.85, 1.00]

INITIAL_BATCH_SIZE = 50
BATCH_SIZE = 50


# ====== COLOR THEME & INPUT SYMBOL

PROMPT = "\033[1;33m > \033[0m"

PRIMARY = "bold green"
SECONDARY = "bold yellow"
ACCENT = "blue"
ERROR = "bold red"
DIVIDER = "cyan"
REDO = "bold magenta"


# ====== STYLING UTILITIES


def style(text, styling=None):
    """Apply ANSI styling to the provided text."""
    code = _ansi(styling)

    if not code:
        return text

    return code + str(text) + "\033[0m"


def rule(length, styling=None, symbol="─"):
    """Return a horizontal rule with the provided styling."""
    code = _ansi(styling)
    if not code:
        return symbol * length

    return code + (symbol * length) + "\033[0m"


def _ansi(styling=None):
    """Return ANSI escape codes for the provided styling."""
    if not styling:
        return ""

    sections = []

    if "bold" in styling:
        sections.append("1")
    if "dim" in styling:
        sections.append("2")
    if "italic" in styling:
        sections.append("3")
    if "underline" in styling:
        sections.append("4")

    if "red" in styling:
        sections.append("31")
    elif "green" in styling:
        sections.append("32")
    elif "yellow" in styling:
        sections.append("33")
    elif "blue" in styling:
        sections.append("94")
    elif "magenta" in styling:
        sections.append("35")
    elif "cyan" in styling:
        sections.append("36")
    elif "white" in styling:
        sections.append("37")

    if not sections:
        return ""

    return "\033[" + ";".join(sections) + "m"


# ====== TOP-LEVEL DISPLAY: HEADERS, MENUS, SIGNATURE


TITLE = (
    f"{rule((LINE_WIDTH // 2 - 7), PRIMARY)}"
    f"{style('  BOOK BRAWL  ', PRIMARY)}"
    f"{rule((LINE_WIDTH // 2 - 7), PRIMARY)}"
)

ONBOARDING_MENU = f""" {style("1", SECONDARY)} → Manual entry
 {style("2", SECONDARY)} → Import from CSV
 {style("q", SECONDARY)} → Quit
"""

MAIN_OPTIONS = ["1", "2", "2 -v", "3", "4", "5", "q", "6"]

MAIN_MENU = f""" {style("1", SECONDARY)} → Play
 {style("2", SECONDARY)} → Leaderboard
 {style("3", SECONDARY)} → Add New Books
 {style("4", SECONDARY)} → Export Leaderboard
 {style("5", SECONDARY)} → Factory Reset
 {style("6", SECONDARY)} → Tap Out
"""

PIT_MENU = f"""{style("Match options:", SECONDARY)}
   {style("1", SECONDARY)} → Select book #1
   {style("2", SECONDARY)} → Select book #2
   {style("u", SECONDARY)} → Undo previous match
   {style("b", SECONDARY)} → Back to main menu
   {style("q", SECONDARY)} → Quit program"""

PIT_OPTIONS = ["1", "2", "u", "b", "q"]

LEADERBOARD_MENU = [
    style(f"↵ → See next {BATCH_SIZE}", styling=SECONDARY),
    "? → Accuracy tiers",
    "b → Main menu",
    "e → Export",
    "q → Quit",
]

IMPORT_MENU = f""" {style("1", SECONDARY)} → Manual entry
 {style("2", SECONDARY)} → Import from CSV
 {style("b", SECONDARY)} → Back to main menu"""

SIGNATURE = "© 2026 Zou Labs🐈‍⬛"

GOODBYE = (
    f"{rule((LINE_WIDTH // 2 - 7), PRIMARY)}"
    f"{style(' 📚 GOODBYE 📚 ', PRIMARY)}"
    f"{rule((LINE_WIDTH // 2 - 8), PRIMARY)}\n"
    f"{' ' * (LINE_WIDTH - 19)}{style(SIGNATURE, 'dim')}"
)


# ====== INSTRUCTIONS


ONBOARDING = f""" {style("Welcome to Book Brawl", SECONDARY)}, where books face off for the ultimate ranking!

 To start the search for {style("the one book to rule them all", SECONDARY)}, we must add some contenders.
 The brawl pit accepts manual entry or import from a CSV file.
"""

PIT_INSTRUCTIONS = f"""
 Books will be repeatedly paired against each other, and each time you'll be asked:
{PROMPT}{style("Which book means more to you?", "italic" + SECONDARY)} 

 Take a moment, or let instinct lead, and select {style("1", SECONDARY)} or {style("2", SECONDARY)}. No draws. No mercy.

 Over time, using an ancient formula thought lost to the burnt scrolls of Alexandria,
 Book Brawl will distill the true standing of every book in your heart and mind.

 {PIT_MENU}

 {style("Press Enter to launch the pit... ", SECONDARY)}"""

MANUAL_INSTRUCTIONS = f""" 
 {rule(LINE_WIDTH - 1, DIVIDER)}
 Please enter the {style("title", SECONDARY)}, {style("author", SECONDARY)}, and an optional {style("rating", SECONDARY)} (1-10, decimals welcome) of
 each book you'd like to add. 
 
 {style("When you're done", SECONDARY)}, leave the {style("title", SECONDARY)} blank and press {style("Enter", SECONDARY)} to continue."""

CSV_INSTRUCTIONS = f"""
 {rule(LINE_WIDTH - 1, DIVIDER)}
 Please provide the path to your CSV file. It must have {style("title", SECONDARY)} and {style("author", SECONDARY)} columns.
 A {style("rating", SECONDARY)} column is optional (but encouraged).

 {style("Note:", SECONDARY)} If {style("rating", SECONDARY)} is included, it should be between 1 and 10, decimals welcome. This
 sets an initial placement for each book, which the brawl pit will confirm or dispel."""


# ====== ACCURACY & PROGRESS LABELS

ACCURACY_LABELS = [
    (ACCURACY_TIERS[0], "🔴 Very Low"),
    (ACCURACY_TIERS[1], "🟠 Low"),
    (ACCURACY_TIERS[2], "🟡 Moderate"),
    (ACCURACY_TIERS[3], "🟢 High"),
    (ACCURACY_TIERS[4], "✅  Very High"),
]

ACCURACY_EXPLAINER = f"""  {ACCURACY_LABELS[0][1]}  — Early data, ranking mostly based on initial rating
  {ACCURACY_LABELS[1][1]}       — Some data, broad tier is likely correct (top/mid/bottom)
  {ACCURACY_LABELS[2][1]}  — General position is fairly reliable, exact rank still shifting
  {ACCURACY_LABELS[3][1]}      — Position is well established, likely within ~5 spots
  {ACCURACY_LABELS[4][1]} — Locked in, unlikely to shift  by more than 1 or 2 spots"""

# Make sure labels have an odd number of chars to fit the display better.
PROGRESS_LABELS = [
    (PROGRESS_TIERS[0], "🔴 JUST STARTING"),
    (PROGRESS_TIERS[1], "🟠 COOKING"),
    (PROGRESS_TIERS[2], "🟡 GETTING THERE"),
    (PROGRESS_TIERS[3], "🟢 WE'RE CLOSE"),
    (PROGRESS_TIERS[4], "✅  LOCKED IN"),
    (PROGRESS_TIERS[5], "✨  COMPLETE!"),
]

SUMMARY_LABELS = [
    (
        PROGRESS_TIERS[0],
        " Not much data yet, ranking mostly based on initial ratings, if available.",
    ),
    (
        PROGRESS_TIERS[1],
        " Still early stages, but broad tiers (top/mid/bottom) likely correct.",
    ),
    (
        PROGRESS_TIERS[2],
        " General positions are fairly reliable, exact ranks still shifting.",
    ),
    (
        PROGRESS_TIERS[3],
        " Positions are well established, likely within ~5 spots of final placement.",
    ),
    (
        PROGRESS_TIERS[4],
        " Rankings are locked in, unlikely to shift by more than 1 or 2 spots.",
    ),
    (
        PROGRESS_TIERS[5],
        " Final standings of all books established! All books are brawled out!",
    ),
]


# ====== WARNINGS


TEST_MESSAGE = (
    f"{' ' * (LINE_WIDTH // 2 - 13)}\033[1;31m⚠️ RUNNING IN TEST MODE ⚠️\033[1;0m"
)


EMPTY_IMPORT = (
    f"{PROMPT}{style('WARNING:', ERROR)}"
    f" No books imported. Please check file and try again."
)

LIMIT_WARNING = (
    f"{PROMPT}{style('WARNING:', ERROR)} Book limit reached, no more can be added!"
)


def limit_reached(book_limit):
    return (
        style(
            " Sorry, you read way too much! The brawl pit has reached its limit of ",
            ERROR,
        )
        + style(book_limit, SECONDARY)
        + style(" books.\n It physically cannot handle any more 😭.", ERROR)
    )


def import_interrupted(books_imported):
    return (
        f"{PROMPT}{style('WARNING:', ERROR)} Book limit reached, only the first "
        f"{books_imported} valid books were added."
    )
