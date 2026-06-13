import os

from fastapi import HTTPException, Request

from models.db import supabase


def _is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def safe_error_detail(error: Exception, fallback: str = "Internal server error") -> str:
    if _is_production():
        return fallback
    return str(error)


async def get_session_user(request: Request):
    """Return the Supabase auth user from the session cookie, or raise 401."""
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        auth_result = supabase.auth.get_user(session_token)
        user = getattr(auth_result, "user", None)
    except Exception:
        user = None

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user


async def require_teacher_access(request: Request, teacher_id: str) -> str:
    """Ensure the authenticated user owns the requested teacher record."""
    user = await get_session_user(request)

    existing = (
        supabase.table("teachers")
        .select("id")
        .eq("id", teacher_id)
        .eq("auth_user_id", user.id)
        .limit(1)
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=403, detail="Access denied")

    return teacher_id
