from fastapi import WebSocket
import contextvars

# Context variable to hold the active WebSocket per request context
_current_websocket: contextvars.ContextVar[WebSocket | None] = contextvars.ContextVar(
    "current_websocket", default=None
)


def set_current_websocket(ws: WebSocket) -> None:
    """
    Call this once at the start of each WebSocket session (e.g., in the FastAPI handler)
    """
    _current_websocket.set(ws)


async def emit_step(step: str) -> None:
    """
    Emits a step name to the frontend via WebSocket (e.g., for progress feedback).
    Should be awaited at the BEGINNING of each node function.
    """
    ws = _current_websocket.get()
    if ws:
        await ws.send_json({"type": "step", "node": step})
