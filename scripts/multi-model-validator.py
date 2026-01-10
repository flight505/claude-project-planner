#!/usr/bin/env python3
"""
Multi-Model Architecture Validator

Validates architecture decisions by querying multiple AI models and
generating a consensus report.

Usage:
    python multi-model-validator.py \
        --architecture-file <path> \
        --building-blocks <path> \
        --output <path> \
        --models "gemini-2.0-flash,gpt-4o-mini,claude-3-5-haiku"
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model mappings for OpenRouter
MODEL_CONFIGS = {
    "gemini-2.0-flash": {
        "id": "google/gemini-2.0-flash-001",
        "name": "Gemini 2.0 Flash",
        "strength": "Fast, broad knowledge",
    },
    "gpt-4o-mini": {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "strength": "Strong reasoning",
    },
    "claude-3-5-haiku": {
        "id": "anthropic/claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku",
        "strength": "Code understanding",
    },
    "claude-3-5-sonnet": {
        "id": "anthropic/claude-3-5-sonnet-20241022",
        "name": "Claude 3.5 Sonnet",
        "strength": "Balanced analysis",
    },
    "deepseek-chat": {
        "id": "deepseek/deepseek-chat",
        "name": "DeepSeek Chat",
        "strength": "Technical depth",
    },
}


@dataclass
class ValidationResult:
    """Result from a single model's validation."""

    model: str
    model_name: str
    decision: str
    scores: dict
    recommendation: str
    reasoning: str
    alternative: Optional[str]
    raw_response: str
    error: Optional[str] = None


@dataclass
class DecisionConsensus:
    """Consensus for a single architecture decision."""

    decision: str
    context: str
    results: list  # List of ValidationResult
    avg_scores: dict
    consensus: str  # "approved", "reconsider", "reject"
    confidence: str  # "high", "medium", "low"


def extract_decisions_from_architecture(
    arch_content: str, blocks_content: str = ""
) -> list:
    """
    Extract key architecture decisions from the documents.

    Returns list of dicts with: decision, context, alternatives
    """
    decisions = []

    # Common decision patterns to look for
    decision_patterns = [
        # Technology choices
        (
            r"(?:use|using|chose|selected|picked)\s+(PostgreSQL|MySQL|MongoDB|DynamoDB|Redis|Cassandra)",
            "database",
        ),
        (
            r"(?:use|using|chose|selected)\s+(React|Vue|Angular|Next\.js|Svelte)",
            "frontend",
        ),
        (
            r"(?:use|using|chose|selected)\s+(Node\.js|Python|Go|Rust|Java|\.NET)",
            "backend",
        ),
        (
            r"(?:deploy(?:ed)?|host(?:ed)?)\s+(?:on|to)\s+(AWS|GCP|Azure|Vercel|Heroku)",
            "cloud",
        ),
        # Architecture patterns
        (
            r"(microservices?|monolith(?:ic)?|serverless|event.driven|CQRS)",
            "architecture",
        ),
        (r"(REST(?:ful)?|GraphQL|gRPC|WebSocket)", "api"),
        (r"(JWT|OAuth|SAML|API.keys?)", "authentication"),
        (r"(Kubernetes|Docker|ECS|Lambda)", "infrastructure"),
    ]

    combined_content = arch_content + "\n" + blocks_content

    # Extract decisions based on patterns
    found_decisions = set()
    for pattern, category in decision_patterns:
        matches = re.findall(pattern, combined_content, re.IGNORECASE)
        for match in matches:
            if match.lower() not in found_decisions:
                found_decisions.add(match.lower())
                # Try to find context around the decision
                context_match = re.search(
                    rf".{{0,200}}{re.escape(match)}.{{0,200}}",
                    combined_content,
                    re.IGNORECASE | re.DOTALL,
                )
                context = context_match.group(0).strip() if context_match else ""

                decisions.append(
                    {
                        "decision": f"Use {match} for {category}",
                        "context": context[:300],
                        "category": category,
                        "alternatives": [],  # Could be extracted from context
                    }
                )

    # Look for explicit ADR-style decisions
    adr_pattern = r"(?:Decision|Decided|Choice|Selected):\s*(.+?)(?:\n|$)"
    adr_matches = re.findall(adr_pattern, combined_content, re.IGNORECASE)
    for match in adr_matches:
        decision_text = match.strip()[:200]
        if decision_text and decision_text.lower() not in found_decisions:
            decisions.append(
                {
                    "decision": decision_text,
                    "context": "",
                    "category": "general",
                    "alternatives": [],
                }
            )

    return decisions[:10]  # Limit to top 10 decisions


def create_validation_prompt(decision: dict, project_context: str = "") -> str:
    """Create a validation prompt for a single decision."""
    return f"""You are a senior software architect reviewing an architecture decision.

Project Context:
{project_context[:500] if project_context else "Not provided"}

Decision to Review:
{decision["decision"]}

Context for this decision:
{decision["context"] if decision["context"] else "Not provided"}

Evaluate this decision on these criteria (score 1-10, where 10 is best):

1. **Scalability**: How well does this scale for growth?
2. **Security Risk**: How risky is this from a security perspective? (10 = low risk)
3. **Cost Effectiveness**: Is this cost-effective for a startup/SMB?
4. **Maintainability**: How easy is this to maintain long-term?

Then provide your recommendation: "approve", "reconsider", or "reject"

Respond ONLY with valid JSON in this exact format:
{{
  "decision": "{decision["decision"][:100]}",
  "scores": {{
    "scalability": <1-10>,
    "security_risk": <1-10>,
    "cost_effectiveness": <1-10>,
    "maintainability": <1-10>
  }},
  "recommendation": "<approve|reconsider|reject>",
  "reasoning": "<brief explanation in 2-3 sentences>",
  "alternative": "<suggested alternative if not approve, or null>"
}}"""


def query_model(model_id: str, prompt: str, api_key: str) -> tuple[str, Optional[str]]:
    """
    Query a model via OpenRouter API.

    Returns: (response_text, error_message)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flight505/claude-project-planner",
        "X-Title": "Claude Project Planner - Architecture Validator",
    }

    data = json.dumps(
        {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.3,  # Lower temperature for more consistent evaluation
        }
    ).encode("utf-8")

    try:
        request = Request(OPENROUTER_API_URL, data=data, headers=headers)
        with urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content, None

    except HTTPError as e:
        return "", f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        return "", f"Network error: {e.reason}"
    except json.JSONDecodeError as e:
        return "", f"JSON decode error: {e}"
    except Exception as e:
        return "", f"Error: {str(e)}"


def parse_model_response(
    response: str, model_name: str, decision: str
) -> ValidationResult:
    """Parse the JSON response from a model."""
    try:
        # Try to extract JSON from the response
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")

        return ValidationResult(
            model=model_name,
            model_name=model_name,
            decision=data.get("decision", decision),
            scores=data.get("scores", {}),
            recommendation=data.get("recommendation", "unknown"),
            reasoning=data.get("reasoning", ""),
            alternative=data.get("alternative"),
            raw_response=response,
        )
    except (json.JSONDecodeError, ValueError) as e:
        return ValidationResult(
            model=model_name,
            model_name=model_name,
            decision=decision,
            scores={},
            recommendation="unknown",
            reasoning="Failed to parse response",
            alternative=None,
            raw_response=response,
            error=str(e),
        )


def calculate_consensus(results: list) -> tuple[str, str, dict]:
    """
    Calculate consensus from multiple model results.

    Returns: (consensus, confidence, avg_scores)
    """
    valid_results = [
        r for r in results if not r.error and r.recommendation != "unknown"
    ]

    if not valid_results:
        return "unknown", "none", {}

    # Count recommendations
    approvals = sum(1 for r in valid_results if r.recommendation == "approve")
    reconsiders = sum(1 for r in valid_results if r.recommendation == "reconsider")
    rejects = sum(1 for r in valid_results if r.recommendation == "reject")

    total = len(valid_results)

    # Determine consensus
    if approvals > total / 2:
        consensus = "approved"
    elif rejects > total / 2:
        consensus = "rejected"
    else:
        consensus = "reconsider"

    # Calculate confidence
    max_agreement = max(approvals, reconsiders, rejects)
    if max_agreement == total:
        confidence = "high"
    elif max_agreement >= total * 0.67:
        confidence = "medium"
    else:
        confidence = "low"

    # Calculate average scores
    score_keys = [
        "scalability",
        "security_risk",
        "cost_effectiveness",
        "maintainability",
    ]
    avg_scores = {}
    for key in score_keys:
        values = [r.scores.get(key, 0) for r in valid_results if r.scores.get(key)]
        avg_scores[key] = round(sum(values) / len(values), 1) if values else 0

    return consensus, confidence, avg_scores


def generate_report(
    project_name: str,
    consensuses: list,
    models_used: list,
) -> str:
    """Generate the markdown validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    model_names: list[str] = [
        MODEL_CONFIGS.get(m, {}).get("name") or m for m in models_used
    ]

    lines = [
        "# Architecture Validation Report",
        "",
        f"**Project:** {project_name}",
        f"**Validated:** {timestamp}",
        f"**Models Used:** {', '.join(model_names)}",
        "",
        "## Executive Summary",
        "",
    ]

    # Summary counts
    approved_count = sum(1 for c in consensuses if c.consensus == "approved")
    reconsider_count = sum(1 for c in consensuses if c.consensus == "reconsider")
    rejected_count = sum(1 for c in consensuses if c.consensus == "rejected")

    lines.extend(
        [
            f"- **Approved:** {approved_count} decisions",
            f"- **Needs Review:** {reconsider_count} decisions",
            f"- **Rejected:** {rejected_count} decisions",
            "",
            "## Decision Summary",
            "",
            "| Decision | " + " | ".join(model_names) + " | Consensus |",
            "|----------|"
            + "|".join(["-------" for _ in model_names])
            + "|-----------|",
        ]
    )

    # Summary table
    for c in consensuses:
        row = [c.decision[:40] + "..." if len(c.decision) > 40 else c.decision]

        for result in c.results:
            if result.error:
                row.append("❌ Error")
            elif result.recommendation == "approve":
                avg = (
                    sum(result.scores.values()) / len(result.scores)
                    if result.scores
                    else 0
                )
                row.append(f"✅ {avg:.0f}/10")
            elif result.recommendation == "reconsider":
                avg = (
                    sum(result.scores.values()) / len(result.scores)
                    if result.scores
                    else 0
                )
                row.append(f"⚠️ {avg:.0f}/10")
            else:
                row.append(f"❌ {result.recommendation}")

        # Consensus
        if c.consensus == "approved":
            row.append(f"✅ **Approved** ({c.confidence})")
        elif c.consensus == "reconsider":
            row.append(f"⚠️ **Reconsider** ({c.confidence})")
        else:
            row.append(f"❌ **Rejected** ({c.confidence})")

        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Detailed Analysis", ""])

    # Detailed sections
    for i, c in enumerate(consensuses, 1):
        lines.extend(
            [
                f"### Decision {i}: {c.decision}",
                "",
                "**Average Scores:**",
            ]
        )

        if c.avg_scores:
            for key, value in c.avg_scores.items():
                label = key.replace("_", " ").title()
                bar = "█" * int(value) + "░" * (10 - int(value))
                lines.append(f"- {label}: [{bar}] {value}/10")

        lines.extend(["", "**Model Feedback:**", ""])

        for result in c.results:
            if result.error:
                lines.append(f"- **{result.model_name}:** ❌ {result.error}")
            else:
                lines.append(f"- **{result.model_name}:** {result.reasoning}")
                if result.alternative:
                    lines.append(f"  - *Alternative:* {result.alternative}")

        lines.extend(
            [
                "",
                f"**Consensus:** {c.consensus.title()} ({c.confidence} confidence)",
                "",
                "---",
                "",
            ]
        )

    # Recommendations section
    lines.extend(
        [
            "## Recommendations",
            "",
        ]
    )

    keep = [c.decision for c in consensuses if c.consensus == "approved"]
    review = [c.decision for c in consensuses if c.consensus == "reconsider"]
    reject = [c.decision for c in consensuses if c.consensus == "rejected"]

    if keep:
        lines.append("**Keep (Approved):**")
        for d in keep:
            lines.append(f"- ✅ {d}")
        lines.append("")

    if review:
        lines.append("**Review (Needs Attention):**")
        for d in review:
            lines.append(f"- ⚠️ {d}")
        lines.append("")

    if reject:
        lines.append("**Reconsider (Not Recommended):**")
        for d in reject:
            lines.append(f"- ❌ {d}")
        lines.append("")

    lines.extend(
        [
            "---",
            f"*Generated by Multi-Model Architecture Validator at {timestamp}*",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Multi-model architecture validator")
    parser.add_argument(
        "--architecture-file",
        type=Path,
        required=True,
        help="Path to architecture document",
    )
    parser.add_argument(
        "--building-blocks", type=Path, help="Path to building blocks file"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output path for validation report"
    )
    parser.add_argument(
        "--models",
        type=str,
        default="gemini-2.0-flash,gpt-4o-mini,claude-3-5-haiku",
        help="Comma-separated list of models to use",
    )
    parser.add_argument("--project-name", type=str, help="Project name for the report")

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Read input files
    if not args.architecture_file.exists():
        print(
            f"Error: Architecture file not found: {args.architecture_file}",
            file=sys.stderr,
        )
        sys.exit(1)

    arch_content = args.architecture_file.read_text(encoding="utf-8")
    blocks_content = ""
    if args.building_blocks and args.building_blocks.exists():
        blocks_content = args.building_blocks.read_text(encoding="utf-8")

    # Extract decisions
    print("Extracting architecture decisions...")
    decisions = extract_decisions_from_architecture(arch_content, blocks_content)

    if not decisions:
        print("Warning: No architecture decisions found to validate")
        # Create minimal report
        report = "# Architecture Validation Report\n\nNo architecture decisions found to validate."
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        sys.exit(0)

    print(f"Found {len(decisions)} decisions to validate")

    # Parse models
    models = [m.strip() for m in args.models.split(",")]
    valid_models = [m for m in models if m in MODEL_CONFIGS]

    if not valid_models:
        print(
            f"Error: No valid models specified. Available: {list(MODEL_CONFIGS.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Using models: {valid_models}")

    # Project context for prompts
    project_name = args.project_name or args.architecture_file.parent.name
    project_context = arch_content[:1000]  # First 1000 chars as context

    # Validate each decision with each model
    consensuses = []

    for i, decision in enumerate(decisions, 1):
        print(
            f"\nValidating decision {i}/{len(decisions)}: {decision['decision'][:50]}..."
        )

        prompt = create_validation_prompt(decision, project_context)
        results = []

        for model_key in valid_models:
            model_config = MODEL_CONFIGS[model_key]
            print(f"  Querying {model_config['name']}...")

            response, error = query_model(model_config["id"], prompt, api_key)

            if error:
                results.append(
                    ValidationResult(
                        model=model_key,
                        model_name=model_config["name"],
                        decision=decision["decision"],
                        scores={},
                        recommendation="unknown",
                        reasoning="",
                        alternative=None,
                        raw_response="",
                        error=error,
                    )
                )
            else:
                result = parse_model_response(
                    response, model_config["name"], decision["decision"]
                )
                results.append(result)

        # Calculate consensus
        consensus, confidence, avg_scores = calculate_consensus(results)

        consensuses.append(
            DecisionConsensus(
                decision=decision["decision"],
                context=decision["context"],
                results=results,
                avg_scores=avg_scores,
                consensus=consensus,
                confidence=confidence,
            )
        )

    # Generate report
    print("\nGenerating validation report...")
    report = generate_report(project_name, consensuses, valid_models)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")

    print(f"\n✓ Validation report saved to: {args.output}")

    # Print summary
    approved = sum(1 for c in consensuses if c.consensus == "approved")
    reconsider = sum(1 for c in consensuses if c.consensus == "reconsider")
    rejected = sum(1 for c in consensuses if c.consensus == "rejected")

    print(
        f"\nSummary: {approved} approved, {reconsider} need review, {rejected} rejected"
    )


if __name__ == "__main__":
    main()
