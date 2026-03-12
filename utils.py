import state

PROMPT = "\033[1;33m > \033[0m"


def prompt(options, error_message=None, p=PROMPT):
    if not error_message:
        error_message = f"Invalid option, please try: {', '.join(options)}"

    while True:
        choice = input(f"{p}").strip().lower()
        if choice in options:
            return choice
        print(f"{p}\033[31m{error_message}\033[0m")


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


def rankings_summary(pct, color="bold green"):
    summary = f" Your library:       {style(f'{len(state.books)} Books', color)}"
    summary += f"\n Current confidence: {style(progress_bar(pct, 20), color)}\n"

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
        summary += " Absolute ranking of all books established!"

    return summary


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
