# Smart Flight Deck Companion - API Reference

## Base URL

```
http://{PC_IP}:8080
```

## Authentication

All requests (except `/` and `/health`) require a session token:

```
Header: X-Session-Token: <session_token>
```

Session tokens are obtained by scanning the QR code displayed by the PC application.

---

## Endpoints

### General

#### GET /
Root endpoint - basic application info.

**Response:**
```json
{
  "name": "Smart Flight Deck Companion",
  "version": "0.1.0",
  "status": "running",
  "ip": "192.168.1.100",
  "port": 8080
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "simconnect": true,
  "whisper_loaded": true,
  "piper_loaded": true
}
```

---

### Connection

#### GET /api/connect/qr
Generate a QR code for mobile app connection.

**Response:**
```json
{
  "qr_image": "data:image/png;base64,...",
  "connection_info": {
    "ip": "192.168.1.100",
    "port": 8080,
    "session_token": "abc123...",
    "expires_at": "2025-01-15T10:10:00Z"
  }
}
```

#### POST /api/connect/verify
Verify mobile app connection.

**Headers:**
- `X-Session-Token`: Session token from QR code

**Response:**
```json
{
  "status": "connected",
  "message": "Mobile app connected successfully"
}
```

---

### Audio

#### POST /api/audio/transcribe
Transcribe audio to text.

**Headers:**
- `X-Session-Token`: Session token
- `Content-Type`: multipart/form-data

**Body:**
- `audio`: WAV file (16kHz, mono)

**Response:**
```json
{
  "text": "gear down",
  "confidence": 0.95,
  "language": "en",
  "duration": 1.5
}
```

#### POST /api/audio/command
Full pipeline: transcribe, parse, execute, and respond.

**Headers:**
- `X-Session-Token`: Session token
- `Content-Type`: multipart/form-data

**Body:**
- `audio`: WAV file (16kHz, mono)

**Response:**
```json
{
  "success": true,
  "command": "gear down",
  "action": "GEAR_DOWN",
  "message": "Gear is down",
  "tts_audio": "data:audio/wav;base64,..."
}
```

---

### Simulator

#### GET /api/sim/status
Get current simulator status.

**Headers:**
- `X-Session-Token`: Session token

**Response:**
```json
{
  "connected": true,
  "aircraft": "Airbus A320neo",
  "flight_phase": "cruise",
  "altitude": 35000,
  "speed": 450,
  "gear_position": 0
}
```

#### POST /api/sim/command/{command}
Execute a direct simulator command.

**Headers:**
- `X-Session-Token`: Session token

**Path Parameters:**
- `command`: Command ID (e.g., `gear_toggle`, `flaps_up`)

**Response:**
```json
{
  "success": true,
  "command": "gear_toggle",
  "message": "Command 'gear_toggle' executed"
}
```

**Available Commands:**
| Command | Description |
|---------|-------------|
| `gear_toggle` | Toggle landing gear |
| `gear_up` | Retract landing gear |
| `gear_down` | Extend landing gear |
| `flaps_up` | Retract flaps one notch |
| `flaps_down` | Extend flaps one notch |
| `parking_brake` | Toggle parking brake |

---

## WebSocket

### WS /ws/stream/{session_token}

Real-time bidirectional communication.

**URL:**
```
ws://{PC_IP}:8080/ws/stream/{session_token}
```

### Server → Client Messages

#### sim_data
Periodic simulator data updates (2 Hz).

```json
{
  "type": "sim_data",
  "data": {
    "connected": true,
    "altitude": 35000,
    "speed": 450,
    "heading": 270,
    "gear_position": 0,
    "flaps_position": 0,
    "on_ground": false
  }
}
```

#### command_result
Result of a command execution.

```json
{
  "type": "command_result",
  "success": true,
  "command": "gear_down",
  "message": "Gear is down"
}
```

#### pong
Response to ping.

```json
{
  "type": "pong"
}
```

### Client → Server Messages

#### ping
Keep-alive ping.

```json
{
  "type": "ping"
}
```

#### command
Direct command (button press).

```json
{
  "type": "command",
  "command": "gear_toggle"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or expired session |
| 404 | Not Found - Endpoint doesn't exist |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Audio endpoints: 10 requests/minute
- Command endpoints: 60 requests/minute
- Status endpoints: 120 requests/minute
