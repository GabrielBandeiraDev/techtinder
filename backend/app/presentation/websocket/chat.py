import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import get_settings
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.security.jwt import safe_decode
from app.application.services.match_service import MatchService

router = APIRouter()

_connections: dict[int, set[WebSocket]] = {}


async def _authenticate_ws(websocket: WebSocket) -> int | None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return None
    settings = get_settings()
    payload = safe_decode(token, settings)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4401)
        return None
    return int(payload["sub"])


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(websocket: WebSocket, conversation_id: int) -> None:
    user_id = await _authenticate_ws(websocket)
    if user_id is None:
        return

    async with AsyncSessionLocal() as session:
        service = MatchService(session)
        try:
            messages = await service.list_messages(user_id, conversation_id, limit=1)
            _ = messages
        except Exception:
            await websocket.accept()
            await websocket.send_json(
                {"error": "Chat disponível apenas após match."}
            )
            await websocket.close(code=4403)
            return

    await websocket.accept()
    _connections.setdefault(conversation_id, set()).add(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data: dict[str, Any] = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "JSON inválido."})
                continue

            text = (data.get("message") or "").strip()
            if not text:
                continue

            async with AsyncSessionLocal() as session:
                service = MatchService(session)
                msg = await service.send_message(user_id, conversation_id, text)
                payload = {
                    "type": "message",
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "sender_id": msg.sender_id,
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat(),
                }

            for conn in list(_connections.get(conversation_id, set())):
                try:
                    await conn.send_json(payload)
                except Exception:
                    _connections.get(conversation_id, set()).discard(conn)

    except WebSocketDisconnect:
        pass
    finally:
        _connections.get(conversation_id, set()).discard(websocket)
