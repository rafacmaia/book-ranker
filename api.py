from contextlib import asynccontextmanager

from fastapi import FastAPI

import state
from db.books_repo import get_all
from db.connection import init_db
from leaderboard import rank_books
from services.scoring_service import calculate_progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    state.books = get_all()
    state.progress = calculate_progress(state.books)
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
