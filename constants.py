from theme import ACCENT, ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import rule, style

BOOK_LIMIT = 2500
BACKUPS_LIMIT = 5

QUIT_OPTION = "5"

INITIAL_BATCH_SIZE = 50
BATCH_SIZE = 50

# --- Informational constants

TEST_MESSAGE = (
    f"{' ' * (LINE_LENGTH // 2 - 13)}\033[1;31m⚠️ RUNNING IN TEST MODE ⚠️\033[1;0m"
)


EMPTY_LIBRARY = f""" {style("Welcome to Book Brawl", SECONDARY)}, where books face off for the ultimate ranking!

 To start the search for the one book to rule them all, please provide the path to a
 CSV file of all your contenders.

 It must have {style("title", SECONDARY)} and {style("author", SECONDARY)} columns. A {style("rating", SECONDARY)} column is optional, but encouraged.

 Note: If {style("rating", SECONDARY)} is included, it should be between 0 and 10, decimals welcome. This
 sets an initial placement for each book, which the brawl pit will confirm or dispel."""

ACCURACY_TIERS = (
    f"{style(' Accuracy Tiers ', 'bold' + ACCENT)}{rule(LINE_LENGTH - 16, 'blue')}"
    f"""
    🔴 Very Low   — Early data, ranking mostly based on initial rating
    🟠 Low        — Some data, broad tier is likely correct (top/mid/bottom)
    🟡 Moderate   — General position is fairly reliable, exact rank still shifting
    🟢 High       — Position is well established, likely within ~5 spots
    ✅  Very High  — Locked in, unlikely to shift significantly"""
    f"\n {rule(LINE_LENGTH - 1, 'blue')}"
)

PIT_OPTIONS = ["1", "2", "u", "b", "q"]

LIMIT_REACHED = (
    f"\033[31m Sorry, you read way too much "
    f"and reached the limit of {BOOK_LIMIT} books.\n"
    f" I can't handle any more 😭.\033[0m"
)

EMPTY_IMPORT = (
    f"{PROMPT}"
    f"{style('No books imported. Please check your file and try again.', ERROR)}"
)

IMPORT_INTERRUPTED = (
    f"{PROMPT}{style('Warning:', ERROR)}"
    f" Book limit reached during import, not all books were added."
)

LIMIT_WARNING = (
    f"{PROMPT}{style('Warning:', ERROR)}"
    f" Book limit reached, no more books can be added!"
)

SIGNATURE = "© 2026 Zou Labs🐈‍⬛"

GOODBYE = (
    f"{rule((LINE_LENGTH // 2 - 16), PRIMARY)}"
    f"{style(' 📚 Goodbye! Keep on reading 📚 ', PRIMARY)}"
    f"{rule((LINE_LENGTH // 2 - 16), PRIMARY)}\n"
    f"{' ' * (LINE_LENGTH - 19)}{style(SIGNATURE, 'dim')}"
)


# --- Header constants


TITLE = (
    f"{rule((LINE_LENGTH // 2 - 7), PRIMARY)}"
    f"{style('  BOOK BRAWL  ', PRIMARY)}"
    f"{rule((LINE_LENGTH // 2 - 7), PRIMARY)}"
)

MAIN_MENU = f""" {style("MAIN MENU", SECONDARY)} {rule(LINE_LENGTH - 11, SECONDARY)}
 1. Play
 2. Leaderboard
 3. Import New Books
 4. Export Leaderboard
 5. Tap Out"""

PIT_HEADER = f"""
 {style("BRAWL PIT", SECONDARY)} {rule(LINE_LENGTH - 11, SECONDARY)}"""

PIT_INSTRUCTIONS = f"""
 Books will be repeatedly paired against each other, and each time you'll be asked:
{PROMPT}{style("Which book means more to you?", "italic" + SECONDARY)} 
 
 Take a moment, or let instinct lead, and select {style("1", SECONDARY)} or {style("2", SECONDARY)}. No draws. No mercy.
 
 Over time, using an ancient formula thought lost to the burnt scrolls of Alexandria,
 Book Brawl will distill the true standing of every book in your heart and mind.
 
 {style("Match options:", "bold" + SECONDARY)}
   {style("1", SECONDARY)} → Select book #1
   {style("2", SECONDARY)} → Select book #2
   {style("u", SECONDARY)} → Undo previous match
   {style("b", SECONDARY)} → Back to main menu
   {style("q", SECONDARY)} → Quit program

 {style("Press Enter to launch the pit... ", SECONDARY)}"""

LEADERBOARD_HEADER = (
    f"{style(' THE LEADERBOARD ', SECONDARY)}{rule(LINE_LENGTH - 17, SECONDARY)}"
)

IMPORT_HEADER = (
    f"{style(' IMPORT NEW BOOKS ', SECONDARY)}{rule(LINE_LENGTH - 18, SECONDARY)}"
)

EXPORT_HEADER = (
    f"{style(' EXPORT LEADERBOARD ', SECONDARY)}{rule(LINE_LENGTH - 20, SECONDARY)}"
)
