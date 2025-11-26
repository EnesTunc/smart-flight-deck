"""
Smart Flight Deck Companion - TTS Voice Downloader
Downloads commercial-safe Piper TTS voices.
"""

import requests
import sys
from pathlib import Path
from typing import Dict, List

# Voice definitions (all Public Domain - commercial use safe)
VOICES: Dict[str, Dict] = {
    "ljspeech": {
        "display_name": "Linda (US Female)",
        "gender": "female",
        "accent": "US",
        "quality": "high",
        "license": "Public Domain",
        "onnx_url": "https://sfo3.digitaloceanspaces.com/bkmdls/ljspeech.onnx",
        "json_url": "https://sfo3.digitaloceanspaces.com/bkmdls/ljspeech.onnx.json",
    },
    "cori-high": {
        "display_name": "Cori (UK Female)",
        "gender": "female",
        "accent": "UK",
        "quality": "high",
        "license": "Public Domain",
        "onnx_url": "https://sfo3.digitaloceanspaces.com/bkmdls/cori-high.onnx",
        "json_url": "https://sfo3.digitaloceanspaces.com/bkmdls/cori-high.onnx.json",
    },
    "john": {
        "display_name": "John (US Male)",
        "gender": "male",
        "accent": "US",
        "quality": "medium",
        "license": "Public Domain",
        "onnx_url": "https://sfo3.digitaloceanspaces.com/bkmdls/john.onnx",
        "json_url": "https://sfo3.digitaloceanspaces.com/bkmdls/john.onnx.json",
    },
    "bryce": {
        "display_name": "Bryce (US Male)",
        "gender": "male",
        "accent": "US",
        "quality": "medium",
        "license": "Public Domain",
        "onnx_url": "https://sfo3.digitaloceanspaces.com/bkmdls/bryce.onnx",
        "json_url": "https://sfo3.digitaloceanspaces.com/bkmdls/bryce.onnx.json",
    },
}


def download_file(url: str, output_path: Path, retries: int = 3) -> bool:
    """Download a file with progress indicator and retry logic."""
    for attempt in range(retries):
        try:
            if attempt > 0:
                print(f"  Retry {attempt}/{retries-1}...", end=" ", flush=True)
            else:
                print(f"  Downloading {output_path.name}...", end=" ", flush=True)

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Progress indicator
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\r  Downloading {output_path.name}... {percent:.0f}%", end="", flush=True)

            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\r  Downloading {output_path.name}... OK ({size_mb:.1f} MB)")
            return True

        except Exception as e:
            print(f"\r  Downloading {output_path.name}... FAILED: {e}")
            if attempt < retries - 1:
                print(f"  Retrying...")
            else:
                print(f"  Give up after {retries} attempts")
                return False

    return False


def download_voice(voice_id: str, voice_info: Dict, models_dir: Path) -> bool:
    """Download a single TTS voice."""
    print(f"\n{'='*60}")
    print(f"Voice: {voice_info['display_name']}")
    print(f"  Gender: {voice_info['gender']}")
    print(f"  Accent: {voice_info['accent']}")
    print(f"  Quality: {voice_info['quality']}")
    print(f"  License: {voice_info['license']}")
    print(f"{'='*60}")

    # Create voice directory
    voice_dir = models_dir / voice_id
    voice_dir.mkdir(parents=True, exist_ok=True)

    # Download model file
    onnx_path = voice_dir / f"{voice_id}.onnx"
    if not download_file(voice_info['onnx_url'], onnx_path):
        return False

    # Download config file
    json_path = voice_dir / f"{voice_id}.onnx.json"
    if not download_file(voice_info['json_url'], json_path):
        return False

    # Create metadata file
    metadata_path = voice_dir / "MODEL_CARD"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(f"# Model card for {voice_id}\n\n")
        f.write(f"* Voice: {voice_info['display_name']}\n")
        f.write(f"* Gender: {voice_info['gender']}\n")
        f.write(f"* Accent: {voice_info['accent']}\n")
        f.write(f"* Quality: {voice_info['quality']}\n")
        f.write(f"* License: {voice_info['license']}\n\n")
        f.write("## Commercial Use\n\n")
        f.write("[OK] Safe for commercial use (Public Domain)\n\n")
        f.write("## Source\n\n")
        f.write("https://brycebeattie.com/files/tts/\n")

    print(f"[OK] Voice '{voice_id}' installed successfully")
    return True


def main():
    """Main download function."""
    print("\n" + "="*60)
    print("  Smart Flight Deck Companion - TTS Voice Installer")
    print("="*60)
    print("\nDownloading 4 commercial-safe voices...")
    print("All voices are Public Domain (safe for commercial use)")

    # Determine models directory
    script_dir = Path(__file__).parent
    bridge_dir = script_dir.parent
    models_dir = bridge_dir / "models" / "piper"

    print(f"\nInstall location: {models_dir}")

    # Create directory
    models_dir.mkdir(parents=True, exist_ok=True)

    # Download all voices
    success_count = 0
    for voice_id, voice_info in VOICES.items():
        if download_voice(voice_id, voice_info, models_dir):
            success_count += 1

    # Summary
    print("\n" + "="*60)
    print(f"Installation complete: {success_count}/{len(VOICES)} voices")
    print("="*60)

    if success_count == len(VOICES):
        print("\n[OK] All voices installed successfully!")
        print("\nAvailable voices:")
        for voice_id, voice_info in VOICES.items():
            print(f"  - {voice_id}: {voice_info['display_name']}")
        print("\nDefault voice: ljspeech (Linda)")
        return 0
    else:
        print("\n[WARNING] Some voices failed to download")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
