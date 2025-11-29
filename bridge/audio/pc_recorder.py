"""
PC Microphone Recorder
Records audio from system microphone using sounddevice
"""

import io
import wave
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, List


class PcRecorder:
    """Records audio from PC microphone."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize PC recorder.

        Args:
            sample_rate: Sample rate in Hz (16kHz for Whisper)
            channels: Number of channels (1 = mono, 2 = stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_buffer: List[np.ndarray] = []
        self.stream: Optional[sd.InputStream] = None
        self.lock = threading.Lock()

    def _audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """Callback for audio stream (called by sounddevice)."""
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording:
            with self.lock:
                # Copy audio data to buffer
                self.audio_buffer.append(indata.copy())

    def start_recording(self) -> bool:
        """
        Start recording from PC microphone.

        Returns:
            True if recording started successfully
        """
        if self.is_recording:
            return False

        with self.lock:
            self.audio_buffer = []

        try:
            # Create input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                callback=self._audio_callback,
            )
            self.stream.start()
            self.is_recording = True
            print(f"PC recording started: {self.sample_rate}Hz, {self.channels} channel(s)")
            return True

        except Exception as e:
            print(f"Failed to start PC recording: {e}")
            return False

    def stop_recording(self) -> Optional[bytes]:
        """
        Stop recording and get WAV audio data.

        Returns:
            WAV file bytes, or None if failed
        """
        if not self.is_recording:
            return None

        self.is_recording = False

        # Stop stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        with self.lock:
            if not self.audio_buffer:
                print("No audio data recorded")
                return None

            # Concatenate all audio chunks
            audio_data = np.concatenate(self.audio_buffer, axis=0)

        # Convert float32 to int16 for WAV
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 2 bytes for int16
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        wav_bytes = wav_buffer.getvalue()
        print(f"PC recording stopped: {len(wav_bytes)} bytes, {len(audio_data)/self.sample_rate:.2f}s")
        return wav_bytes

    def cancel_recording(self):
        """Cancel recording without returning data."""
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            with self.lock:
                self.audio_buffer = []

            print("PC recording cancelled")

    def get_available_devices(self) -> list:
        """Get list of available input devices."""
        devices = sd.query_devices()
        input_devices = []

        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels'],
                    'sample_rate': dev['default_samplerate'],
                })

        return input_devices

    def set_device(self, device_index: Optional[int] = None):
        """Set input device by index (None = default)."""
        sd.default.device = (device_index, None)
        print(f"Audio input device set to: {device_index if device_index is not None else 'default'}")
