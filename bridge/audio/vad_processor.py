"""
Voice Activity Detection (VAD) Processor
Detects speech in audio stream using Silero VAD
"""

import io
import wave
import numpy as np
import torch
from collections import deque
from typing import Optional, List, Tuple


class VadProcessor:
    """
    Processes audio stream with VAD to detect speech segments.
    Uses Silero VAD for robust speech detection.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 500,
        padding_duration_ms: int = 300,
    ):
        """
        Initialize VAD processor.

        Args:
            sample_rate: Audio sample rate (16kHz for Whisper)
            threshold: VAD confidence threshold (0.0-1.0)
            min_speech_duration_ms: Minimum speech duration to trigger
            min_silence_duration_ms: Silence duration to end speech segment
            padding_duration_ms: Padding before/after speech
        """
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_speech_samples = int(sample_rate * min_speech_duration_ms / 1000)
        self.min_silence_samples = int(sample_rate * min_silence_duration_ms / 1000)
        self.padding_samples = int(sample_rate * padding_duration_ms / 1000)

        # Load Silero VAD model
        try:
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            print(f"✓ Silero VAD loaded (threshold={threshold})")
        except Exception as e:
            print(f"⚠ Failed to load Silero VAD: {e}")
            print("  Using simple energy-based VAD as fallback")
            self.model = None

        # State
        self.reset()

    def reset(self):
        """Reset VAD state."""
        self.is_speech = False
        self.speech_buffer = []
        self.temp_buffer = deque(maxlen=self.padding_samples)
        self.silence_counter = 0
        self.speech_counter = 0

    def process_chunk(self, audio_chunk: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Process audio chunk with VAD.

        Args:
            audio_chunk: Audio samples (float32, -1.0 to 1.0)

        Returns:
            (has_speech_ended, speech_segment)
            - has_speech_ended: True if a complete speech segment is ready
            - speech_segment: Complete speech audio if ended, else None
        """
        if self.model is not None:
            # Use Silero VAD
            speech_prob = self._silero_vad(audio_chunk)
        else:
            # Fallback to energy-based VAD
            speech_prob = self._energy_vad(audio_chunk)

        is_speech_detected = speech_prob > self.threshold

        if is_speech_detected:
            self.silence_counter = 0
            self.speech_counter += len(audio_chunk)

            # Add to temporary buffer (for padding)
            self.temp_buffer.extend(audio_chunk)

            if not self.is_speech and self.speech_counter >= self.min_speech_samples:
                # Speech started
                self.is_speech = True
                # Add padding from temp buffer
                self.speech_buffer.extend(self.temp_buffer)
                print(f"🎤 Speech started (prob={speech_prob:.2f})")
            elif self.is_speech:
                # Continue speech
                self.speech_buffer.extend(audio_chunk)

        else:
            # Silence detected
            self.silence_counter += len(audio_chunk)
            self.temp_buffer.extend(audio_chunk)

            if self.is_speech:
                # Add silence to buffer (for natural endings)
                self.speech_buffer.extend(audio_chunk)

                if self.silence_counter >= self.min_silence_samples:
                    # Speech ended
                    print(f"🔇 Speech ended ({len(self.speech_buffer)/self.sample_rate:.2f}s)")
                    speech_segment = np.array(self.speech_buffer, dtype=np.float32)
                    self.reset()
                    return True, speech_segment

            else:
                # Still waiting for speech
                self.speech_counter = 0

        return False, None

    def _silero_vad(self, audio_chunk: np.ndarray) -> float:
        """Run Silero VAD on audio chunk."""
        # Silero expects torch tensor
        audio_tensor = torch.from_numpy(audio_chunk).float()

        with torch.no_grad():
            speech_prob = self.model(audio_tensor, self.sample_rate).item()

        return speech_prob

    def _energy_vad(self, audio_chunk: np.ndarray) -> float:
        """Simple energy-based VAD (fallback)."""
        energy = np.sqrt(np.mean(audio_chunk ** 2))
        # Normalize to 0-1 range
        # Threshold ~0.01 for 16-bit audio normalized to -1/+1
        speech_prob = min(energy / 0.05, 1.0)
        return speech_prob

    def get_current_duration(self) -> float:
        """Get current speech buffer duration in seconds."""
        if not self.speech_buffer:
            return 0.0
        return len(self.speech_buffer) / self.sample_rate

    def export_wav(self, audio_data: np.ndarray) -> bytes:
        """
        Export audio segment as WAV bytes.

        Args:
            audio_data: Float32 audio (-1.0 to 1.0)

        Returns:
            WAV file bytes
        """
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Create WAV in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (int16)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return wav_buffer.getvalue()


# Singleton instance for session management
_vad_sessions = {}


def get_vad_processor(session_id: str) -> VadProcessor:
    """Get or create VAD processor for session."""
    if session_id not in _vad_sessions:
        _vad_sessions[session_id] = VadProcessor(
            sample_rate=16000,
            threshold=0.5,
            min_speech_duration_ms=250,
            min_silence_duration_ms=500,
            padding_duration_ms=300,
        )
    return _vad_sessions[session_id]


def remove_vad_session(session_id: str):
    """Remove VAD processor for session."""
    if session_id in _vad_sessions:
        del _vad_sessions[session_id]
        print(f"VAD session removed: {session_id}")
