# 📚 Book Ranker

![Status](https://img.shields.io/badge/status-in--development-yellow)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Last commit](https://img.shields.io/github/last-commit/rafacmaia/book-ranker)

You've read dozens (hundreds?) of books and vaguely know you like some better than
others. But which one was actually your favourite? Your top 20? Top 42? And was that
rating of 7 you gave in 2021 really fair compared to the 8 you handed out last week?

Book Ranker cuts through the noise by turning your reading log into a tournament. It pits
two books head-to-head and asks one simple question:

> Which book means more to you, A or B?

Over time, an Elo-based rating system does the math and builds a ranked list that
reflects your ultimate breakdown. No more stuttering when someone asks you what your 33rd
favorite book of all time is. Those days are over!

## 🪄 Preview

<details>
<summary><b>&nbsp;Screenshots of latest version</b></summary>

<h3>Book Arena:</h3>
<img src="screenshots/game-arena-1.png" alt="Game Arena Start">
<img src="screenshots/game-arena-2.png" alt="Game Arena ongoing comparisons">
<img src="screenshots/game-arena-3.png" alt="Game Arena ongoing comparisons">

<h3>View Rankings:</h3>
<img src="screenshots/rankings-1.png" alt="Rankings display 1">
<img src="screenshots/rankings-2.png" alt="Rankings display 2">


</details>

## 🪩 Features

- CSV import from your reading log (format: title, author, rating)
- Book Arena: head-to-head book comparisons on loop
- Elo-based ranking system with confidence tiers and variable K values
- Smart matchmaking: prioritize books with lower confidence rating, similar Elo
  scores, and unmatched pairs
- Multifactor confidence scoring: measures both individual and overall confidence
  in rankings
- Persistent rankings via SQLite to build accurate data over time
- Add new books at any time: New books are mapped into the current Elo range based on
  their original rating, ensuring intelligent initial positioning before the game can
  refine it.
- Confidence and matchmaking algorithms are optimized to avoid full pairwise comparisons,
  allowing the system to scale efficiently to libraries of 2500+ books.
- Export your rankings to CSV

_See the [How it Works](#-how-it-works) section below for more details._

## 📋 Requirements

- Python 3.x
- [Rich](https://github.com/Textualize/rich) — terminal formatting

## ⚙️ Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/rafacmaia/book-ranker.git
   cd book-ranker
   ```


2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```


3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


4. Run the app:
   ```bash
   python main.py
   ```
   In the first run, you'll be prompted to import your book log from a CSV file.


5. To run on sample or test data instead of your own library:
   ```bash
   python main.py --test
   ```
   *Note, a sample CSV with 20 books is included at [
   `data/sample-books.csv`](data/sample-books.csv) to get you started.*

## 📃 CSV Format

Your CSV file should have the following columns:
> title, author, rating

Where rating is a number from 1 to 10, inclusive. Decimals encouraged!

Example:

```csv
title,author,rating
Confessions of a Mask,Yukio Mishima,6.5
The Republic,Plato,8
"Rich Dad, Poor Dad",Robert Kiyosaki,3.5 
Just Kids,Patti Smith,9
```

## 📖 How It Works

Each book starts with an Elo score derived from your initial rating (1–10 scale, mapped
to an initial 800–1200 range). From there, rankings are determined entirely through
head-to-head comparisons.

Every time a book wins a matchup, both books’ Elo scores are updated using the standard
Elo formula. However, this implementation extends basic Elo with adaptive volatility and
stability modeling to improve convergence speed and ranking reliability.

#### Adaptive K-Factor

The Elo K-value (which determines how much a rating can change in a single match) adapts
dynamically based on ranking confidence:

- Low-confidence books have higher K values, allowing them to move quickly toward their
  appropriate tier.

- High-confidence books gradually shift to lower K values, reducing volatility as their
  position stabilizes.

This ensures fast early convergence without sacrificing long-term ranking stability.

### 🔍 Confidence Calculation

Each book’s confidence score represents how stable its current ranking is. It is
calculated as a weighted combination of three independent signals:

1. **Absolute Coverage** – How many unique opponents the book has faced. This ensures
   broad exposure across the library.
2. **Local Coverage** – How thoroughly the book has been tested against competitively
   similar opponents (based on expected win probability, not just raw Elo difference).
   This refines placement within its tier.
3. **Local Density (Rank Fragility)** – Measures how many nearby books sit within a
   narrow Elo band. Even if a book has strong coverage, tight clusters indicate potential
   short-term rank instability. High density prevents premature “Very High” confidence
   assignments.

#### Confidence Tiers

- 🔴 Very Low: Early data, ranking mostly based on initial rating
- 🟠 Low: Some data, broad tier is likely correct (top/mid/bottom)
- 🟡 Moderate: General position is fairly reliable, exact rank still shifting
- 🟢 High: Position is well established, likely within ~10 spots
- ✅ Very High: Locked in, unlikely to shift significantly

### 🎯 Intelligent Matchmaking

Matchups are not random.

The Book Arena uses weighted stochastic matchmaking designed to maximize information gain
and accelerate ranking convergence.

Pair selection prioritizes:

- Books with very few matches (to quickly obtain some data on every book)
- Rare or unmatched pairings
- Matchups between books with similar Elo score (where outcomes are most informative)
- Books with lower confidence (to maximize overall ranking confidence)

The result is a system that converges efficiently while still allowing occasional
cross-tier matchups to maintain global calibration.

### Why This Matters

Instead of treating ranking as a static score, Book Ranker models:

- Volatility (via adaptive K)
- Information gain (via weighted matchmaking)
- Local instability (via density detection)
- Progressive convergence toward stable rankings

The outcome is a ranking system that becomes more reliable over time, without ever fully
freezing into rigidity. Giving book lovers and ranking enthusiasts a fun, but also
mathematically robust, way to reflect on their books.

## 🗂️ Project Structure

| File                               | Description                                                   |
|------------------------------------|---------------------------------------------------------------|
| [`main.py`](main.py)               | Entry point and main menu                                     |
| [`game.py`](game.py)               | Game loop and matchmaking logic                               |
| [`models.py`](models.py)           | Book class                                                    |
| [`db.py`](db.py)                   | Database setup and queries                                    |
| [`csv_handler.py`](csv_handler.py) | CSV import and export logic                                   |
| [`display.py`](display.py)         | Rankings display and UI constants                             |
| [`state.py`](state.py)             | Global state management                                       |
| [`ranking.py`](ranking.py)         | Mathematical calculations of Elo scores and confidence levels |

## 🗺️ Roadmap

- [X] Track confidence tiers for Elo ratings to indicate the reliability of current
  rankings
- [X] Improve matchmaking (prioritize books with similar Elo scores, unmatched pairs,
  and lower confidence ratings)
- [X] CSV export of final rankings
- [ ] Handle tied Elo scores (e.g., by initial rating, head-to-head comparison, and
  confidence rating)
- [ ] Support for adding/removing individual books
- [ ] Undo option for mistakes (track and undo the last 1–3 face-offs)
- [ ] Filter rankings by genre, author, or year read (e.g., "2021" or "Fantasy")
- [ ] Web terminal; serve the CLI interface via browser (Flask + xterm.js)
- [ ] Web UI, full browser-based interface (longer term)
  
