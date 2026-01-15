#!/usr/bin/env python3
"""
Test and Validate AI Provider API Keys

This script tests that API keys are not only present, but actually work
by making real API calls to each provider.

Usage:
    python scripts/test-providers.py [--verbose]
"""

import os
import sys
import asyncio
from typing import Dict, Optional, Tuple


def test_anthropic_key() -> Tuple[bool, str, Optional[str]]:
    """
    Test ANTHROPIC_API_KEY by listing models.

    Returns:
        (is_valid, status_message, error_details)
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return False, "Not set", None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Test by listing models (lightweight call)
        models = client.models.list()
        return True, "Valid", None
    except Exception as e:
        return False, "Invalid", str(e)


def test_claude_max_token() -> Tuple[bool, str, Optional[str]]:
    """
    Test CLAUDE_CODE_OAUTH_TOKEN.

    Returns:
        (is_valid, status_message, error_details)
    """
    token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        return False, "Not set", None

    # OAuth tokens are harder to validate without full context
    # Just check it exists and has reasonable format
    if len(token) > 20 and not token.startswith("sk-"):
        return True, "Found (Claude Max)", None
    else:
        return False, "Invalid format", "Token doesn't match expected format"


def test_openrouter_key() -> Tuple[bool, str, Optional[str]]:
    """
    Test OPENROUTER_API_KEY by fetching models.

    Returns:
        (is_valid, status_message, error_details)
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False, "Not set", None

    try:
        import requests
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            # Check credits (optional)
            credits_response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if credits_response.status_code == 200:
                data = credits_response.json()
                limit = data.get("data", {}).get("limit")
                if limit:
                    return True, f"Valid (${limit:.2f} credits)", None
            return True, "Valid", None
        elif response.status_code == 401:
            return False, "Invalid key", "Authentication failed"
        else:
            return False, f"Error ({response.status_code})", response.text[:100]

    except Exception as e:
        return False, "Connection failed", str(e)


def test_gemini_key() -> Tuple[bool, str, Optional[str]]:
    """
    Test GEMINI_API_KEY by listing models.

    Returns:
        (is_valid, status_message, error_details)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "Not set", None

    try:
        import requests
        response = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            # Check for Deep Research capability
            has_deep_research = any(
                "deep-research" in model.get("name", "").lower()
                for model in models
            )
            if has_deep_research:
                return True, "Valid (Deep Research available)", None
            else:
                return True, "Valid", None
        elif response.status_code == 400:
            return False, "Invalid key", "API key not recognized"
        else:
            return False, f"Error ({response.status_code})", response.text[:100]

    except Exception as e:
        return False, "Connection failed", str(e)


def test_perplexity_key() -> Tuple[bool, str, Optional[str]]:
    """
    Test PERPLEXITY_API_KEY with a minimal query.

    Returns:
        (is_valid, status_message, error_details)
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return False, "Not set", None

    try:
        import requests
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            },
            timeout=10
        )

        if response.status_code == 200:
            return True, "Valid", None
        elif response.status_code == 401:
            return False, "Invalid key", "Authentication failed"
        else:
            return False, f"Error ({response.status_code})", response.text[:100]

    except Exception as e:
        return False, "Connection failed", str(e)


def get_available_capabilities(test_results: Dict[str, Tuple[bool, str, Optional[str]]]) -> Dict[str, bool]:
    """
    Determine what capabilities are available based on API key test results.

    Returns:
        Dict mapping capability names to availability
    """
    claude_available = (
        test_results["CLAUDE_CODE_OAUTH_TOKEN"][0] or
        test_results["ANTHROPIC_API_KEY"][0]
    )

    return {
        "planning": claude_available,
        "fast_research": (
            test_results["OPENROUTER_API_KEY"][0] or
            test_results["PERPLEXITY_API_KEY"][0]
        ),
        "deep_research": test_results["GEMINI_API_KEY"][0],
        "nanobanana_images": (
            test_results["GEMINI_API_KEY"][0] or
            test_results["OPENROUTER_API_KEY"][0]
        ),
        "flux_images": test_results["OPENROUTER_API_KEY"][0],
    }


def print_capability_matrix(capabilities: Dict[str, bool]):
    """Print a formatted capability matrix."""
    print("\n" + "=" * 70)
    print("  Available Capabilities")
    print("=" * 70)
    print()

    status = lambda available: "✅" if available else "❌"

    print(f"{status(capabilities['planning'])}  Core Planning (Claude Sonnet)")
    print(f"{status(capabilities['fast_research'])}  Fast Research (Perplexity Sonar, ~30 sec)")
    print(f"{status(capabilities['deep_research'])}  Deep Research (Gemini Agent, 60 min)")
    print(f"{status(capabilities['nanobanana_images'])}  Image Generation (NanoBanana Pro)")
    print(f"{status(capabilities['flux_images'])}  Photo Generation (Flux Pro)")
    print()

    # Research mode availability
    print("Research Modes:")
    print(f"  {status(capabilities['fast_research'])}  Quick - Perplexity only")
    print(f"  {status(capabilities['deep_research'])}  Balanced - Deep Research for Phase 1")
    print(f"  {status(capabilities['deep_research'])}  Comprehensive - Deep Research for all")
    print(f"  {status(capabilities['fast_research'])}  Auto - Use best available")
    print()


def print_recommendations(test_results: Dict[str, Tuple[bool, str, Optional[str]]]):
    """Print recommendations for missing capabilities."""
    missing = []

    if not test_results["GEMINI_API_KEY"][0]:
        missing.append({
            "key": "GEMINI_API_KEY",
            "enables": "Deep Research (60-min comprehensive analysis)",
            "url": "https://aistudio.google.com/apikey",
            "cost": "Free tier (20 req/day) or $19.99/mo AI Pro"
        })

    if not test_results["OPENROUTER_API_KEY"][0]:
        missing.append({
            "key": "OPENROUTER_API_KEY",
            "enables": "Perplexity research & NanoBanana/Flux images",
            "url": "https://openrouter.ai/keys",
            "cost": "Pay-per-use (~$0.01/query + 5.5% fee)"
        })

    if not test_results["PERPLEXITY_API_KEY"][0] and not test_results["OPENROUTER_API_KEY"][0]:
        missing.append({
            "key": "PERPLEXITY_API_KEY",
            "enables": "Direct Perplexity access (skip OpenRouter fee)",
            "url": "https://www.perplexity.ai/settings/api",
            "cost": "$5/1M tokens"
        })

    if missing:
        print("=" * 70)
        print("  💡 Optional Enhancements")
        print("=" * 70)
        print()

        for item in missing:
            print(f"Add {item['key']} to enable:")
            print(f"  • {item['enables']}")
            print(f"  • Get key: {item['url']}")
            print(f"  • Cost: {item['cost']}")
            print()

        print("Add keys to ~/.zshrc or ~/.bashrc:")
        for item in missing:
            print(f"  export {item['key']}='your-key-here'")
        print()
        print("Then run: source ~/.zshrc && /project-planner:setup")
        print()


def main():
    """Main testing routine."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print("=" * 70)
    print("  Claude Project Planner - Provider Validation")
    print("=" * 70)
    print()
    print("Testing API keys...")
    print()

    # Test all providers
    tests = {
        "CLAUDE_CODE_OAUTH_TOKEN": test_claude_max_token,
        "ANTHROPIC_API_KEY": test_anthropic_key,
        "OPENROUTER_API_KEY": test_openrouter_key,
        "GEMINI_API_KEY": test_gemini_key,
        "PERPLEXITY_API_KEY": test_perplexity_key,
    }

    results = {}
    for key_name, test_func in tests.items():
        is_valid, status, error = test_func()
        results[key_name] = (is_valid, status, error)

        # Format output
        symbol = "✅" if is_valid else "❌" if status != "Not set" else "⬜"
        print(f"  {symbol}  {key_name:25} {status}")

        if verbose and error:
            print(f"      └─ {error[:60]}")

    # Determine available capabilities
    capabilities = get_available_capabilities(results)

    # Print capability matrix
    print_capability_matrix(capabilities)

    # Print recommendations
    print_recommendations(results)

    # Exit status
    if capabilities["planning"]:
        print("✨ Core planning capabilities available!")
        return 0
    else:
        print("❌ Missing core authentication (CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
