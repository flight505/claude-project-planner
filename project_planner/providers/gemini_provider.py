"""
Google Gemini API provider implementation.

This module provides integration with Google's Gemini API, including:
- Deep Research (requires Google AI Pro subscription)
- Veo 3.1 video generation
- Gemini 2.0 Flash Thinking for text generation
- 1M token context window

Requires:
    - google-genai package
    - GEMINI_API_KEY environment variable
    - Google AI Pro subscription for Deep Research
"""

import asyncio
import time
from typing import Any, Dict, Optional

from .base import (
    BaseAPIProvider,
    ProviderAuthenticationError,
    ProviderError,
    ProviderTimeoutError,
)


class GeminiProvider(BaseAPIProvider):
    """Google Gemini API provider implementation."""

    # Default models
    DEFAULT_TEXT_MODEL = "gemini-2.0-flash-thinking-exp-01-21"
    DEFAULT_VIDEO_MODEL = "veo-3.1-generate-preview"
    DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-001"
    DEEP_RESEARCH_AGENT = "deep-research-pro-preview-12-2025"

    # Timeouts
    DEEP_RESEARCH_TIMEOUT = 3600  # 60 minutes max
    VIDEO_GENERATION_TIMEOUT = 300  # 5 minutes max
    TEXT_GENERATION_TIMEOUT = 60  # 1 minute max

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google Gemini API key
            **kwargs: Additional configuration
                - text_model: Override default text model
                - video_model: Override default video model
                - image_model: Override default image model
        """
        super().__init__(api_key, **kwargs)

        try:
            from google import genai
            from google.genai import types

            self.genai = genai
            self.types = types
            self.client = genai.Client(api_key=api_key)
        except ImportError as e:
            raise ProviderError(
                "google-genai package not installed. "
                "Install with: pip install google-genai"
            ) from e
        except Exception as e:
            raise ProviderAuthenticationError(
                f"Failed to initialize Gemini client: {e}"
            ) from e

        # Model configuration
        self.text_model = kwargs.get("text_model", self.DEFAULT_TEXT_MODEL)
        self.video_model = kwargs.get("video_model", self.DEFAULT_VIDEO_MODEL)
        self.image_model = kwargs.get("image_model", self.DEFAULT_IMAGE_MODEL)

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Gemini models.

        Args:
            prompt: Input prompt
            model: Model override (defaults to gemini-2.0-flash-thinking)
            **kwargs: Additional generation parameters

        Returns:
            Generated text

        Raises:
            ProviderError: If generation fails
            ProviderTimeoutError: If generation times out
        """
        try:
            model_name = model or self.text_model

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    **kwargs
                )
            )

            return response.text

        except Exception as e:
            raise ProviderError(f"Text generation failed: {e}") from e

    async def deep_research(
        self,
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Conduct deep research using Gemini Deep Research agent.

        Requires Google AI Pro subscription ($19.99/month).
        AI Pro: 5 reports/month
        AI Ultra: 200 reports/day

        Args:
            query: Research question or topic
            **kwargs: Additional parameters
                - background: bool - Run in background (default: True)
                - timeout: int - Max wait time in seconds

        Returns:
            Dictionary containing:
                - report: Full research report text
                - citations: List of sources (extracted from report)
                - metadata: Interaction metadata

        Raises:
            ProviderError: If research fails
            ProviderTimeoutError: If research times out
        """
        try:
            background = kwargs.get("background", True)
            timeout = kwargs.get("timeout", self.DEEP_RESEARCH_TIMEOUT)

            # Create interaction
            loop = asyncio.get_event_loop()
            interaction = await loop.run_in_executor(
                None,
                lambda: self.client.interactions.create(
                    input=query,
                    agent=self.DEEP_RESEARCH_AGENT,
                    background=background
                )
            )

            start_time = time.time()

            # Poll for completion
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    raise ProviderTimeoutError(
                        f"Deep research timed out after {timeout} seconds"
                    )

                # Get current status
                interaction = await loop.run_in_executor(
                    None,
                    lambda: self.client.interactions.get(interaction.id)
                )

                if interaction.status == "completed":
                    report_text = interaction.outputs[-1].text if interaction.outputs else ""

                    return {
                        "report": report_text,
                        "citations": self._extract_citations(report_text),
                        "metadata": {
                            "interaction_id": interaction.id,
                            "status": interaction.status,
                            "elapsed_time": time.time() - start_time,
                        }
                    }

                elif interaction.status == "failed":
                    error_msg = getattr(interaction, "error", "Unknown error")
                    raise ProviderError(f"Deep research failed: {error_msg}")

                # Wait before next poll
                await asyncio.sleep(10)

        except ProviderTimeoutError:
            raise
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Deep research failed: {e}") from e

    async def generate_video(
        self,
        prompt: str,
        duration: int = 8,
        **kwargs
    ) -> bytes:
        """
        Generate video using Veo 3.1.

        Pricing: $0.75/second (e.g., 8 seconds = $6.00)

        Args:
            prompt: Video description with cinematographic details
            duration: Video duration in seconds (4, 6, or 8)
            **kwargs: Additional parameters
                - resolution: "720p" or "1080p"
                - aspect_ratio: "16:9", "9:16", "1:1"
                - reference_images: List of reference images
                - model: Override video model

        Returns:
            Video file as bytes (MP4 format)

        Raises:
            ProviderError: If generation fails
            ProviderTimeoutError: If generation times out
        """
        try:
            model = kwargs.get("model", self.video_model)
            timeout = kwargs.get("timeout", self.VIDEO_GENERATION_TIMEOUT)

            # Prepare generation config
            config_params = {}
            if "resolution" in kwargs:
                config_params["resolution"] = kwargs["resolution"]
            if "aspect_ratio" in kwargs:
                config_params["aspect_ratio"] = kwargs["aspect_ratio"]
            if "reference_images" in kwargs:
                config_params["reference_images"] = kwargs["reference_images"]

            config = self.types.GenerateVideosConfig(**config_params) if config_params else None

            # Start generation
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=model,
                    prompt=prompt,
                    config=config
                )
            )

            start_time = time.time()

            # Poll for completion
            while not operation.done:
                # Check timeout
                if time.time() - start_time > timeout:
                    raise ProviderTimeoutError(
                        f"Video generation timed out after {timeout} seconds"
                    )

                await asyncio.sleep(20)

                # Refresh operation status
                operation = await loop.run_in_executor(
                    None,
                    lambda: self.client.operations.get(operation)
                )

            # Download generated video
            generated_video = operation.result.generated_videos[0]
            video_bytes = await loop.run_in_executor(
                None,
                lambda: self.client.files.download(file=generated_video.video)
            )

            return video_bytes

        except ProviderTimeoutError:
            raise
        except Exception as e:
            raise ProviderError(f"Video generation failed: {e}") from e

    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> bytes:
        """
        Generate image using Imagen 3.

        Args:
            prompt: Image description
            **kwargs: Additional parameters
                - model: Override image model
                - aspect_ratio: "1:1", "16:9", "9:16", "4:3", "3:4"
                - negative_prompt: What to avoid
                - safety_filter: Safety filter level

        Returns:
            Image file as bytes

        Raises:
            ProviderError: If generation fails
        """
        try:
            model = kwargs.get("model", self.image_model)

            # Prepare config
            config_params = {}
            if "aspect_ratio" in kwargs:
                config_params["aspect_ratio"] = kwargs["aspect_ratio"]
            if "negative_prompt" in kwargs:
                config_params["negative_prompt"] = kwargs["negative_prompt"]

            config = self.types.GenerateImagesConfig(**config_params) if config_params else None

            # Generate image
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_images(
                    model=model,
                    prompt=prompt,
                    config=config
                )
            )

            # Get first image
            if response.generated_images:
                image = response.generated_images[0]
                return image.image.data  # Return bytes
            else:
                raise ProviderError("No images generated")

        except Exception as e:
            raise ProviderError(f"Image generation failed: {e}") from e

    def supports_feature(self, feature: str) -> bool:
        """
        Check if Gemini provider supports a feature.

        Args:
            feature: Feature name

        Returns:
            True if supported, False otherwise
        """
        supported_features = {
            "text_generation",
            "deep_research",
            "video_generation",
            "image_generation",
            "1m_token_context",
        }

        return feature in supported_features

    def _extract_citations(self, report: str) -> list:
        """
        Extract citations from research report.

        Gemini Deep Research includes citations as numbered references
        like [1], [2], etc. with URLs at the bottom of the report.

        Args:
            report: Research report text

        Returns:
            List of dictionaries with citation info
        """
        import re

        citations = []

        # Pattern to match citations: [1] https://example.com - Title
        pattern = r'\[(\d+)\]\s+(https?://[^\s]+)(?:\s+-\s+(.+))?'

        for match in re.finditer(pattern, report):
            citation_num = match.group(1)
            url = match.group(2)
            title = match.group(3) if match.group(3) else url

            citations.append({
                "number": int(citation_num),
                "url": url,
                "title": title.strip()
            })

        return citations
