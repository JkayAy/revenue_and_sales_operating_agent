from __future__ import annotations

from sales_api.config import settings


def pg_dsn() -> str | None:
    url = settings.database_url.strip()
    if not url:
        return None
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


def db_enabled() -> bool:
    return pg_dsn() is not None


def check_database() -> tuple[bool, str]:
    if not db_enabled():
        return True, "disabled"
    try:
        import psycopg

        with psycopg.connect(pg_dsn(), connect_timeout=5) as conn:
            conn.execute("SELECT 1")
        return True, "connected"
    except Exception as exc:  # noqa: BLE001
        return False, f"error: {exc}"


def load_flags_from_db() -> dict[str, bool]:
    dsn = pg_dsn()
    if not dsn:
        return {}
    import psycopg

    out: dict[str, bool] = {}
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        rows = conn.execute("SELECT key, enabled FROM feature_flags").fetchall()
        for key, enabled in rows:
            out[str(key)] = bool(enabled)
    return out


def persist_flag(key: str, enabled: bool) -> None:
    dsn = pg_dsn()
    if not dsn:
        return
    import psycopg

    with psycopg.connect(dsn, connect_timeout=5) as conn:
        conn.execute(
            """
            INSERT INTO feature_flags (key, enabled, payload)
            VALUES (%s, %s, '{}')
            ON CONFLICT (key) DO UPDATE
            SET enabled = EXCLUDED.enabled, updated_at = now()
            """,
            (key, enabled),
        )
        conn.commit()
