from fastapi import APIRouter

from sales_api.database import check_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    ok, detail = check_database()
    if not ok:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail=detail)
    return {"status": "ready", "database": detail}
