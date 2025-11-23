# Smart Flight Deck Companion - Setup Guide

## Requirements

### PC (Windows)
- Windows 10/11
- Microsoft Flight Simulator 2020/2024
- Python 3.10+ (for development)
- 4GB+ RAM
- GPU recommended for faster speech recognition

### Mobile
- Android 8.0+ or iOS 14+
- Same Wi-Fi network as PC

---

## Installation

### Option A: Pre-built Installer (Recommended)

1. Download the latest release from [Releases](https://github.com/EnesTunc/smart-flight-deck/releases)
2. Run `SmartFlightDeck_Setup.exe`
3. Follow the installation wizard
4. Allow firewall access when prompted

### Option B: From Source

#### 1. Clone the Repository

```bash
git clone https://github.com/EnesTunc/smart-flight-deck.git
cd smart-flight-deck
```

#### 2. Set Up Python Environment

```bash
cd bridge
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 3. Download AI Models

```bash
python scripts/download_models.py
```

This downloads:
- Whisper base.en (~140MB)
- Piper TTS voice (~50MB)

#### 4. Run the Server

```bash
python main.py
```

---

## First Run

### 1. Start MSFS
Launch Microsoft Flight Simulator and load into a flight.

### 2. Start Smart Flight Deck
Run the PC application. You should see:

```
==================================================
Smart Flight Deck Companion - PC Bridge
==================================================
Local IP: 192.168.1.100
Server: http://192.168.1.100:8080
Whisper Model: base.en
==================================================
```

A QR code will be displayed for mobile connection.

### 3. Connect Mobile App

1. Open Smart Flight Deck on your phone/tablet
2. Tap "Scan QR Code"
3. Point camera at the QR code on your PC
4. Wait for "Connected" confirmation

### 4. Test Commands

1. Hold the PTT (Push-to-Talk) button
2. Say "Gear down"
3. Release the button
4. You should hear "Gear down" confirmation

---

## Troubleshooting

### Connection Issues

#### "Connection Failed" on Mobile

**Causes:**
- PC and mobile not on same network
- Firewall blocking connection
- Wrong IP address

**Solutions:**
1. Ensure both devices are on the same Wi-Fi
2. Run `installer/firewall.ps1` as Administrator
3. Check PC's IP address matches QR code
4. Temporarily disable VPN

#### QR Code Not Scanning

**Solutions:**
1. Increase screen brightness
2. Clean camera lens
3. Hold steady at arm's length
4. Try manual entry if available

---

### SimConnect Issues

#### "Could not connect to MSFS"

**Causes:**
- MSFS not running
- SimConnect not installed

**Solutions:**
1. Start MSFS before the PC app
2. Make sure you're in a flight (not main menu)
3. Reinstall MSFS SDK if needed

#### "SimConnect Connection Lost"

**Causes:**
- MSFS crashed
- Flight ended

**Solutions:**
1. Restart MSFS
2. Load a new flight
3. Restart PC application

---

### Audio Issues

#### Voice Not Recognized

**Causes:**
- Microphone too quiet
- Background noise
- Speaking too fast

**Solutions:**
1. Check microphone permissions on phone
2. Speak clearly and at normal pace
3. Use headphones to reduce echo
4. Reduce background noise

#### No TTS Response

**Causes:**
- PC audio muted
- Piper model not loaded

**Solutions:**
1. Check PC volume
2. Verify Piper model is in `models/` directory
3. Check console for TTS errors

---

### Performance Issues

#### High Latency

**Causes:**
- Slow network
- CPU overloaded
- Large Whisper model

**Solutions:**
1. Use 5GHz Wi-Fi instead of 2.4GHz
2. Close unnecessary applications
3. Switch to `tiny.en` Whisper model
4. Enable GPU acceleration if available

#### High CPU Usage

**Solutions:**
1. Use smaller Whisper model (`tiny.en`)
2. Reduce sim data update frequency
3. Close browser tabs

---

## Configuration

### Environment Variables

Create `.env` file in `bridge/` directory:

```bash
# Server
SFDC_HOST=0.0.0.0
SFDC_PORT=8080
SFDC_DEBUG=false

# Whisper
SFDC_WHISPER_MODEL=base.en
SFDC_WHISPER_DEVICE=cpu  # or cuda

# Piper
SFDC_PIPER_VOICE=en_US-lessac-medium
```

### Changing Whisper Model

Available models (speed vs accuracy):

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny.en | 75MB | Fastest | Basic |
| base.en | 140MB | Fast | Good |
| small.en | 460MB | Medium | Better |

Edit `.env`:
```bash
SFDC_WHISPER_MODEL=small.en
```

---

## Uninstallation

### Installer Version
1. Open Windows Settings → Apps
2. Find "Smart Flight Deck Companion"
3. Click Uninstall

### Source Version
1. Delete the project folder
2. Remove Python virtual environment
