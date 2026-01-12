"""
OpenRouter API provider implementation.

This module provides integration with OpenRouter, enabling access to:
- Perplexity for research (via perplexity/llama-3.1-sonar-large-128k-online)
- Various LLMs for text generation
- Image generation models (Flux, DALL-E, etc.)

OpenRouter acts as a unified API gateway to multiple AI providers.
"""

import asyncio
from typing import Any, Dict, Optional

from .base import (
    BaseAPIProvider,
    FeatureNotSupportedError,
    ProviderError,
)


class OpenRouterProvider(BaseAPIProvider):
    """OpenRouter API provider implementation."""

    # Default models
    DEFAULT_TEXT_MODEL = "anthropic/claude-3.5-sonnet"
    DEFAULT_RESEARCH_MODEL = "perplexity/llama-3.1-sonar-large-128k-online"
    DEFAULT_IMAGE_MODEL = "black-forest-labs/flux-1.1-pro"

    # OpenRouter API endpoint
    API_BASE = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            **kwargs: Additional configuration
                - text_model: Override default text model
                - research_model: Override default research model
                - image_model: Override default image model
                - app_name: Application name for OpenRouter attribution
        """
        super().__init__(api_key, **kwargs)

        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=api_key,
                base_url=self.API_BASE
            )
        except ImportError as e:
            raise ProviderError(
                "openai package not installed. "
                "Install with: pip install openai"
            ) from e

        # Model configuration
        self.text_model = kwargs.get("text_model", self.DEFAULT_TEXT_MODEL)
        self.research_model = kwargs.get("research_model", self.DEFAULT_RESEARCH_MODEL)
        self.image_model = kwargs.get("image_model", self.DEFAULT_IMAGE_MODEL)
        self.app_name = kwargs.get("app_name", "claude-project-planner")

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenRouter models.

        Args:
            prompt: Input prompt
            model: Model override (defaults to claude-3.5-sonnet)
            **kwargs: Additional generation parameters
                - temperature: float (0.0-2.0)
                - max_tokens: int
                - system: str - System message

        Returns:
            Generated text

        Raises:
            ProviderError: If generation fails
        """
        try:
            model_name = model or self.text_model

            # Prepare messages
            messages = []
            if "system" in kwargs:
                messages.append({"role": "system", "content": kwargs.pop("system")})
            messages.append({"role": "user", "content": prompt})

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    extra_headers={
                        "X-Title": self.app_name,
                    },
                    **kwargs
                )
            )

            return response.choices[0].message.content

        except Exception as e:
            raise ProviderError(f"Text generation failed: {e}") from e

    async def deep_research(
        self,
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Conduct research using Perplexity via OpenRouter.

        This is a simpler alternative to Gemini Deep Research.
        Uses Perplexity's online model for web-grounded responses.

        Args:
            query: Research question
            **kwargs: Additional parameters
                - max_tokens: int (default: 4000)

        Returns:
            Dictionary containing:
                - report: Research response
                - citations: Empty list (Perplexity citations not extracted)
                - metadata: Request metadata

        Raises:
            ProviderError: If research fails
        """
        try:
            max_tokens = kwargs.get("max_tokens", 4000)

            messages = [
                {
                    "role": "system",
                    "content": "You are a research assistant. Provide comprehensive, "
                              "well-researched responses with citations where possible."
                },
                {"role": "user", "content": query}
            ]

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.research_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    extra_headers={
                        "X-Title": self.app_name,
                    }
                )
            )

            report_text = response.choices[0].message.content

            return {
                "report": report_text,
                "citations": [],  # Perplexity citations not easily extractable
                "metadata": {
                    "model": self.research_model,
                    "tokens_used": response.usage.total_tokens if response.usage else None,
                }
            }

        except Exception as e:
            raise ProviderError(f"Research failed: {e}") from e

    async def generate_video(
        self,
        prompt: str,
        duration: int = 8,
        **kwargs
    ) -> bytes:
        """
        Video generation not supported via OpenRouter.

        Raises:
            FeatureNotSupportedError: Always raises this error
        """
        raise FeatureNotSupportedError(
            "Video generation not supported by OpenRouter. "
            "Use GeminiProvider with Veo 3.1 instead."
        )

    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> bytes:
        """
        Generate image using models available on OpenRouter.

        Args:
            prompt: Image description
            **kwargs: Additional parameters
                - model: Override image model
                - size: Image size (e.g., "1024x1024")
                - quality: "standard" or "hd"

        Returns:
            Image file as bytes

        Raises:
            ProviderError: If generation fails
        """
        try:
            model = kwargs.get("model", self.image_model)
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "standard")

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality,
                    extra_headers={
                        "X-Title": self.app_name,
                    }
                )
            )

            # Download image from URL
            import requests
            image_url = response.data[0].url
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()

            return image_response.content

        except Exception as e:
            raise ProviderError(f"Image generation failed: {e}") from e

    def supports_feature(self, feature: str) -> bool:
        """
        Check if OpenRouter provider supports a feature.

        Args:
            feature: Feature name

        Returns:
            True if supported, False otherwise
        """
        supported_features = {
            "text_generation",
            "deep_research",  # Via Perplexity
            "image_generation",
        }

        return feature in supported_features
