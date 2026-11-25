import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1 import resumes, users
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import request_id_var, setup_logging
from app.db.session import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # Safety rule: the temporary dev user must never run in production.
    if settings.app_env == "production" and settings.auth_mode == "dev_stub":
        raise RuntimeError("Refusing to start: AUTH_MODE=dev_stub is not allowed in production.")
    yield


app = FastAPI(title="Prep Suzy API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],  # exact origin only, never "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-Request-ID"],
)

register_error_handlers(app)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex
    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = rid
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"  # private data must not be cached
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """Confirms the backend can reach Supabase Postgres."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}


app.include_router(users.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")