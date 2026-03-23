-- Book Brawl Database Schema
-- Last updated: 2026-03-22
--
-- To recreate the database from scratch:
--   sqlite3 data/book_brawl.db < db/schema.sql
--
-- For incremental changes to an existing database, use db/migrate.py instead.


CREATE TABLE IF NOT EXISTS user (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    NOT NULL UNIQUE,
    email     TEXT    NOT NULL UNIQUE,
    clerk_id  TEXT    NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS book (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL REFERENCES user(id),
    title    TEXT    NOT NULL,
    author   TEXT    NOT NULL,
    rating   REAL    DEFAULT NULL,
    elo      INTEGER DEFAULT 1000,
    UNIQUE (user_id, title, author)   -- same book can exist for different users
);


CREATE TABLE IF NOT EXISTS comparison (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER   NOT NULL REFERENCES user(id),
    winner_id  INTEGER   NOT NULL REFERENCES book(id),
    loser_id   INTEGER   NOT NULL REFERENCES book(id),
    timestamp  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Indexes to speed up the frequent queries.
CREATE INDEX IF NOT EXISTS idx_book_user       ON book(user_id);
CREATE INDEX IF NOT EXISTS idx_comparison_user ON comparison(user_id);
CREATE INDEX IF NOT EXISTS idx_comparison_winner ON comparison(winner_id);
CREATE INDEX IF NOT EXISTS idx_comparison_loser  ON comparison(loser_id);
