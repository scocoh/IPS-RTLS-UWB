# Name: websocket_event.py
# Version: 0.1.1
# Created: 250525
# Modified: 250525
# Creator: ParcoAdmin
# Description: Real-time WebSocket stream for Parco Event Engine
# Location: /home/parcoadmin/parco_fastapi/app/routes/websocket_event.py
# Role: WebSocket Interface for TETSE
# Status: Active
# Dependent: TRUE

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from manager.manager import Manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/event_stream/{entity_id}")
async def ws_event_stream(websocket: WebSocket, entity_id: str):
    """
    WebSocket stream for event updates per entity_id.
    Clients subscribe to: /ws/event_stream/{entity_id}
    Any published event (via insert) will be broadcast in real-time.
    """
    topic = f"ws_event_{entity_id}"
    await websocket.accept()
    logger.info(f"[WebSocket] Client connected to {topic}")

    await Manager.add_client(topic, websocket)

    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        logger.info(f"[WebSocket] Client disconnected from {topic}")
        await Manager.remove_client(topic, websocket)
    except Exception as e:
        logger.error(f"[WebSocket] Error on {topic}: {str(e)}")
        await Manager.remove_client(topic, websocket)
