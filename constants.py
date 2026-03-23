from theme import LINE_LENGTH

# ====== CONFIG CONSTANTS


BOOK_LIMIT = 2000
BACKUPS_LIMIT = 5

DEFAULT_RATING = 6.2

PROGRESS_TIERS = [0.20, 0.45, 0.65, 0.85, 0.95, 1.00]

INITIAL_BATCH_SIZE = 50
BATCH_SIZE = 50

SIGNATURE = "© 2026 Zou Labs🐈‍⬛"


# ====== MENUS


MAIN_MENU = """ 1. Play
 2. Leaderboard
 3. Add New Books
 4. Export Leaderboard
 5. Factory Reset
 6. Tap Out
"""

MAIN_OPTIONS = ["1", "2", "2 -v", "3", "4", "5", "q", "6"]

PIT_OPTIONS = ["1", "2", "u", "b", "q"]


# ====== DISPLAY MESSAGES


TEST_MESSAGE = (
    f"{' ' * (LINE_LENGTH // 2 - 13)}\033[1;31m⚠️ RUNNING IN TEST MODE ⚠️\033[1;0m"
)

ACCURACY_TIERS = """    🔴 Very Low   — Early data, ranking mostly based on initial rating
    🟠 Low        — Some data, broad tier is likely correct (top/mid/bottom)
    🟡 Moderate   — General position is fairly reliable, exact rank still shifting
    🟢 High       — Position is well established, likely within ~5 spots
    ✅  Very High  — Locked in, unlikely to shift significantly"""

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
