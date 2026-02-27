import os
import json
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    NONE = "none"


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.settings_file = os.path.expanduser("~/.cse_trade_settings.json")
        self._settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        default_settings = {
            "provider": "none",
            "api_key": "",
            "model": "",
            "temperature": 0.7,
            "max_tokens": 2000,
            "refresh_interval": 60,
        }

        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
            except Exception as e:
                logger.error(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self, settings: Dict[str, Any]):
        self._settings.update(settings)
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self._settings, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        self._settings[key] = value
        self.save_settings(self._settings)

    @property
    def provider(self) -> str:
        return self._settings.get("provider", "none")

    @property
    def api_key(self) -> str:
        return self._settings.get("api_key", "")

    @property
    def model(self) -> str:
        return self._settings.get("model", "")

    @property
    def temperature(self) -> float:
        return self._settings.get("temperature", 0.7)

    @property
    def max_tokens(self) -> int:
        return self._settings.get("max_tokens", 2000)

    @property
    def refresh_interval(self) -> int:
        return self._settings.get("refresh_interval", 60)


class LLMProviderFactory:
    PROVIDER_MODELS = {
        "openai": ["gpt-5.2", "gpt-5-mini", "gpt-5-nano"],
        "anthropic": [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
        ],
        "gemini": [
            "gemini-3.1-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
        "ollama": [],
    }

    @staticmethod
    def get_available_providers() -> list:
        return [
            {"id": "none", "name": "No API (Offline Mode)", "requires_key": False},
            {"id": "openai", "name": "OpenAI", "requires_key": True},
            {"id": "anthropic", "name": "Anthropic (Claude)", "requires_key": True},
            {"id": "gemini", "name": "Google Gemini", "requires_key": True},
            {"id": "ollama", "name": "Ollama (Local)", "requires_key": False},
        ]

    @staticmethod
    def get_models_for_provider(provider: str) -> list:
        return LLMProviderFactory.PROVIDER_MODELS.get(provider, [])

    @staticmethod
    def create_llm(
        provider: str,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        if not api_key and provider not in ["ollama", "none"]:
            logger.warning(f"No API key provided for {provider}")
            return None

        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI

                return ChatOpenAI(
                    model=model or "gpt-4o-mini",
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            elif provider == "anthropic":
                from langchain_anthropic import ChatAnthropic

                return ChatAnthropic(
                    model=model or "claude-3-5-sonnet-20241022",
                    anthropic_api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            elif provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI

                model_name = model if model else "gemini-1.5-flash"
                logger.info(f"Creating Gemini LLM with model: {model_name}")

                return ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )

            elif provider == "ollama":
                from langchain_ollama import ChatOllama

                return ChatOllama(
                    model=model or "llama3.1",
                    temperature=temperature,
                    num_predict=max_tokens,
                )

            else:
                return None

        except ImportError as e:
            logger.error(f"Missing dependency for {provider}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating {provider} LLM: {e}")
            return None

    @staticmethod
    def test_connection(
        provider: str, api_key: str = None, model: str = None
    ) -> tuple[bool, str]:
        try:
            llm = LLMProviderFactory.create_llm(provider, api_key, model)
            if llm is None:
                return False, "Failed to create LLM instance"

            response = llm.invoke("Say 'OK' if you receive this message.")
            return True, "Connection successful!"
        except Exception as e:
            return False, str(e)


def get_settings() -> SettingsManager:
    return SettingsManager()
