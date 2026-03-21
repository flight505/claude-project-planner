"""
OpenRouter API provider implementation.

This module provides integration with OpenRouter, enabling access to:
- Perplexity Sonar Pro for research (via perplexity/sonar-pro)
- Various LLMs for text generation
- Image generation models (via chat completions with modalities)

OpenRouter acts as a unified API gateway to multiple AI providers.
"""

import asyncio
import base64
from typing import Any, Dict, Optional

from .base import (
    BaseAPIProvider,
    FeatureNotSupportedError,
    ProviderError,
)


class OpenRouterProvider(BaseAPIProvider):
    """OpenRouter API provider implementation."""

    # Default models
    DEFAULT_TEXT_MODEL = "anthropic/claude-sonnet-4-5"
    DEFAULT_RESEARCH_MODEL = "perplexity/sonar-pro"
    DEFAULT_IMAGE_MODEL = "google/gemini-2.5-flash-image"

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
            model: Model override (defaults to claude-sonnet-4-5)
            **kwargs: Additional generation parameters
                - temperature: float (0.0-2.0)
                - max_completion_tokens: int
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
                - max_completion_tokens: int (default: 4000)

        Returns:
            Dictionary containing:
                - report: Research response
                - citations: Empty list (Perplexity citations not extracted)
                - metadata: Request metadata

        Raises:
            ProviderError: If research fails
        """
        try:
            max_tokens = kwargs.get("max_completion_tokens", kwargs.get("max_tokens", 4000))

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
                    max_completion_tokens=max_tokens,
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

        Uses the chat completions API with modalities parameter, as
        OpenRouter no longer supports a separate /images/generations endpoint.

        Args:
            prompt: Image description
            **kwargs: Additional parameters
                - model: Override image model
                - aspect_ratio: Aspect ratio (e.g., "16:9", "1:1")

        Returns:
            Image file as bytes

        Raises:
            ProviderError: If generation fails
        """
        try:
            model = kwargs.get("model", self.image_model)

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    extra_headers={"X-Title": self.app_name},
                    extra_body={"modalities": ["image", "text"]},
                )
            )

            # Extract image from response
            message = response.choices[0].message

            # Handle images in content array
            if hasattr(message, "content") and isinstance(message.content, list):
                for part in message.content:
                    if hasattr(part, "type") and part.type == "image_url":
                        url = part.image_url.url
                        if url.startswith("data:"):
                            # Base64 data URL
                            b64_data = url.split(",", 1)[1]
                            return base64.b64decode(b64_data)

            # Handle images field (some models)
            if hasattr(message, "images") and message.images:
                b64_data = message.images[0]
                return base64.b64decode(b64_data)

            raise ProviderError("No image found in response")

        except ProviderError:
            raise
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
