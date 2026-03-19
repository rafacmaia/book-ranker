import textwrap

import state
from theme import ERROR, LINE_LENGTH, PRIMARY, PROMPT, SECONDARY


def prompt(options, error_message=None, p=PROMPT):
    if not error_message:
        error_message = f"Nope, please try: {', '.join(options)}"

    while True:
        choice = input(f"{p}").strip().lower()
        if choice in options:
            return choice
        print(f"{p}{style(error_message, ERROR)}")


def style(text, styling=None):
    code = ansi(styling)

    if not code:
        return text

    return code + str(text) + "\033[0m"


def rule(length, styling=None, symbol="─"):
    code = ansi(styling)
    if not code:
        return symbol * length

    return code + (symbol * length) + "\033[0m"


def ansi(styling=None):
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


def leaderboard_summary(pct, color=PRIMARY):
    summary = f" Your library:     {style(f'{len(state.books)} Books', color)}"
    summary += f"\n Current progress: {style(progress_bar(pct, 20), color)}\n\033[3m"

    if pct < 0.2:
        summary += " Not much data yet, ranking mostly based on initial ratings."
    elif pct < 0.45:
        summary += (
            " Still early stages, but broad tiers (top/mid/bottom) likely correct."
        )
    elif pct < 0.65:
        summary += " General positions are fairly reliable, exact ranks still shifting."
    elif pct < 0.85:
        summary += (
            " Positions are well established, "
            "likely within ~5 spots of final placement."
        )
    elif pct < 0.95:
        summary += " Rankings are locked in, unlikely to shift significantly."
    else:
        summary += " Final standings of all books established!"

    return summary + "\033[0m"


def progress_bar(pct, width=20):
    filled = round(pct * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    pct_str = f"{pct * 100:3.0f}%"

    # Make sure labels have an odd number of chars to fit the display better.
    if pct < 0.2:
        label = "🔴 JUST STARTING"
    elif pct < 0.45:
        label = "🟠 COOKING"
    elif pct < 0.65:
        label = "🟡 GETTING THERE"
    elif pct < 0.85:
        label = "🟢 WE'RE CLOSE"
    elif pct < 0.95:
        label = "✅  LOCKED IN"
    else:
        label = "✨ COMPLETE! ✨"

    return f"{bar} {pct_str}  {label}"


def format_book(book, width=LINE_LENGTH - 7):
    return textwrap.fill(str(book), width=width, subsequent_indent="\t")


def press_enter(message="Press Enter for the main menu... ", new_line=True):
    print() if new_line else None
    input(f"{PROMPT}{style(message, SECONDARY)}")
