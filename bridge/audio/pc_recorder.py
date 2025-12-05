"""
PC Microphone Recorder
Records audio from system microphone using sounddevice
Supports both buffered recording and streaming mode for VAD
"""

import io
import wave
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, List, Callable


class PcRecorder:
    """Records audio from PC microphone with streaming support."""

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
        self.is_streaming = False
        self.audio_buffer: List[np.ndarray] = []
        self.stream: Optional[sd.InputStream] = None
        self.lock = threading.Lock()

        # Streaming mode callback
        self.stream_callback: Optional[Callable[[np.ndarray], None]] = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """Callback for audio stream (called by sounddevice)."""
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording or self.is_streaming:
            # Flatten to 1D array (mono)
            audio_chunk = indata[:, 0] if indata.ndim > 1 else indata

            if self.is_streaming and self.stream_callback:
                # Streaming mode: Send chunk to callback (VAD processor)
                try:
                    self.stream_callback(audio_chunk.copy())
                except Exception as e:
                    print(f"Stream callback error: {e}")

            if self.is_recording:
                # Buffer mode: Store chunk for later export
                with self.lock:
                    self.audio_buffer.append(audio_chunk.copy())

    def start_recording(self) -> bool:
        """
        Start recording from PC microphone (buffered mode).

        Returns:
            True if recording started successfully
        """
        if self.is_recording or self.is_streaming:
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
            print(f"[PC] Recording started: {self.sample_rate}Hz, {self.channels} channel(s)")
            return True

        except Exception as e:
            print(f"[PC] Failed to start recording: {e}")
            return False

    def start_streaming(self, chunk_callback: Callable[[np.ndarray], None]) -> bool:
        """
        Start streaming from PC microphone to callback (for VAD processing).

        Args:
            chunk_callback: Function to call with each audio chunk (float32 array)

        Returns:
            True if streaming started successfully
        """
        if self.is_recording or self.is_streaming:
            return False

        self.stream_callback = chunk_callback

        try:
            # Create input stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                callback=self._audio_callback,
            )
            self.stream.start()
            self.is_streaming = True
            print(f"[PC] Streaming started: {self.sample_rate}Hz, {self.channels} channel(s)")
            return True

        except Exception as e:
            print(f"[PC] Failed to start streaming: {e}")
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
                print("[PC] No audio data recorded")
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
        print(f"[PC] Recording stopped: {len(wav_bytes)} bytes, {len(audio_data)/self.sample_rate:.2f}s")
        return wav_bytes

    def stop_streaming(self):
        """Stop streaming mode."""
        if not self.is_streaming:
            return

        self.is_streaming = False
        self.stream_callback = None

        # Stop stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        print("[PC] Streaming stopped")

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

            print("[PC] Recording cancelled")

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
