from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

from starlette.requests import Request

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

logger = logging.getLogger("pipelinepilot")


def configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] trace=%(trace_id)s %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class TraceFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_var.get() or "-"
        return True


def ensure_trace_filter() -> None:
    configure_logging()
    filt = TraceFilter()
    for h in logger.handlers:
        if not any(isinstance(f, TraceFilter) for f in h.filters):
            h.addFilter(filt)


def new_trace_id() -> str:
    return str(uuid.uuid4())


async def tracing_middleware(request: Request, call_next):
    ensure_trace_filter()
    incoming = request.headers.get("X-Trace-Id") or request.headers.get("X-Request-Id")
    tid = incoming or new_trace_id()
    token = trace_id_var.set(tid)
    try:
        response = await call_next(request)
        response.headers["X-Trace-Id"] = tid
        return response
    finally:
        trace_id_var.reset(token)


def log_event(event: str, **fields: object) -> None:
    ensure_trace_filter()
    extra = " ".join(f"{k}={v!r}" for k, v in fields.items())
    logger.info("%s %s", event, extra)
