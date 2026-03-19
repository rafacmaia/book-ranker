import textwrap

import state
from constants import PROGRESS_LABELS, SUMMARY_LABELS
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
    count = len(state.books)
    summary = (
        f" Your library:     {style(f'{count} Book{"s" if count > 1 else ""}', color)}"
    )
    summary += f"\n Current progress: {style(progress_bar(pct, 20), color)}\n\033[3m"

    summary += next(label for threshold, label in SUMMARY_LABELS if pct <= threshold)

    return summary + "\033[0m"


def progress_bar(pct, width=20):
    filled_section = round(pct * width)
    empty_section = width - filled_section

    bar = "█" * filled_section + "░" * empty_section

    pct_str = f"{pct * 100:3.0f}%"

    label = next(label for threshold, label in PROGRESS_LABELS if pct <= threshold)

    return f"{bar} {pct_str}  {label}"


def format_book(book, width=LINE_LENGTH - 7):
    return textwrap.fill(str(book), width=width, subsequent_indent="\t")


def press_enter(message="Press Enter for the main menu... ", new_line=True):
    print() if new_line else None
    input(f"{PROMPT}{style(message, SECONDARY)}")


def header(title, color=SECONDARY, new_line=False):
    next_line = "\n" if new_line else ""
    text = style(title, "bold" + color)
    divider = rule(LINE_LENGTH - len(title) - 2, color)

    return f"{next_line} {text} {divider}"
