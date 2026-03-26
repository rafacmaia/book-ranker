import jwt
import requests
from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.algorithms import RSAAlgorithm

from config import CLERK_JWKS_URL

# HTTPBearer extracts the token from the Authorization: Bearer <token> header
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """Verify the JWT and return the Clerk user ID.

    Inject this into any endpoint that requires authentication.
    """
    token = credentials.credentials

    try:
        public_key = _get_public_key(token)
        payload = jwt.decode(
            token, public_key, algorithms=["RS256"], options={"verify_audience": False}
        )
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token missing required claim")
        return sub  # Clerk user ID lives in the "sub" claim

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def _get_public_key(token):
    """Find the matching public key for the given token from Clerk's JWKS."""
    jwks = _get_jwks()
    headers = jwt.get_unverified_header(token)

    headers_kid = headers.get("kid")
    if not headers_kid:
        raise HTTPException(status_code=401, detail="Invalid token: missing kid")

    for key in jwks["keys"]:
        if key.get("kid") == headers_kid:
            return RSAAlgorithm.from_jwk(key)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="No matching public key found"
    )


def _get_jwks():
    """Fetch Clerk's public keys (JWKS) for JWT verification."""
    response = requests.get(CLERK_JWKS_URL)
    response.raise_for_status()  # Raise an exception if there's an HTTP error
    return response.json()
