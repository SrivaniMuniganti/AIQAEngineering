"""Route LLM requests to Ollama or Groq with automatic fallback."""

import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from groq import Groq
from openai import OpenAI

from utils.config import Settings


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class LLMUnavailableError(LLMError):
    """Raised when no LLM provider is available."""
    pass


@dataclass
class LLMResult:
    """Result from LLM generation."""
    text: str
    provider: str  # "Ollama" or "Groq"


class LLMRouter:
    """Route requests to Ollama (local) with Groq (cloud) fallback."""

    def __init__(self, settings: Settings):
        """Initialize the router with settings.

        Args:
            settings: Settings object with LLM configuration
        """
        self.settings = settings

    def generate(self, messages: List[dict]) -> LLMResult:
        """Generate response, trying Ollama first, then Groq.

        Args:
            messages: List of messages in OpenAI format

        Returns:
            LLMResult with text and provider name

        Raises:
            LLMUnavailableError: If both providers fail or are unavailable
        """
        ollama_error = None
        groq_error = None

        # Try Ollama first
        if self.settings.has_ollama_config():
            try:
                response = self._call_ollama(messages)
                if response and response.strip():
                    return LLMResult(text=response, provider="Ollama")
            except LLMError as e:
                ollama_error = str(e)

        # Fall back to Groq
        if self.settings.has_groq_config():
            try:
                response = self._call_groq(messages)
                if response and response.strip():
                    return LLMResult(text=response, provider="Groq")
            except LLMError as e:
                groq_error = str(e)

        # Both failed or unavailable
        error_msg = "No LLM provider available"
        if ollama_error:
            error_msg += f"\nOllama: {ollama_error}"
        if groq_error:
            error_msg += f"\nGroq: {groq_error}"

        raise LLMUnavailableError(error_msg)

    def _call_ollama(self, messages: List[dict]) -> str:
        """Call Ollama API.

        Args:
            messages: List of messages

        Returns:
            Response text

        Raises:
            LLMError: If request fails
        """
        if not self.settings.ollama_base_url or not self.settings.ollama_model:
            raise LLMError("Ollama not configured")

        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"

        try:
            response = requests.post(
                url,
                json={
                    "model": self.settings.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "format": "json",
                },
                timeout=self.settings.ollama_timeout,
            )

            if response.status_code != 200:
                raise LLMError(
                    f"Ollama returned status {response.status_code}"
                )

            data = response.json()
            text = data.get("message", {}).get("content", "").strip()

            if not text:
                raise LLMError("Ollama returned empty response")

            return text

        except requests.exceptions.Timeout:
            raise LLMError(f"Ollama timeout after {self.settings.ollama_timeout}s")
        except requests.exceptions.ConnectionError:
            raise LLMError("Cannot connect to Ollama")
        except Exception as e:
            raise LLMError(f"Ollama error: {str(e)}")

    def _call_groq(self, messages: List[dict]) -> str:
        """Call Groq API via OpenAI SDK.

        Args:
            messages: List of messages

        Returns:
            Response text

        Raises:
            LLMError: If request fails
        """
        if not self.settings.groq_api_key:
            raise LLMError("Groq API key not configured")

        try:
            client = Groq(api_key=self.settings.groq_api_key)

            response = client.chat.completions.create(
                model=self.settings.groq_model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )

            text = response.choices[0].message.content.strip()

            if not text:
                raise LLMError("Groq returned empty response")

            return text

        except Exception as e:
            raise LLMError(f"Groq error: {str(e)}")

    def test_ollama(self) -> tuple[bool, str]:
        """Test Ollama connection.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.settings.ollama_base_url or not self.settings.ollama_model:
            return False, "Ollama not configured"

        try:
            url = f"{self.settings.ollama_base_url.rstrip('/')}/api/tags"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return False, f"Ollama returned status {response.status_code}"

            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]

            if self.settings.ollama_model not in models:
                available = ", ".join(models) if models else "no models"
                return False, f"Model {self.settings.ollama_model} not found. Available: {available}"

            return True, f"Connected to Ollama ({self.settings.ollama_model})"

        except requests.exceptions.Timeout:
            return False, "Ollama connection timed out"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama"
        except Exception as e:
            return False, f"Ollama error: {str(e)}"

    def test_groq(self) -> tuple[bool, str]:
        """Test Groq connection.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.settings.groq_api_key:
            return False, "Groq API key not configured"

        try:
            client = Groq(api_key=self.settings.groq_api_key)

            # Try a simple completion to test the API key
            response = client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
            )

            return True, "Connected to Groq"

        except Exception as e:
            return False, f"Groq error: {str(e)}"
