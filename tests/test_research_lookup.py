"""
Tests for research-lookup skill routing logic (v1.3.2).

Tests the intelligent routing between Perplexity and Gemini Deep Research
without requiring actual API keys or plugin installation.
"""

import pytest
import sys
import os

# Add research-lookup script directory to path
script_dir = os.path.join(
    os.path.dirname(__file__),
    "..",
    "project_planner",
    ".claude",
    "skills",
    "research-lookup",
    "scripts"
)
sys.path.insert(0, script_dir)

from research_lookup import ResearchLookup


class TestResearchModeRouting:
    """Test research mode configuration affects routing decisions."""

    def test_perplexity_mode_never_uses_deep_research(self):
        """Perplexity mode should always return False for deep research."""
        tool = ResearchLookup(research_mode="perplexity")

        # Even with Phase 1 competitive analysis (normally Deep Research)
        result = tool._should_use_deep_research("competitive landscape analysis")
        assert result is False

        # Even with deep research keywords
        result = tool._should_use_deep_research("comprehensive market analysis")
        assert result is False

    def test_deep_research_mode_always_uses_deep_research(self):
        """Deep research mode should always return True."""
        tool = ResearchLookup(research_mode="deep_research")

        # Even for simple queries
        result = tool._should_use_deep_research("What is React?")
        assert result is True

        # Even for quick lookups
        result = tool._should_use_deep_research("Current AWS pricing")
        assert result is True

    def test_balanced_mode_uses_deep_research_for_phase1_competitive(self):
        """Balanced mode should use Deep Research for Phase 1 competitive analysis."""
        context = {"phase": 1, "task_type": "competitive-analysis"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        result = tool._should_use_deep_research("Analyze competitors")
        assert result is True

    def test_balanced_mode_uses_deep_research_for_phase1_market_reports(self):
        """Balanced mode should use Deep Research for Phase 1 market reports."""
        context = {"phase": 1, "task_type": "market-research-reports"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        result = tool._should_use_deep_research("Market research report")
        assert result is True

    def test_balanced_mode_uses_perplexity_for_phase1_quick_lookup(self):
        """Balanced mode should use Perplexity for Phase 1 quick lookups."""
        context = {"phase": 1, "task_type": "research-lookup"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        result = tool._should_use_deep_research("Quick fact lookup")
        assert result is False

    def test_balanced_mode_uses_perplexity_for_phase2_general(self):
        """Balanced mode should use Perplexity for Phase 2 general queries."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        result = tool._should_use_deep_research("How does PostgreSQL work?")
        assert result is False

    def test_auto_mode_default_behavior(self):
        """Auto mode should use Perplexity by default for simple queries."""
        tool = ResearchLookup(research_mode="auto")

        result = tool._should_use_deep_research("Simple query")
        assert result is False


class TestPhaseBasedRouting:
    """Test phase-based routing logic."""

    def test_phase1_competitive_analysis_uses_deep_research(self):
        """Phase 1 competitive analysis should use Deep Research."""
        context = {"phase": 1, "task_type": "competitive-analysis"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("Competitor analysis")
        assert result is True

    def test_phase1_market_research_uses_deep_research(self):
        """Phase 1 market research reports should use Deep Research."""
        context = {"phase": 1, "task_type": "market-research-reports"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("Market analysis")
        assert result is True

    def test_phase1_research_lookup_uses_perplexity(self):
        """Phase 1 quick lookups should use Perplexity."""
        context = {"phase": 1, "task_type": "research-lookup"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("Quick fact")
        assert result is False

    def test_phase2_architecture_decision_uses_deep_research(self):
        """Phase 2 architecture decisions should use Deep Research."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("architecture decision for microservices")
        assert result is True

    def test_phase2_technology_evaluation_uses_deep_research(self):
        """Phase 2 technology evaluation should use Deep Research."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("technology evaluation for databases")
        assert result is True

    def test_phase2_simple_query_uses_perplexity(self):
        """Phase 2 simple queries should use Perplexity."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("How to install PostgreSQL?")
        assert result is False

    def test_phase3_uses_perplexity_by_default(self):
        """Phase 3 queries should use Perplexity by default."""
        context = {"phase": 3, "task_type": "service-cost-analysis"}
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("AWS pricing")
        assert result is False


class TestKeywordBasedRouting:
    """Test keyword-based routing logic."""

    def test_competitive_landscape_keyword(self):
        """'competitive landscape' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("competitive landscape for SaaS products")
        assert result is True

    def test_market_analysis_keyword(self):
        """'market analysis' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("market analysis for fintech")
        assert result is True

    def test_competitor_analysis_keyword(self):
        """'competitor analysis' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("competitor analysis")
        assert result is True

    def test_comprehensive_analysis_keyword(self):
        """'comprehensive analysis' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("comprehensive analysis of AI trends")
        assert result is True

    def test_deep_dive_keyword(self):
        """'deep dive' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("deep dive into blockchain technology")
        assert result is True

    def test_in_depth_analysis_keyword(self):
        """'in-depth analysis' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("in-depth analysis of cloud providers")
        assert result is True

    def test_strategic_analysis_keyword(self):
        """'strategic analysis' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("strategic analysis for market entry")
        assert result is True

    def test_feasibility_study_keyword(self):
        """'feasibility study' should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("feasibility study for new product")
        assert result is True

    def test_no_keywords_uses_perplexity(self):
        """Queries without keywords should use Perplexity."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("What is React?")
        assert result is False


class TestQueryLengthRouting:
    """Test query length affects routing."""

    def test_very_long_query_uses_deep_research(self):
        """Queries over 300 characters should use Deep Research."""
        tool = ResearchLookup(research_mode="auto")

        long_query = "a" * 301  # 301 characters
        result = tool._should_use_deep_research(long_query)
        assert result is True

    def test_short_query_uses_perplexity(self):
        """Short queries should use Perplexity."""
        tool = ResearchLookup(research_mode="auto")

        short_query = "a" * 50  # 50 characters
        result = tool._should_use_deep_research(short_query)
        assert result is False

    def test_boundary_query_uses_perplexity(self):
        """Queries at exactly 300 characters should use Perplexity."""
        tool = ResearchLookup(research_mode="auto")

        boundary_query = "a" * 300  # Exactly 300 characters
        result = tool._should_use_deep_research(boundary_query)
        assert result is False


class TestPerplexityModelSelection:
    """Test Perplexity model selection logic."""

    def test_force_model_pro(self):
        """Forcing 'pro' model should use sonar-pro."""
        tool = ResearchLookup(research_mode="perplexity", force_model="pro")
        model = tool._select_model("any query")
        assert model == "perplexity/sonar-pro"

    def test_force_model_reasoning(self):
        """Forcing 'reasoning' model should use sonar-reasoning-pro."""
        tool = ResearchLookup(research_mode="perplexity", force_model="reasoning")
        model = tool._select_model("any query")
        assert model == "perplexity/sonar-reasoning-pro"

    def test_compare_keyword_uses_reasoning(self):
        """'compare' keyword should select reasoning model."""
        tool = ResearchLookup(research_mode="perplexity")
        model = tool._select_model("compare React and Vue")
        assert model == "perplexity/sonar-reasoning-pro"

    def test_analyze_keyword_uses_reasoning(self):
        """'analyze' keyword should select reasoning model."""
        tool = ResearchLookup(research_mode="perplexity")
        model = tool._select_model("analyze the pros and cons")
        assert model == "perplexity/sonar-reasoning-pro"

    def test_versus_keyword_uses_reasoning(self):
        """'versus' keyword should select reasoning model."""
        tool = ResearchLookup(research_mode="perplexity")
        model = tool._select_model("Python versus JavaScript")
        assert model == "perplexity/sonar-reasoning-pro"

    def test_multiple_questions_use_reasoning(self):
        """Multiple questions should select reasoning model."""
        tool = ResearchLookup(research_mode="perplexity")
        model = tool._select_model("What is React? How does it work?")
        assert model == "perplexity/sonar-reasoning-pro"

    def test_long_query_uses_reasoning(self):
        """Queries over 200 characters should use reasoning model."""
        tool = ResearchLookup(research_mode="perplexity")
        long_query = "a" * 201
        model = tool._select_model(long_query)
        assert model == "perplexity/sonar-reasoning-pro"

    def test_simple_query_uses_pro(self):
        """Simple queries should use pro model."""
        tool = ResearchLookup(research_mode="perplexity")
        model = tool._select_model("What is React?")
        assert model == "perplexity/sonar-pro"


class TestContextPropagation:
    """Test context is properly used in routing decisions."""

    def test_context_with_phase_and_task_type(self):
        """Context with phase and task_type should affect routing."""
        context = {
            "phase": 1,
            "task_type": "competitive-analysis",
            "project_name": "test-project"
        }
        tool = ResearchLookup(research_mode="auto", context=context)

        result = tool._should_use_deep_research("competitor research")
        assert result is True

    def test_empty_context_defaults_to_perplexity(self):
        """Empty context should default to Perplexity."""
        tool = ResearchLookup(research_mode="auto", context={})

        result = tool._should_use_deep_research("simple query")
        assert result is False

    def test_missing_context_defaults_to_perplexity(self):
        """Missing context should default to Perplexity."""
        tool = ResearchLookup(research_mode="auto")

        result = tool._should_use_deep_research("simple query")
        assert result is False

    def test_partial_context_still_works(self):
        """Partial context (only phase, no task_type) should work."""
        context = {"phase": 2}
        tool = ResearchLookup(research_mode="auto", context=context)

        # Should still use Perplexity without task_type
        result = tool._should_use_deep_research("simple query")
        assert result is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_case_insensitive_keyword_matching(self):
        """Keyword matching should be case-insensitive."""
        tool = ResearchLookup(research_mode="auto")

        # Uppercase
        assert tool._should_use_deep_research("COMPETITIVE LANDSCAPE") is True
        # Mixed case
        assert tool._should_use_deep_research("Competitive Landscape") is True
        # Lowercase
        assert tool._should_use_deep_research("competitive landscape") is True

    def test_empty_query_uses_perplexity(self):
        """Empty query should default to Perplexity."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("")
        assert result is False

    def test_whitespace_query_uses_perplexity(self):
        """Whitespace-only query should default to Perplexity."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research("   ")
        assert result is False

    def test_multiple_keywords_trigger_deep_research(self):
        """Query with multiple Deep Research keywords should trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")
        result = tool._should_use_deep_research(
            "comprehensive analysis of competitive landscape and market analysis"
        )
        assert result is True

    def test_keyword_partial_match_does_not_trigger(self):
        """Partial keyword matches should not trigger Deep Research."""
        tool = ResearchLookup(research_mode="auto")

        # "competitive" alone is not a keyword, needs "competitive landscape"
        result = tool._should_use_deep_research("competitive pricing")
        assert result is False


class TestRealWorldScenarios:
    """Test realistic research scenarios."""

    def test_phase1_competitor_research_scenario(self):
        """Realistic Phase 1 competitor research should use Deep Research."""
        context = {"phase": 1, "task_type": "competitive-analysis"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        query = "Analyze the competitive landscape for B2B SaaS inventory management platforms"
        result = tool._should_use_deep_research(query)
        assert result is True

    def test_phase2_quick_tech_lookup_scenario(self):
        """Realistic Phase 2 quick tech lookup should use Perplexity."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        query = "What is the current stable version of PostgreSQL?"
        result = tool._should_use_deep_research(query)
        assert result is False

    def test_phase2_architecture_decision_scenario(self):
        """Realistic Phase 2 architecture decision should use Deep Research."""
        context = {"phase": 2, "task_type": "architecture-research"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        query = "architecture decision: Should we use monolithic or microservices for a B2B SaaS?"
        result = tool._should_use_deep_research(query)
        assert result is True

    def test_phase3_cost_analysis_scenario(self):
        """Realistic Phase 3 cost analysis should use Perplexity."""
        context = {"phase": 3, "task_type": "service-cost-analysis"}
        tool = ResearchLookup(research_mode="balanced", context=context)

        query = "What are the current AWS RDS pricing tiers for PostgreSQL?"
        result = tool._should_use_deep_research(query)
        assert result is False

    def test_comprehensive_mode_always_deep_research(self):
        """Comprehensive mode should use Deep Research even for simple queries."""
        tool = ResearchLookup(research_mode="deep_research")

        query = "What is React?"
        result = tool._should_use_deep_research(query)
        assert result is True

    def test_quick_mode_never_deep_research(self):
        """Quick mode should never use Deep Research, even for complex queries."""
        context = {"phase": 1, "task_type": "competitive-analysis"}
        tool = ResearchLookup(research_mode="perplexity", context=context)

        query = "comprehensive analysis of competitive landscape for market analysis"
        result = tool._should_use_deep_research(query)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
