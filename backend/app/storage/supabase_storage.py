import logging

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)
TIMEOUT = 30


class StorageError(Exception):
    pass


class StorageNotFound(StorageError):
    pass


def _base_url() -> str:
    return f"{settings.supabase_url.rstrip('/')}/storage/v1"


def _headers() -> dict[str, str]:
    key = settings.supabase_service_key
    headers = {"apikey": key}
    if key.startswith("eyJ"):  # legacy JWT-style service key
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _object_url(key: str) -> str:
    return f"{_base_url()}/object/{settings.supabase_storage_bucket}/{key}"


def _check(response: httpx.Response, action: str) -> None:
    if response.status_code < 400:
        return
    body = response.text[:200]
    if response.status_code == 404 or "not found" in body.lower():
        raise StorageNotFound(f"{action}: not found")
    log.error("Storage %s failed: %s %s", action, response.status_code, body)
    raise StorageError(f"Storage {action} failed ({response.status_code})")


def put(key: str, data: bytes, content_type: str) -> None:
    r = httpx.post(
        _object_url(key),
        headers={**_headers(), "Content-Type": content_type, "x-upsert": "false"},
        content=data,
        timeout=TIMEOUT,
    )
    _check(r, "upload")


def get(key: str) -> bytes:
    r = httpx.get(_object_url(key), headers=_headers(), timeout=TIMEOUT)
    _check(r, "download")
    return r.content


def delete(key: str) -> None:
    r = httpx.delete(_object_url(key), headers=_headers(), timeout=TIMEOUT)
    _check(r, "delete")


def signed_url(key: str, seconds: int = 120) -> str:
    r = httpx.post(
        f"{_base_url()}/object/sign/{settings.supabase_storage_bucket}/{key}",
        headers=_headers(),
        json={"expiresIn": seconds},
        timeout=TIMEOUT,
    )
    _check(r, "sign")
    return f"{_base_url()}{r.json()['signedURL']}"