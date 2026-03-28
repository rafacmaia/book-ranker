import os

from dotenv import load_dotenv

load_dotenv()

# ====== APP CONFIG

BOOK_LIMIT = 2000
DEFAULT_RATING = 6.2

# ====== CLERK AUTH

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
