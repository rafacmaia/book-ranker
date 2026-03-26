import os

from dotenv import load_dotenv

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")

if not (CLERK_SECRET_KEY and CLERK_JWKS_URL):
    raise RuntimeError(
        "Missing required Clerk config: CLERK_SECRET_KEY and CLERK_JWKS_URL must be set in .env"
    )
