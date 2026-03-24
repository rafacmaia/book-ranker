from collections import namedtuple

import state
from constants import (
    PIT_OPTIONS,
)
from messages import PIT_INSTRUCTIONS
from services.game_service import resolve_comparison, select_opponents
from theme import DIVIDER, ERROR, LINE_LENGTH, PROMPT, REDO, SECONDARY
from utils import format_book, header, press_enter, prompt, rule, style

PendingMatch = namedtuple("PendingMatch", ["match", "a", "b", "choice"])


def run_game():
    """Run the game's main loop.

    Select two books for comparison, prompt the user for choice between the two,
    resolve the match, and repeat until the user stops.
    """
    print(header("BRAWL PIT", new_line=True))

    if len(state.books) <= 1:
        print(
            f" {style('Not enough books in the pit.', ERROR)} Add some more and try again."
        )
        press_enter()
        return None

    print_instructions()

    match_count = 1
    book_a, book_b = select_opponents(state.books)
    previous = None
    opponents_selected = True
    while True:
        if not opponents_selected:
            match_count += 1
            book_a, book_b = select_opponents(state.books)

        print_match(match_count, book_a, book_b)
        choice = prompt(options=PIT_OPTIONS)

        while choice == "u" and previous is None:
            print(f"{PROMPT}No previous match to undo.")
            choice = prompt(options=PIT_OPTIONS)

        if choice == "u":
            opponents_selected = True  # Makes sure the interrupted match gets reprinted
            previous = rematch(previous)
            continue

        if previous:
            resolve_comparison(previous.a, previous.b, previous.choice, state.books)

        if choice in ["q", "b"]:
            return choice

        previous = PendingMatch(match_count, book_a, book_b, choice)
        opponents_selected = False


def print_instructions():
    instructions = (
        f" {style(len(state.books), SECONDARY)} books enter."
        f" {style('One wins.', SECONDARY)}\n"
    )

    instructions += PIT_INSTRUCTIONS

    print(instructions, end="")
    input()


def print_match(match_count, book_a, book_b, redo=False):
    match_divider = (
        f" {rule((LINE_LENGTH - 5 - len(str(match_count))), DIVIDER)}"
        f" {style(match_count, DIVIDER)}"
        f" {rule(2, DIVIDER)}"
    )

    redo_divider = (
        f" {rule(2, REDO)}"
        f" {style('REMATCH', REDO)}"
        f" {rule((LINE_LENGTH - 16 - len(str(match_count))), REDO)}"
        f" {style(match_count, REDO)}"
        f" {rule(2, REDO)}"
    )

    match = (
        f" {style('Which means more to you?', SECONDARY)}\n"
        f"   {style('1.', SECONDARY)} {format_book(book_a)}\n"
        f"   {style('2.', SECONDARY)} {format_book(book_b)}"
    )

    divider = match_divider if not redo else redo_divider

    print("\n" + divider + "\n" + match)


def rematch(previous):
    print_match(previous.match, previous.a, previous.b, redo=True)
    new_choice = prompt(options=["1", "2"])
    return PendingMatch(previous.match, previous.a, previous.b, new_choice)
