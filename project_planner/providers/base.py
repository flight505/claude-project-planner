"""
Base provider interface for AI API integrations.

This module defines the abstract base class for all AI API providers,
enabling flexible provider switching and fallback chains.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAPIProvider(ABC):
    """Abstract base class for AI API providers."""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the provider with API credentials.

        Args:
            api_key: API key for authentication
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from a prompt.

        Args:
            prompt: Input prompt text
            model: Model identifier (provider-specific)
            **kwargs: Additional generation parameters

        Returns:
            Generated text response

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def deep_research(
        self,
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive deep research on a topic.

        Args:
            query: Research query or question
            **kwargs: Additional research parameters

        Returns:
            Dictionary containing:
                - report: str - Full research report
                - citations: List[Dict] - Source citations
                - metadata: Dict - Research metadata

        Raises:
            ProviderError: If research fails
            NotImplementedError: If provider doesn't support deep research
        """
        pass

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: int = 8,
        **kwargs
    ) -> bytes:
        """
        Generate video from text prompt.

        Args:
            prompt: Video description
            duration: Duration in seconds (typically 4-8)
            **kwargs: Additional video generation parameters

        Returns:
            Video file as bytes (typically MP4)

        Raises:
            ProviderError: If generation fails
            NotImplementedError: If provider doesn't support video generation
        """
        pass

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> bytes:
        """
        Generate image from text prompt.

        Args:
            prompt: Image description
            **kwargs: Additional image generation parameters

        Returns:
            Image file as bytes

        Raises:
            ProviderError: If generation fails
            NotImplementedError: If provider doesn't support image generation
        """
        pass

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """
        Check if provider supports a specific feature.

        Args:
            feature: Feature name (e.g., "deep_research", "video_generation")

        Returns:
            True if feature is supported, False otherwise
        """
        pass

    def get_capabilities(self) -> Dict[str, bool]:
        """
        Get all capabilities of this provider.

        Returns:
            Dictionary mapping feature names to support status
        """
        return {
            "text_generation": self.supports_feature("text_generation"),
            "deep_research": self.supports_feature("deep_research"),
            "video_generation": self.supports_feature("video_generation"),
            "image_generation": self.supports_feature("image_generation"),
            "1m_token_context": self.supports_feature("1m_token_context"),
        }

    def __repr__(self) -> str:
        """String representation of provider."""
        return f"{self.__class__.__name__}(capabilities={list(self.get_capabilities().keys())})"


class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available or not configured."""
    pass


class FeatureNotSupportedError(ProviderError):
    """Raised when a requested feature is not supported by the provider."""
    pass


class ProviderAuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    pass


class ProviderTimeoutError(ProviderError):
    """Raised when a provider operation times out."""
    pass
