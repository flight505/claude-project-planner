"""
Provider router with automatic fallback logic.

This module implements intelligent routing of AI requests to available providers,
with automatic fallback chains when providers are unavailable or lack specific features.
"""

import os
from typing import Any, Dict, Optional

from .base import (
    BaseAPIProvider,
    ProviderError,
    ProviderNotAvailableError,
)
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider


class ProviderRouter:
    """
    Routes AI requests to appropriate providers with fallback support.

    The router automatically detects available API keys and initializes
    corresponding providers. It then routes requests based on:
    1. Feature availability
    2. Provider capability
    3. Cost optimization
    4. Fallback chains
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider router.

        Args:
            config: Optional configuration dictionary with keys:
                - prefer_gemini: bool - Prefer Gemini when available (default: True)
                - openrouter_app_name: str - App name for OpenRouter
                - gemini_text_model: str - Override Gemini text model
                - openrouter_text_model: str - Override OpenRouter text model
        """
        self.config = config or {}
        self.providers: Dict[str, BaseAPIProvider] = {}
        self._load_providers()

    def _load_providers(self) -> None:
        """
        Load all available providers based on environment variables.

        Checks for API keys in this order:
        1. GEMINI_API_KEY or GOOGLE_API_KEY
        2. OPENROUTER_API_KEY
        """
        # Try loading Gemini provider
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                gemini_config = {}
                if "gemini_text_model" in self.config:
                    gemini_config["text_model"] = self.config["gemini_text_model"]

                self.providers["gemini"] = GeminiProvider(gemini_key, **gemini_config)
            except Exception as e:
                # Log warning but don't fail
                print(f"Warning: Failed to initialize Gemini provider: {e}")

        # Try loading OpenRouter provider
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                openrouter_config = {}
                if "openrouter_app_name" in self.config:
                    openrouter_config["app_name"] = self.config["openrouter_app_name"]
                if "openrouter_text_model" in self.config:
                    openrouter_config["text_model"] = self.config["openrouter_text_model"]

                self.providers["openrouter"] = OpenRouterProvider(
                    openrouter_key,
                    **openrouter_config
                )
            except Exception as e:
                print(f"Warning: Failed to initialize OpenRouter provider: {e}")

    def get_provider_for_task(self, task_type: str, **kwargs) -> BaseAPIProvider:
        """
        Select the best provider for a given task type.

        Args:
            task_type: Type of task ("text", "research", "video", "image")
            **kwargs: Additional routing hints
                - prefer_provider: str - Force specific provider

        Returns:
            Provider instance

        Raises:
            ProviderNotAvailableError: If no suitable provider found
        """
        # Check for forced provider
        if "prefer_provider" in kwargs:
            provider_name = kwargs["prefer_provider"]
            if provider_name in self.providers:
                return self.providers[provider_name]
            else:
                raise ProviderNotAvailableError(
                    f"Requested provider '{provider_name}' not available"
                )

        # Route based on task type
        if task_type == "text":
            return self._get_text_provider()

        elif task_type == "research" or task_type == "deep_research":
            return self._get_research_provider()

        elif task_type == "video":
            return self._get_video_provider()

        elif task_type == "image":
            return self._get_image_provider()

        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _get_text_provider(self) -> BaseAPIProvider:
        """Get provider for text generation."""
        # Prefer Gemini if available (better quality)
        if self.config.get("prefer_gemini", True) and "gemini" in self.providers:
            return self.providers["gemini"]

        # Fallback to OpenRouter
        if "openrouter" in self.providers:
            return self.providers["openrouter"]

        raise ProviderNotAvailableError(
            "No text generation provider available. "
            "Set GEMINI_API_KEY or OPENROUTER_API_KEY."
        )

    def _get_research_provider(self) -> BaseAPIProvider:
        """Get provider for research tasks."""
        # Prefer Gemini Deep Research if available (more comprehensive)
        if "gemini" in self.providers:
            return self.providers["gemini"]

        # Fallback to Perplexity via OpenRouter
        if "openrouter" in self.providers:
            return self.providers["openrouter"]

        raise ProviderNotAvailableError(
            "No research provider available. "
            "Set GEMINI_API_KEY (for Deep Research) or OPENROUTER_API_KEY (for Perplexity)."
        )

    def _get_video_provider(self) -> BaseAPIProvider:
        """Get provider for video generation."""
        # Only Gemini supports video (Veo 3.1)
        if "gemini" in self.providers:
            return self.providers["gemini"]

        raise ProviderNotAvailableError(
            "Video generation requires Gemini with Veo 3.1. "
            "Set GEMINI_API_KEY and ensure you have Google AI Pro subscription."
        )

    def _get_image_provider(self) -> BaseAPIProvider:
        """Get provider for image generation."""
        # Prefer OpenRouter (more models, lower cost)
        if "openrouter" in self.providers:
            return self.providers["openrouter"]

        # Fallback to Gemini Imagen
        if "gemini" in self.providers:
            return self.providers["gemini"]

        raise ProviderNotAvailableError(
            "No image generation provider available. "
            "Set OPENROUTER_API_KEY or GEMINI_API_KEY."
        )

    def get_available_providers(self) -> Dict[str, Dict[str, bool]]:
        """
        Get all available providers and their capabilities.

        Returns:
            Dictionary mapping provider names to capabilities
        """
        return {
            name: provider.get_capabilities()
            for name, provider in self.providers.items()
        }

    def has_feature(self, feature: str) -> bool:
        """
        Check if ANY available provider supports a feature.

        Args:
            feature: Feature name

        Returns:
            True if at least one provider supports the feature
        """
        return any(
            provider.supports_feature(feature)
            for provider in self.providers.values()
        )

    def __repr__(self) -> str:
        """String representation of router."""
        provider_names = list(self.providers.keys())
        return f"ProviderRouter(providers={provider_names})"
