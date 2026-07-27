from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from sales_api.database import persist_flag
from sales_api.store import get_flags, get_metrics, set_flag

router = APIRouter(prefix="/admin", tags=["admin"])


class FlagUpdate(BaseModel):
    enabled: bool


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    return get_metrics()


@router.get("/flags")
def flags(request: Request) -> dict[str, bool]:
    return request.app.state.flags


@router.post("/flags/{key}")
def update_flag(key: str, body: FlagUpdate, request: Request) -> dict[str, bool]:
    set_flag(key, body.enabled)
    request.app.state.flags[key] = body.enabled
    persist_flag(key, body.enabled)
    return request.app.state.flags
