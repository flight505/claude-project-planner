"""
Streaming Research Wrapper - Pattern 1

Provides real-time progress feedback for research operations using Claude Agent SDK streaming.

Usage:
    wrapper = StreamingResearchWrapper(progress_callback)
    results = await wrapper.research_with_progress(query, max_turns=100)

Features:
- Real-time message streaming
- Tool execution visibility
- Agent thinking/reasoning display
- Progress callbacks for UI integration
"""

import asyncio
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

try:
    from claude_agent_sdk import (
        query,
        ClaudeAgentOptions,
        AssistantMessage,
        TextBlock,
        ToolUseBlock,
        ToolResultBlock
    )
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    # Mock classes for type hints when SDK not available
    class AssistantMessage: pass
    class TextBlock: pass
    class ToolUseBlock: pass
    class ToolResultBlock: pass


class StreamingResearchWrapper:
    """
    Wrapper that adds progress streaming to research tasks.

    Integrates with Claude Agent SDK to provide real-time feedback
    during research operations (e.g., Perplexity queries).
    """

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize wrapper with optional progress callback.

        Args:
            progress_callback: Async function called with (event_type, data)
                              Event types: "start", "thinking", "tool_start",
                                          "tool_result", "result", "error"
        """
        if not AGENT_SDK_AVAILABLE:
            raise ImportError(
                "Claude Agent SDK not available. "
                "Install with: pip install claude-agent-sdk"
            )

        self.progress_callback = progress_callback or self._default_callback
        self.tools_used: List[str] = []
        self.findings: List[str] = []
        self.start_time: Optional[datetime] = None

    async def _default_callback(self, event_type: str, data: Dict[str, Any]):
        """Default callback that prints to console."""
        if event_type == "start":
            print(f"🚀 Starting research...")
            print(f"   Query: {data['query'][:80]}...")

        elif event_type == "thinking":
            text = data.get("text", "")
            # Show first 100 chars of reasoning
            if text:
                print(f"  💭 {text[:100]}...")

        elif event_type == "tool_start":
            tool_name = data.get("tool_name", "unknown")
            print(f"  🛠️  Using: {tool_name}")

        elif event_type == "tool_result":
            tool_name = data.get("tool_name", "unknown")
            success = data.get("success", True)
            status = "✅" if success else "❌"
            print(f"  {status} {tool_name} completed")

        elif event_type == "result":
            print(f"  ✅ Research complete")

        elif event_type == "error":
            error = data.get("error", "Unknown error")
            print(f"  ❌ Error: {error}")

    async def research_with_progress(
        self,
        research_query: str,
        max_turns: int = 100,
        allowed_tools: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute research with real-time progress updates.

        Args:
            research_query: The research question to investigate
            max_turns: Maximum number of agent turns (default: 100)
            allowed_tools: List of tool patterns to allow (default: Read, WebSearch, Grep, Perplexity)

        Returns:
            Dictionary with:
                - query: Original query
                - tools_used: List of tools that were invoked
                - findings: List of text findings from the agent
                - duration_sec: Total execution time
                - turn_count: Number of agent turns taken

        Raises:
            Exception: If research fails after retries
        """
        self.start_time = datetime.now()
        self.tools_used = []
        self.findings = []

        # Default allowed tools for research
        if allowed_tools is None:
            allowed_tools = [
                "Read",
                "WebSearch",
                "Grep",
                "mcp__perplexity__*"
            ]

        options = ClaudeAgentOptions(
            allowed_tools=allowed_tools,
            max_turns=max_turns
        )

        results = {
            "query": research_query,
            "tools_used": [],
            "findings": [],
            "duration_sec": 0,
            "turn_count": 0
        }

        try:
            # Notify start
            await self.progress_callback("start", {"query": research_query})

            turn_count = 0

            # Stream messages from agent
            async for message in query(prompt=research_query, options=options):
                turn_count += 1

                if isinstance(message, AssistantMessage):
                    # Process each content block
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Agent reasoning/findings
                            text = block.text
                            results["findings"].append(text)
                            self.findings.append(text)

                            await self.progress_callback("thinking", {"text": text})

                        elif isinstance(block, ToolUseBlock):
                            # Tool execution started
                            tool_name = block.name
                            results["tools_used"].append(tool_name)
                            self.tools_used.append(tool_name)

                            await self.progress_callback("tool_start", {
                                "tool_name": tool_name,
                                "tool_input": getattr(block, "input", {})
                            })

                        elif isinstance(block, ToolResultBlock):
                            # Tool execution completed
                            tool_name = getattr(block, "tool_use_id", "unknown")
                            is_error = getattr(block, "is_error", False)

                            await self.progress_callback("tool_result", {
                                "tool_name": tool_name,
                                "success": not is_error
                            })

                # Check for final result
                elif hasattr(message, "result"):
                    # Research complete
                    duration = (datetime.now() - self.start_time).total_seconds()
                    results["duration_sec"] = duration
                    results["turn_count"] = turn_count

                    await self.progress_callback("result", {"data": results})
                    return results

            # If we exit loop without result, still return what we collected
            duration = (datetime.now() - self.start_time).total_seconds()
            results["duration_sec"] = duration
            results["turn_count"] = turn_count

            await self.progress_callback("result", {"data": results})
            return results

        except Exception as e:
            # Notify error
            await self.progress_callback("error", {"error": str(e)})
            raise

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of last research operation.

        Returns:
            Dictionary with tools used, findings count, and duration
        """
        duration = 0
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()

        return {
            "tools_used": list(set(self.tools_used)),
            "tool_count": len(self.tools_used),
            "findings_count": len(self.findings),
            "duration_sec": duration
        }


class ProgressFormatter:
    """
    Formats progress updates for console display.

    Provides consistent formatting for different event types.
    """

    ICONS = {
        "start": "🚀",
        "thinking": "💭",
        "tool_start": "🛠️",
        "tool_result_success": "✅",
        "tool_result_failure": "❌",
        "result": "✅",
        "error": "❌",
        "checkpoint": "💾"
    }

    @staticmethod
    def format_event(event_type: str, data: Dict[str, Any]) -> str:
        """
        Format a progress event for display.

        Args:
            event_type: Type of event (start, thinking, tool_start, etc.)
            data: Event data dictionary

        Returns:
            Formatted string ready for printing
        """
        if event_type == "start":
            query = data.get("query", "")[:80]
            return f"{ProgressFormatter.ICONS['start']} Starting research: {query}..."

        elif event_type == "thinking":
            text = data.get("text", "")[:100]
            return f"  {ProgressFormatter.ICONS['thinking']} {text}..."

        elif event_type == "tool_start":
            tool_name = data.get("tool_name", "unknown")
            return f"  {ProgressFormatter.ICONS['tool_start']} Using: {tool_name}"

        elif event_type == "tool_result":
            tool_name = data.get("tool_name", "unknown")
            success = data.get("success", True)
            icon = ProgressFormatter.ICONS["tool_result_success" if success else "tool_result_failure"]
            status = "completed" if success else "failed"
            return f"  {icon} {tool_name} {status}"

        elif event_type == "result":
            return f"{ProgressFormatter.ICONS['result']} Research complete"

        elif event_type == "error":
            error = data.get("error", "Unknown error")
            return f"{ProgressFormatter.ICONS['error']} Error: {error}"

        return f"[{event_type}] {data}"


# Example usage
async def example_usage():
    """Example of how to use StreamingResearchWrapper."""

    # Custom progress callback
    async def my_progress_callback(event_type: str, data: Dict[str, Any]):
        formatted = ProgressFormatter.format_event(event_type, data)
        print(formatted)

    # Create wrapper
    wrapper = StreamingResearchWrapper(progress_callback=my_progress_callback)

    # Execute research with progress
    query = "What are the latest trends in AI agent frameworks?"
    results = await wrapper.research_with_progress(query, max_turns=50)

    # Get summary
    summary = wrapper.get_summary()
    print(f"\nSummary:")
    print(f"  Tools used: {', '.join(summary['tools_used'])}")
    print(f"  Findings: {summary['findings_count']}")
    print(f"  Duration: {summary['duration_sec']:.1f}s")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
