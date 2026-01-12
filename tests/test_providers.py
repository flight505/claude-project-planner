"""
Tests for AI provider abstraction layer.

This module tests the provider routing logic, fallback chains,
and individual provider implementations.
"""

import os
import pytest

from project_planner.providers import (
    ProviderRouter,
    ProviderNotAvailableError,
    FeatureNotSupportedError,
)


class TestProviderRouter:
    """Tests for ProviderRouter class."""

    def test_router_initialization_no_keys(self, monkeypatch):
        """Test router initialization when no API keys are set."""
        # Remove all API keys
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()

        assert len(router.providers) == 0
        assert router.get_available_providers() == {}

    def test_router_initialization_gemini_only(self, monkeypatch):
        """Test router with only Gemini API key."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()

        assert "gemini" in router.providers
        assert "openrouter" not in router.providers

    def test_router_initialization_openrouter_only(self, monkeypatch):
        """Test router with only OpenRouter API key."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()

        assert "openrouter" in router.providers
        assert "gemini" not in router.providers

    def test_router_initialization_both_keys(self, monkeypatch):
        """Test router with both API keys."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()

        assert "gemini" in router.providers
        assert "openrouter" in router.providers

    def test_get_text_provider_prefer_gemini(self, monkeypatch):
        """Test text provider selection prefers Gemini."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter(config={"prefer_gemini": True})
        provider = router.get_provider_for_task("text")

        assert provider == router.providers["gemini"]

    def test_get_text_provider_fallback_openrouter(self, monkeypatch):
        """Test text provider falls back to OpenRouter."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        provider = router.get_provider_for_task("text")

        assert provider == router.providers["openrouter"]

    def test_get_text_provider_no_providers(self, monkeypatch):
        """Test text provider raises error when no providers available."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()

        with pytest.raises(ProviderNotAvailableError, match="No text generation provider"):
            router.get_provider_for_task("text")

    def test_get_research_provider_prefer_gemini(self, monkeypatch):
        """Test research provider selection prefers Gemini (Deep Research)."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        provider = router.get_provider_for_task("research")

        assert provider == router.providers["gemini"]

    def test_get_research_provider_fallback_openrouter(self, monkeypatch):
        """Test research provider falls back to OpenRouter (Perplexity)."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        provider = router.get_provider_for_task("research")

        assert provider == router.providers["openrouter"]

    def test_get_video_provider_requires_gemini(self, monkeypatch):
        """Test video provider requires Gemini (Veo 3.1)."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

        router = ProviderRouter()
        provider = router.get_provider_for_task("video")

        assert provider == router.providers["gemini"]

    def test_get_video_provider_not_available(self, monkeypatch):
        """Test video provider raises error without Gemini."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()

        with pytest.raises(ProviderNotAvailableError, match="Video generation requires Gemini"):
            router.get_provider_for_task("video")

    def test_get_image_provider_prefer_openrouter(self, monkeypatch):
        """Test image provider selection prefers OpenRouter (lower cost)."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        provider = router.get_provider_for_task("image")

        assert provider == router.providers["openrouter"]

    def test_get_image_provider_fallback_gemini(self, monkeypatch):
        """Test image provider falls back to Gemini (Imagen)."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()
        provider = router.get_provider_for_task("image")

        assert provider == router.providers["gemini"]

    def test_force_specific_provider(self, monkeypatch):
        """Test forcing a specific provider."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()

        # Force OpenRouter for text even though Gemini is available
        provider = router.get_provider_for_task("text", prefer_provider="openrouter")
        assert provider == router.providers["openrouter"]

        # Force Gemini
        provider = router.get_provider_for_task("text", prefer_provider="gemini")
        assert provider == router.providers["gemini"]

    def test_force_unavailable_provider(self, monkeypatch):
        """Test forcing an unavailable provider raises error."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()

        with pytest.raises(ProviderNotAvailableError, match="openrouter"):
            router.get_provider_for_task("text", prefer_provider="openrouter")

    def test_has_feature(self, monkeypatch):
        """Test feature availability checking."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()

        assert router.has_feature("text_generation")
        assert router.has_feature("deep_research")
        assert router.has_feature("video_generation")
        assert router.has_feature("image_generation")

    def test_has_feature_no_providers(self, monkeypatch):
        """Test feature checking with no providers."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        router = ProviderRouter()

        assert not router.has_feature("text_generation")
        assert not router.has_feature("deep_research")
        assert not router.has_feature("video_generation")

    def test_get_available_providers(self, monkeypatch):
        """Test getting available providers and capabilities."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        providers = router.get_available_providers()

        assert "gemini" in providers
        assert "openrouter" in providers

        # Check Gemini capabilities
        assert providers["gemini"]["text_generation"]
        assert providers["gemini"]["deep_research"]
        assert providers["gemini"]["video_generation"]

        # Check OpenRouter capabilities
        assert providers["openrouter"]["text_generation"]
        assert providers["openrouter"]["deep_research"]
        assert not providers["openrouter"]["video_generation"]

    def test_router_repr(self, monkeypatch):
        """Test router string representation."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

        router = ProviderRouter()
        repr_str = repr(router)

        assert "ProviderRouter" in repr_str
        assert "gemini" in repr_str
        assert "openrouter" in repr_str


class TestProviderCapabilities:
    """Tests for individual provider capabilities."""

    def test_gemini_capabilities(self, monkeypatch):
        """Test Gemini provider supports expected features."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        router = ProviderRouter()
        provider = router.providers["gemini"]

        assert provider.supports_feature("text_generation")
        assert provider.supports_feature("deep_research")
        assert provider.supports_feature("video_generation")
        assert provider.supports_feature("image_generation")
        assert provider.supports_feature("1m_token_context")

    def test_openrouter_capabilities(self, monkeypatch):
        """Test OpenRouter provider supports expected features."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

        router = ProviderRouter()
        provider = router.providers["openrouter"]

        assert provider.supports_feature("text_generation")
        assert provider.supports_feature("deep_research")
        assert not provider.supports_feature("video_generation")
        assert provider.supports_feature("image_generation")
        assert not provider.supports_feature("1m_token_context")


# Integration tests (require actual API keys, marked as skip by default)
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY for integration testing"
)
@pytest.mark.asyncio
async def test_gemini_text_generation_integration():
    """Integration test for Gemini text generation."""
    from project_planner.providers import GeminiProvider

    provider = GeminiProvider(os.getenv("GEMINI_API_KEY"))
    result = await provider.generate_text("What is 2+2? Answer briefly.")

    assert "4" in result.lower()


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="Requires OPENROUTER_API_KEY for integration testing"
)
@pytest.mark.asyncio
async def test_openrouter_text_generation_integration():
    """Integration test for OpenRouter text generation."""
    from project_planner.providers import OpenRouterProvider

    provider = OpenRouterProvider(os.getenv("OPENROUTER_API_KEY"))
    result = await provider.generate_text("What is 2+2? Answer briefly.")

    assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
