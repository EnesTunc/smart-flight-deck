"""
Smart Flight Deck Companion - WebSocket Handler
Real-time communication with mobile app.
"""

import asyncio
import json
import logging
import base64
import numpy as np
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)

# Connected clients
connected_clients: Set[WebSocket] = set()

# Import VAD processor
from audio.vad_processor import get_vad_processor, remove_vad_session


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
    from .routes import get_sim_connection, try_connect_sim, update_context_from_state

    # Try initial connection
    sim = get_sim_connection()
    if not sim.is_connected:
        try_connect_sim()

    while True:
        try:
            sim = get_sim_connection()

            if sim.is_connected:
                state = sim.update_state()

                # Calculate fuel endurance
                fuel_endurance_min = 0
                if state.fuel_flow_kg_h > 0:
                    fuel_endurance_min = int((state.fuel_total_kg / state.fuel_flow_kg_h) * 60)

                # Build nested data structure matching MOBILE_DESIGN.md format
                sim_data = {
                    "type": "sim_data",
                    "data": {
                        "connected": True,
                        "sim_connected": True,
                        "on_ground": state.on_ground,
                        "aircraft": state.aircraft_title,
                        "flight_phase": update_context_from_state(state),

                        # Nested position data
                        "position": {
                            "latitude": state.latitude,
                            "longitude": state.longitude,
                            "altitude_msl": state.altitude,
                            "altitude_agl": state.altitude_agl,
                            "heading": state.heading,
                            "track": state.track,
                        },

                        # Nested speed data
                        "speed": {
                            "indicated": state.indicated_airspeed,
                            "true": state.true_airspeed,
                            "ground": state.ground_speed,
                            "mach": state.mach,
                            "vertical": state.vertical_speed,
                        },

                        # Nested aircraft data
                        "aircraft": {
                            "title": state.aircraft_title,
                            "gear_position": state.gear_handle_position,
                            "flaps_index": state.flaps_handle_index,
                            "spoilers_armed": state.spoilers_armed,
                        },

                        # Nested fuel data
                        "fuel": {
                            "total_kg": state.fuel_total_kg,
                            "flow_kg_h": state.fuel_flow_kg_h,
                            "endurance_min": fuel_endurance_min,
                        },
                        "fuel_percent": state.fuel_percent,

                        # Nested navigation data
                        "navigation": {
                            "nav1_freq": state.nav1_freq,
                            "nav1_ident": state.nav1_ident,
                            "nav1_dme": state.nav1_dme,
                            "nav2_freq": state.nav2_freq,
                            "nav2_ident": state.nav2_ident,
                            "nav2_dme": state.nav2_dme,
                        },

                        # Nested environment data
                        "environment": {
                            "wind_direction": state.wind_direction,
                            "wind_speed": state.wind_speed,
                            "oat": state.oat,
                            "qnh": state.qnh,
                        },
                    },
                }
            else:
                # Not connected - send minimal data
                sim_data = {
                    "type": "sim_data",
                    "data": {
                        "connected": False,
                        "sim_connected": False,
                    },
                }

            await manager.send_personal(session_token, sim_data)
            await asyncio.sleep(0.5)  # 2 Hz update rate

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Sim data stream error: {e}")
            await asyncio.sleep(1.0)  # Wait before retrying


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

    elif msg_type == "audio_chunk":
        # Streaming audio chunk with VAD
        await handle_audio_chunk(session_token, message)

    elif msg_type == "audio_stream_start":
        # Client started audio streaming
        logger.info(f"Audio stream started: {session_token[:8]}")
        vad = get_vad_processor(session_token)
        vad.reset()

    elif msg_type == "audio_stream_stop":
        # Client stopped audio streaming
        logger.info(f"Audio stream stopped: {session_token[:8]}")
        remove_vad_session(session_token)

    elif msg_type == "pc_stream_start":
        # Client wants to start PC microphone streaming
        await handle_pc_stream_start(session_token)

    elif msg_type == "pc_stream_stop":
        # Client wants to stop PC microphone streaming
        await handle_pc_stream_stop(session_token)

    else:
        logger.warning(f"Unknown message type: {msg_type}")


async def handle_audio_chunk(session_token: str, message: dict):
    """
    Process audio chunk with VAD.

    Message format:
    {
        "type": "audio_chunk",
        "audio": "base64_encoded_float32_pcm",
        "sample_rate": 16000
    }
    """
    try:
        # Decode audio
        audio_base64 = message.get("audio")
        if not audio_base64:
            return

        audio_bytes = base64.b64decode(audio_base64)

        # Mobile sends PCM16 (Int16), convert to float32 (-1.0 to 1.0)
        audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0  # Normalize to -1.0/+1.0

        # Debug: Log first chunk
        if not hasattr(handle_audio_chunk, '_logged_first'):
            logger.info(f"First audio chunk: size={len(audio_float32)}, min={audio_float32.min():.4f}, max={audio_float32.max():.4f}, mean={audio_float32.mean():.4f}")
            handle_audio_chunk._logged_first = True

        # Process with VAD
        vad = get_vad_processor(session_token)
        has_ended, speech_segment = vad.process_chunk(audio_float32)

        if has_ended and speech_segment is not None:
            # Speech segment complete - process it
            logger.info(f"Processing speech segment: {len(speech_segment)/16000:.2f}s")

            # Export as WAV
            wav_bytes = vad.export_wav(speech_segment)

            # Send to command pipeline (same as phone recording)
            # TODO: Integrate with Whisper + Parser + SimConnect
            result = await process_speech_segment(session_token, wav_bytes)

            # Send result back to client
            tts_audio = result.get("tts_audio")
            if tts_audio:
                logger.info(f"✅ Sending command_result with tts_audio: {len(tts_audio)} chars")
            else:
                logger.warning("⚠️ Sending command_result with no tts_audio")

            await manager.send_personal(session_token, {
                "type": "command_result",
                "success": result.get("success", False),
                "command": result.get("command", ""),
                "message": result.get("message", ""),
                "tts_audio": tts_audio,
            })

    except Exception as e:
        logger.error(f"Audio chunk processing error: {e}")


async def process_speech_segment(session_token: str, wav_bytes: bytes) -> dict:
    """
    Process complete speech segment through command pipeline.

    Steps:
    1. Save WAV to temp file
    2. Transcribe with Whisper STT
    3. Parse command
    4. Execute with SimConnect
    5. Generate TTS response
    """
    import tempfile
    from pathlib import Path

    from .routes import (
        get_whisper_stt,
        get_command_parser,
        get_sim_connection,
        try_connect_sim,
        get_piper_tts,
    )
    from logic.commands import CommandRegistry

    try:
        # Save WAV bytes to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(wav_bytes)
            temp_audio_path = Path(temp_audio.name)

        # 1. Transcribe audio with Whisper
        stt = get_whisper_stt()
        transcribed_text, confidence = stt.transcribe(temp_audio_path)

        # Clean up temp file
        temp_audio_path.unlink()

        if not transcribed_text:
            return {
                "success": False,
                "command": "",
                "message": "Could not understand audio",
                "tts_audio": None,
            }

        logger.info(f"Transcribed: '{transcribed_text}' (confidence: {confidence:.2f})")

        # 2. Parse command
        parser = get_command_parser()
        parsed_command = parser.parse(transcribed_text)

        if not parsed_command:
            return {
                "success": False,
                "command": transcribed_text,
                "message": f"Unknown command: {transcribed_text}",
                "tts_audio": None,
            }

        # Get command definition from registry
        command_def = CommandRegistry.get(parsed_command.intent)
        if not command_def or not command_def.sim_event:
            return {
                "success": False,
                "command": transcribed_text,
                "message": f"Command not found: {parsed_command.intent}",
                "tts_audio": None,
            }

        # 3. Execute SimConnect action
        sim = get_sim_connection()
        if not sim.is_connected:
            try_connect_sim()

        if not sim.is_connected:
            return {
                "success": False,
                "command": transcribed_text,
                "message": "Not connected to MSFS",
                "tts_audio": None,
            }

        # Send event to sim
        event_value = parsed_command.parameters.get("value", 0)
        success = sim.send_event(command_def.sim_event, event_value)

        # 4. Generate TTS response
        tts = get_piper_tts()
        response_text = command_def.response_template if success else "Command failed"
        tts_wav = tts.synthesize(response_text)

        # Encode TTS as base64
        if tts_wav:
            logger.info(f"✅ TTS synthesis successful: {len(tts_wav)} bytes")
            tts_base64 = base64.b64encode(tts_wav).decode("utf-8")
            logger.info(f"✅ TTS base64 encoded: {len(tts_base64)} chars")
        else:
            logger.warning("⚠️ TTS synthesis returned empty bytes")
            tts_base64 = None

        return {
            "success": success,
            "command": transcribed_text,
            "message": response_text,
            "tts_audio": tts_base64,
        }

    except Exception as e:
        logger.error(f"Speech segment processing error: {e}")
        return {
            "success": False,
            "command": "",
            "message": f"Processing error: {str(e)}",
            "tts_audio": None,
        }


# PC Microphone Streaming
# Session-based PC recorder instances
_pc_recorders = {}


async def handle_pc_stream_start(session_token: str):
    """
    Start PC microphone streaming with VAD.
    Audio chunks are sent directly to VAD processor via callback.
    """
    from audio.pc_recorder import PcRecorder

    try:
        # Get or create VAD processor for session
        vad = get_vad_processor(session_token)
        vad.reset()

        # Get event loop for async task creation from sync callback
        loop = asyncio.get_event_loop()

        # Define callback that processes audio chunks with VAD
        def audio_chunk_callback(audio_chunk: np.ndarray):
            """Called by PC recorder for each audio chunk."""
            has_ended, speech_segment = vad.process_chunk(audio_chunk)

            if has_ended and speech_segment is not None:
                # Speech segment complete - process it asynchronously
                logger.info(f"[PC] Processing speech segment: {len(speech_segment)/16000:.2f}s")

                # Export as WAV
                wav_bytes = vad.export_wav(speech_segment)

                # Schedule async task from sync callback
                asyncio.run_coroutine_threadsafe(
                    _process_pc_speech_segment(session_token, wav_bytes),
                    loop
                )

        # Create PC recorder and start streaming
        pc_recorder = PcRecorder(sample_rate=16000, channels=1)
        success = pc_recorder.start_streaming(audio_chunk_callback)

        if success:
            # Store recorder instance for session
            _pc_recorders[session_token] = pc_recorder
            logger.info(f"[PC] Streaming started for session: {session_token[:8]}")

            await manager.send_personal(session_token, {
                "type": "pc_stream_status",
                "status": "started",
                "message": "PC microphone streaming started",
            })
        else:
            logger.error(f"[PC] Failed to start streaming for session: {session_token[:8]}")
            await manager.send_personal(session_token, {
                "type": "pc_stream_status",
                "status": "error",
                "message": "Failed to start PC microphone",
            })

    except Exception as e:
        logger.error(f"[PC] Stream start error: {e}")
        await manager.send_personal(session_token, {
            "type": "pc_stream_status",
            "status": "error",
            "message": f"PC streaming error: {str(e)}",
        })


async def handle_pc_stream_stop(session_token: str):
    """Stop PC microphone streaming."""
    try:
        # Get recorder instance
        pc_recorder = _pc_recorders.get(session_token)

        if pc_recorder:
            pc_recorder.stop_streaming()
            del _pc_recorders[session_token]
            logger.info(f"[PC] Streaming stopped for session: {session_token[:8]}")

        # Remove VAD session
        remove_vad_session(session_token)

        await manager.send_personal(session_token, {
            "type": "pc_stream_status",
            "status": "stopped",
            "message": "PC microphone streaming stopped",
        })

    except Exception as e:
        logger.error(f"[PC] Stream stop error: {e}")


async def _process_pc_speech_segment(session_token: str, wav_bytes: bytes):
    """
    Process PC speech segment through pipeline.
    Same as process_speech_segment but sends result via WebSocket.
    """
    result = await process_speech_segment(session_token, wav_bytes)

    # Send result back to client via WebSocket
    await manager.send_personal(session_token, {
        "type": "command_result",
        "success": result.get("success", False),
        "command": result.get("command", ""),
        "message": result.get("message", ""),
        "tts_audio": result.get("tts_audio"),
    })
