from constants import BOOK_LIMIT, SIGNATURE
from theme import ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY
from utils import rule, style

# ====== MENUS


PIT_MENU = f"""{style("Match options:", SECONDARY)}
   {style("1", SECONDARY)} → Select book #1
   {style("2", SECONDARY)} → Select book #2
   {style("u", SECONDARY)} → Undo previous match
   {style("b", SECONDARY)} → Back to main menu
   {style("q", SECONDARY)} → Quit program"""

IMPORT_MENU = f""" How would you like to import new books?
   {style("1", SECONDARY)} → Manual entry
   {style("2", SECONDARY)} → Import from CSV
   {style("b", SECONDARY)} → Back to main menu"""


# ====== HEADERS & DIVIDERS


TITLE = (
    f"{rule((LINE_LENGTH // 2 - 7), PRIMARY)}"
    f"{style('  BOOK BRAWL  ', PRIMARY)}"
    f"{rule((LINE_LENGTH // 2 - 7), PRIMARY)}"
)

GOODBYE = (
    f"{rule((LINE_LENGTH // 2 - 16), PRIMARY)}"
    f"{style(' 📚 Goodbye! Keep on reading 📚 ', PRIMARY)}"
    f"{rule((LINE_LENGTH // 2 - 16), PRIMARY)}\n"
    f"{' ' * (LINE_LENGTH - 19)}{style(SIGNATURE, 'dim')}"
)


# ====== MESSAGES

ONBOARDING = f""" {style("Welcome to Book Brawl", SECONDARY)}, where books face off for the ultimate ranking!

 To start the search for the one book to rule them all, please provide the path to a
 CSV file of all your contenders."""

CSV_INSTRUCTIONS = f""" 
 It must have {style("title", SECONDARY)} and {style("author", SECONDARY)} columns. A {style("rating", SECONDARY)} column is optional, but encouraged.

 Note: If {style("rating", SECONDARY)} is included, it should be between 0 and 10, decimals welcome. This
 sets an initial placement for each book, which the brawl pit will confirm or dispel."""


PIT_INSTRUCTIONS = f"""
 Books will be repeatedly paired against each other, and each time you'll be asked:
{PROMPT}{style("Which book means more to you?", "italic" + SECONDARY)} 

 Take a moment, or let instinct lead, and select {style("1", SECONDARY)} or {style("2", SECONDARY)}. No draws. No mercy.

 Over time, using an ancient formula thought lost to the burnt scrolls of Alexandria,
 Book Brawl will distill the true standing of every book in your heart and mind.

 {PIT_MENU}

 {style("Press Enter to launch the pit... ", SECONDARY)}"""


# ====== WARNINGS


LIMIT_REACHED = (
    f" {style('Sorry, you read way too much! The brawl pit has reached its limit of', ERROR)}"
    f" {style(BOOK_LIMIT, SECONDARY)}"
    f" {style('books.\n It physically cannot handle any more 😭.', ERROR)}"
)

EMPTY_IMPORT = (
    f"{PROMPT}{style('WARNING:', ERROR)}"
    f" No books imported. Please check file and try again."
)

IMPORT_INTERRUPTED = (
    f"{PROMPT}{style('WARNING:', ERROR)}"
    f" Book limit reached during import, not all books were added."
)

LIMIT_WARNING = (
    f"{PROMPT}{style('WARNING:', ERROR)} Book limit reached, no more can be added!"
)
