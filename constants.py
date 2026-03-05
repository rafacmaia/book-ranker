from utils import rule, style

LINE_LENGTH = 86  # Keep it to an even number
BOOK_LIMIT = 2500
BACKUPS_LIMIT = 5

QUIT_OPTION = "5"

INITIAL_BATCH_SIZE = 50
BATCH_SIZE = 50


# --- Styling constants


HEADER = "bold green"
SUBHEADER = "bold yellow"
ACCENT = "blue"
DIVIDER = "cyan"


# --- Informational constants


CONFIDENCE_TIERS = (
    f"{style(" Confidence Tiers ", "bold" + ACCENT)}{rule(LINE_LENGTH - 18, "blue")}"
    f"""
    🔴 Very Low   — Early data, ranking mostly based on initial rating
    🟠 Low        — Some data, broad tier is likely correct (top/mid/bottom)
    🟡 Moderate   — General position is fairly reliable, exact rank still shifting
    🟢 High       — Position is well established, likely within ~10 spots
    ✅  Very High  — Locked in, unlikely to shift significantly"""
    f"\n {rule(LINE_LENGTH - 1, "blue")}"
)

TEST_MESSAGE = (
    f"{' ' * (LINE_LENGTH // 2 - 13)}\033[1;31m⚠️ RUNNING IN TEST MODE ⚠️\033[1;0m"
)

GOODBYE = (
    f"{rule((LINE_LENGTH // 2 - 16), HEADER)}"
    f"{style(" 📚 Goodbye! Keep on reading 📚 ", HEADER)}"
    f"{rule((LINE_LENGTH // 2 - 16), HEADER)}"
)


# --- Header constants


TITLE = (
    f"{rule((LINE_LENGTH // 2 - 8), HEADER)}"
    f"{style("  BOOK RANKER  ", HEADER)}"
    f"{rule((LINE_LENGTH // 2 - 7), HEADER)}"
)

MAIN_MENU = f""" {style("MAIN MENU", SUBHEADER)} {rule(LINE_LENGTH - 11, SUBHEADER)}
 1. Play
 2. View Rankings
 3. Import New Books
 4. Export Rankings
 5. Quit"""

ARENA_HEADER = f""" {style("BOOK ARENA", SUBHEADER)} {rule(LINE_LENGTH - 12, SUBHEADER)}
 Let's rank some books!
 Books will face-off in random matches to craft the ultimate book ranking.
 Options:
   {style("1", SUBHEADER)} → Select book #1
   {style("2", SUBHEADER)} → Select book #2
   {style("b", SUBHEADER)} → Back to main menu
   {style("q", SUBHEADER)} → Quit program
   
 {style("Let's get started! (press Enter) ", SUBHEADER)}"""

RANKINGS_HEADER = (
    f"{style(" CURRENT RANKINGS ", SUBHEADER)}{rule(LINE_LENGTH - 18, SUBHEADER)}"
)

IMPORT_HEADER = (
    f"{style(" IMPORT NEW BOOKS ", SUBHEADER)}{rule(LINE_LENGTH - 18, SUBHEADER)}"
)

EXPORT_HEADER = (
    f"{style(" EXPORT RANKINGS ", SUBHEADER)}{rule(LINE_LENGTH - 17, SUBHEADER)}"
)
