"""
Smart Flight Deck Companion - WebSocket Handler
Real-time communication with mobile app.
"""

import asyncio
import json
import logging
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)

# Connected clients
connected_clients: Set[WebSocket] = set()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_token: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_token] = websocket
        logger.info(f"Client connected: {session_token[:8]}...")

    def disconnect(self, session_token: str):
        """Remove a WebSocket connection."""
        if session_token in self.active_connections:
            del self.active_connections[session_token]
            logger.info(f"Client disconnected: {session_token[:8]}...")

    async def send_personal(self, session_token: str, message: dict):
        """Send message to specific client."""
        if session_token in self.active_connections:
            await self.active_connections[session_token].send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")


manager = ConnectionManager()


@router.websocket("/stream/{session_token}")
async def websocket_endpoint(websocket: WebSocket, session_token: str):
    """
    WebSocket endpoint for real-time communication.

    Message types:
    - sim_data: Periodic simulator data updates
    - command_result: Result of voice command
    - tts_audio: Text-to-speech audio stream
    - error: Error messages
    """
    # TODO: Validate session token

    await manager.connect(websocket, session_token)

    try:
        # Start background task for sim data streaming
        sim_task = asyncio.create_task(stream_sim_data(session_token))

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            await handle_client_message(session_token, message)

    except WebSocketDisconnect:
        manager.disconnect(session_token)
        sim_task.cancel()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_token)


async def stream_sim_data(session_token: str):
    """Stream simulator data to client at regular intervals."""
    while True:
        try:
            # TODO: Get actual SimConnect data
            sim_data = {
                "type": "sim_data",
                "data": {
                    "connected": False,
                    "altitude": 0,
                    "speed": 0,
                    "heading": 0,
                    "gear_position": 0,
                    "flaps_position": 0,
                    "on_ground": True,
                },
            }

            await manager.send_personal(session_token, sim_data)
            await asyncio.sleep(0.5)  # 2 Hz update rate

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Sim data stream error: {e}")
            break


async def handle_client_message(session_token: str, message: dict):
    """Handle incoming messages from mobile client."""
    msg_type = message.get("type")

    if msg_type == "ping":
        await manager.send_personal(session_token, {"type": "pong"})

    elif msg_type == "command":
        # Direct command (non-voice)
        command = message.get("command")
        # TODO: Execute command and send result
        await manager.send_personal(
            session_token,
            {
                "type": "command_result",
                "success": True,
                "command": command,
                "message": f"Command '{command}' received",
            },
        )

    elif msg_type == "audio_stream":
        # Streaming audio data
        # TODO: Process audio chunks
        pass

    else:
        logger.warning(f"Unknown message type: {msg_type}")
