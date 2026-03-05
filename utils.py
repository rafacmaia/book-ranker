PROMPT = "\033[1;33m > \033[0m"


def prompt(options, error_message="Invalid choice, please try again.", p=PROMPT):
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


def progress_bar(pct, width=20):
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
