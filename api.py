from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

import state
from auth import get_current_user
from db.books_repo import get_all
from db.connection import init_db
from services.ranking_service import rank_books
from services.scoring_service import calculate_progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(state.db_path)
    state.books = get_all()
    state.progress = calculate_progress(state.books)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/rankings")
def get_rankings(user_id: str = Depends(get_current_user)):
    ranked_books = rank_books(state.books)
    return [
        {
            "Rank": rank,
            "Title": book.title,
            "Author": book.author,
        }
        for rank, book in ranked_books
    ]
