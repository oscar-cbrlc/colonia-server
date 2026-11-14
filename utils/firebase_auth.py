import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

firebase_bearer = HTTPBearer(auto_error=False)


def get_firebase_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(firebase_bearer),
) -> dict[str, str]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        app = firebase_admin.get_app()
    except ValueError:
        try:
            app = firebase_admin.initialize_app()
        except ValueError:
            app = firebase_admin.get_app()

    try:
        claims = auth.verify_id_token(
            credentials.credentials,
            app=app,
            check_revoked=True,
        )
    except (
        auth.InvalidIdTokenError,
        auth.UserDisabledError,
        auth.UserNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    uid = claims.get("uid")
    email = claims.get("email")
    if not uid or not isinstance(email, str) or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase account must have a valid email address.",
        )
    if claims.get("email_verified") is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase email must be verified.",
        )

    return {"uid": uid, "email": email.strip().lower()}