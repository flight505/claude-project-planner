"""
AI API provider abstraction layer for claude-project-planner.

This package provides a unified interface for working with multiple AI providers:
- Google Gemini (Deep Research, Veo 3.1, Imagen 3)
- OpenRouter (Perplexity, various LLMs, image models)

Usage:
    from project_planner.providers import ProviderRouter

    # Auto-detect and initialize providers
    router = ProviderRouter()

    # Get appropriate provider for task
    provider = router.get_provider_for_task("research")

    # Use provider
    result = await provider.deep_research("What is quantum computing?")
"""

from .base import (
    BaseAPIProvider,
    FeatureNotSupportedError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderNotAvailableError,
    ProviderTimeoutError,
)
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider
from .router import ProviderRouter

__all__ = [
    # Base classes and exceptions
    "BaseAPIProvider",
    "ProviderError",
    "ProviderNotAvailableError",
    "FeatureNotSupportedError",
    "ProviderAuthenticationError",
    "ProviderTimeoutError",
    # Provider implementations
    "GeminiProvider",
    "OpenRouterProvider",
    # Router
    "ProviderRouter",
]
