import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import users
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import request_id_var, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # Safety rule: the temporary dev user must never run in production.
    if settings.app_env == "production" and settings.auth_mode == "dev_stub":
        raise RuntimeError("Refusing to start: AUTH_MODE=dev_stub is not allowed in production.")
    yield


app = FastAPI(title="PrepAI API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],   # exact origin only, never "*"
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
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(users.router, prefix="/api/v1")