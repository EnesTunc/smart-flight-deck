"""
Smart Flight Deck Companion - Text-to-Speech
Piper TTS integration for voice responses.

All voices are Public Domain - safe for commercial use.
"""

import logging
import wave
import io
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


# Available voices (all Public Domain - commercial use safe)
AVAILABLE_VOICES: Dict[str, Dict] = {
    "ljspeech": {
        "display_name": "Linda (US Female)",
        "gender": "female",
        "accent": "US",
        "quality": "high",
        "license": "Public Domain",
        "file_prefix": "ljspeech",
    },
    "cori-high": {
        "display_name": "Cori (UK Female)",
        "gender": "female",
        "accent": "UK",
        "quality": "high",
        "license": "Public Domain",
        "file_prefix": "cori-high",
    },
    "john": {
        "display_name": "John (US Male)",
        "gender": "male",
        "accent": "US",
        "quality": "medium",
        "license": "Public Domain",
        "file_prefix": "john",
    },
    "bryce": {
        "display_name": "Bryce (US Male)",
        "gender": "male",
        "accent": "US",
        "quality": "medium",
        "license": "Public Domain",
        "file_prefix": "bryce",
    },
}


class PiperTTS:
    """
    Text-to-Speech using Piper TTS.

    Generates natural-sounding speech for copilot responses.
    Supports multiple voices (all Public Domain licensed).
    """

    def __init__(
        self,
        voice: str = "ljspeech",
        models_dir: Optional[Path] = None,
    ):
        self.voice = voice
        self.models_dir = models_dir or Path("models") / "piper"
        self._loaded = False
        self._piper = None

        # Validate voice
        if voice not in AVAILABLE_VOICES:
            logger.warning(f"Unknown voice '{voice}', using default 'ljspeech'")
            self.voice = "ljspeech"

    def load(self) -> bool:
        """Load the Piper TTS model."""
        try:
            # Get voice info
            voice_info = AVAILABLE_VOICES.get(self.voice)
            if not voice_info:
                logger.error(f"Unknown voice: {self.voice}")
                return False

            # Build model path
            voice_dir = self.models_dir / self.voice
            model_file = voice_info['file_prefix'] + ".onnx"
            model_path = voice_dir / model_file

            if not model_path.exists():
                logger.error(f"Model file not found: {model_path}")
                logger.error("Run 'python scripts/download_tts_voices.py' to download voices")
                return False

            logger.info(f"Loading Piper TTS voice: {voice_info['display_name']}")
            logger.info(f"Model path: {model_path}")

            # TODO: Implement actual Piper loading
            # from piper import PiperVoice
            # self._piper = PiperVoice.load(model_path)

            self._loaded = True
            logger.info(f"Piper TTS loaded: {voice_info['display_name']} ({voice_info['license']})")
            return True

        except Exception as e:
            logger.error(f"Failed to load Piper TTS: {e}")
            return False

    def synthesize(self, text: str) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to speak

        Returns:
            WAV audio data as bytes
        """
        if not self._loaded:
            raise RuntimeError("TTS not loaded. Call load() first.")

        try:
            # TODO: Implement actual Piper synthesis
            # audio_data = self._piper.synthesize(text)

            # For now, return empty placeholder
            logger.debug(f"Synthesizing: '{text}'")

            # Create a silent WAV as placeholder
            return self._create_silent_wav(duration=1.0)

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return b""

    def synthesize_to_file(self, text: str, output_path: Path) -> bool:
        """
        Synthesize speech and save to file.

        Args:
            text: Text to speak
            output_path: Path to save WAV file

        Returns:
            True if successful
        """
        try:
            audio_data = self.synthesize(text)
            if audio_data:
                output_path.write_bytes(audio_data)
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to save TTS audio: {e}")
            return False

    def _create_silent_wav(
        self,
        duration: float = 1.0,
        sample_rate: int = 22050,
    ) -> bytes:
        """Create a silent WAV file (placeholder)."""
        num_samples = int(sample_rate * duration)
        silent_data = b"\x00\x00" * num_samples

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(silent_data)

        return buffer.getvalue()

    def set_voice(self, voice: str) -> bool:
        """
        Change the active voice.

        Args:
            voice: Voice ID from AVAILABLE_VOICES

        Returns:
            True if voice changed successfully
        """
        if voice not in AVAILABLE_VOICES:
            logger.error(f"Unknown voice: {voice}")
            return False

        if voice == self.voice:
            return True  # Already using this voice

        self.voice = voice
        self._loaded = False  # Force reload
        return self.load()

    def get_voice_info(self) -> Dict:
        """Get current voice information."""
        return AVAILABLE_VOICES.get(self.voice, {})

    @staticmethod
    def get_available_voices() -> List[Dict]:
        """Get list of all available voices with metadata."""
        return [
            {
                "id": voice_id,
                **voice_info,
            }
            for voice_id, voice_info in AVAILABLE_VOICES.items()
        ]

    @property
    def is_loaded(self) -> bool:
        """Check if TTS is loaded."""
        return self._loaded


# Pre-defined responses for common commands
COPILOT_RESPONSES = {
    "gear_down": "Gear down",
    "gear_up": "Gear up",
    "flaps_10": "Flaps 10",
    "flaps_20": "Flaps 20",
    "flaps_full": "Flaps full",
    "flaps_up": "Flaps up",
    "parking_brake_on": "Parking brake set",
    "parking_brake_off": "Parking brake released",
    "lights_on": "Lights on",
    "lights_off": "Lights off",
    "speed_check": "Speed is {speed} knots",
    "altitude_check": "Altitude is {altitude} feet",
    "not_understood": "Say again please",
    "gear_unsafe": "Speed too high for gear extension",
}
