"""Configuration management for Jira and LLM settings."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, set_key


@dataclass
class Settings:
    """Settings container for Jira and LLM endpoints."""

    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:12b"
    ollama_timeout: int = 60

    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            jira_url=os.getenv("JIRA_URL"),
            jira_email=os.getenv("JIRA_EMAIL"),
            jira_api_token=os.getenv("JIRA_API_TOKEN"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "gemma3:12b"),
            ollama_timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )

    def has_jira_config(self) -> bool:
        """Check if Jira is configured."""
        return bool(self.jira_url and self.jira_email and self.jira_api_token)

    def has_ollama_config(self) -> bool:
        """Check if Ollama is configured."""
        return bool(self.ollama_base_url and self.ollama_model)

    def has_groq_config(self) -> bool:
        """Check if Groq is configured."""
        return bool(self.groq_api_key)


def load_settings() -> Settings:
    """Load settings from .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    load_dotenv(env_file, override=True)
    return Settings.from_env()


def save_settings(settings: Settings) -> None:
    """Save settings to .env file."""
    env_file = Path(__file__).parent.parent / ".env"

    # Ensure .env exists
    env_file.touch(exist_ok=True)

    # Write each setting
    settings_map = {
        "JIRA_URL": settings.jira_url or "",
        "JIRA_EMAIL": settings.jira_email or "",
        "JIRA_API_TOKEN": settings.jira_api_token or "",
        "OLLAMA_BASE_URL": settings.ollama_base_url,
        "OLLAMA_MODEL": settings.ollama_model,
        "OLLAMA_TIMEOUT": str(settings.ollama_timeout),
        "GROQ_API_KEY": settings.groq_api_key or "",
        "GROQ_MODEL": settings.groq_model,
    }

    for key, value in settings_map.items():
        set_key(str(env_file), key, value)
        os.environ[key] = value


def mask_secret(secret: Optional[str], visible_chars: int = 4) -> str:
    """Mask a secret for display, showing only the last N characters."""
    if not secret:
        return "(not set)"
    if len(secret) <= visible_chars:
        return "●" * len(secret)
    return "●" * (len(secret) - visible_chars) + secret[-visible_chars:]
