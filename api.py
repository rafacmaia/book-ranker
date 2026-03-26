from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from pydantic import BaseModel

import state
from auth import get_current_user
from db import users_repo
from db.books_repo import get_all
from db.connection import init_db
from services.ranking_service import rank_books
from services.scoring_service import calculate_progress

# ====== APP SETUP


class UserSync(BaseModel):
    email: str
    username: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(state.db_path)
    state.books = get_all()
    state.progress = calculate_progress(state.books)
    yield


app = FastAPI(lifespan=lifespan)


# ====== LEADERBOARD


@app.get("/leaderboard")
def get_leaderboard(user_id: str = Depends(get_current_user)):
    ranked_books = rank_books(state.books)
    return [
        {
            "rank": rank,
            "title": book.title,
            "author": book.author,
        }
        for rank, book in ranked_books
    ]


# ====== READERS


@app.post("/readers")
def sync_user(data: UserSync, clerk_id: str = Depends(get_current_user)):
    """Create a new user record on the first login or return an existing one."""
    user = users_repo.get_by_clerk_id(clerk_id)

    if not user:
        user_id = users_repo.insert(clerk_id, data.email, data.username)
        return {"id": user_id, "clerk_id": clerk_id, "created": True}

    return {"id": user["id"], "clerk_id": clerk_id, "created": False}
