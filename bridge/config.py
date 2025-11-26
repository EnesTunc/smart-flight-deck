"""
Smart Flight Deck Companion - Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # Paths
    models_dir: Path = Field(
        default=Path("models"), description="Directory for AI models"
    )
    logs_dir: Path = Field(default=Path("logs"), description="Directory for logs")

    # Whisper STT
    whisper_model: str = Field(
        default="base.en",
        description="Whisper model size: tiny.en, base.en, small.en",
    )
    whisper_device: str = Field(
        default="cpu", description="Device for Whisper: cpu, cuda"
    )

    # Piper TTS
    piper_voice: str = Field(
        default="ljspeech",
        description="Piper TTS voice: ljspeech, cori-high, john, bryce (all Public Domain)"
    )
    tts_enabled: bool = Field(
        default=True, description="Enable text-to-speech responses"
    )

    # License
    license_server_url: str = Field(
        default="https://license.smartflightdeck.com/api/v1",
        description="License server URL",
    )
    offline_grace_days: int = Field(
        default=7, description="Days allowed offline before warning"
    )

    # Security
    session_token_expiry: int = Field(
        default=600, description="QR session token expiry in seconds"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "SFDC_"


# Global settings instance
settings = Settings()


def get_local_ip() -> str:
    """Get the local IP address for LAN communication."""
    import socket

    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
