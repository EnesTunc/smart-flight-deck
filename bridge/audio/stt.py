"""
Smart Flight Deck Companion - Speech-to-Text
Whisper integration for voice recognition.
"""

import logging
import math
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class WhisperSTT:
    """
    Speech-to-Text using faster-whisper.

    Supports models: tiny.en, base.en, small.en
    """

    def __init__(
        self,
        model_size: str = "small.en",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._loaded = False

    def load(self) -> bool:
        """Load the Whisper model."""
        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            self._loaded = True
            logger.info("Whisper model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False

    def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
    ) -> Tuple[str, float]:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (WAV format)
            language: Language code

        Returns:
            Tuple of (transcribed_text, confidence)
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=False,  # Disable Whisper VAD - we use Silero VAD
            )

            # Combine all segments
            text_parts = []
            total_logprob = 0.0
            segment_count = 0

            for segment in segments:
                text_parts.append(segment.text)
                total_logprob += segment.avg_logprob
                segment_count += 1

            full_text = " ".join(text_parts).strip()
            avg_logprob = (
                total_logprob / segment_count if segment_count > 0 else -3.0
            )

            # Convert log probability to confidence (0-1)
            # Whisper avg_logprob range: -0.1 (excellent) to -3.0 (poor)
            # Using exponential scaling for better distribution:
            # -0.1 → ~0.90, -0.5 → ~0.60, -1.0 → ~0.37, -2.0 → ~0.13
            confidence = math.exp(avg_logprob)

            # Clamp to [0, 1] range
            confidence = min(1.0, max(0.0, confidence))

            logger.info(f"STT: '{full_text}' | logprob={avg_logprob:.3f} | confidence={confidence:.2f} | segments={segment_count}")
            return full_text, confidence

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "", 0.0

    def transcribe_bytes(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
    ) -> Tuple[str, float]:
        """
        Transcribe audio from bytes.

        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate

        Returns:
            Tuple of (transcribed_text, confidence)
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            import numpy as np

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio_array /= 32768.0  # Normalize to [-1, 1]

            segments, info = self.model.transcribe(
                audio_array,
                beam_size=5,
                vad_filter=True,
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)

            full_text = " ".join(text_parts).strip()
            return full_text, 0.9  # Simplified confidence

        except Exception as e:
            logger.error(f"Transcription from bytes failed: {e}")
            return "", 0.0

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded
