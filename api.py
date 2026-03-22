from contextlib import asynccontextmanager

from fastapi import FastAPI

import state
from db import init_db
from leaderboard import rank_books
from models import Book
from scoring import calculate_progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    state.books = Book.load_all()
    calculate_progress()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/rankings")
def get_rankings():
    ranked_books = rank_books()
    return [
        {
            "Rank": rank,
            "Title": book.title,
            "Author": book.author,
        }
        for rank, book in ranked_books
    ]
