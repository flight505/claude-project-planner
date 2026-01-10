#!/usr/bin/env python3
"""
Parallel Task Orchestrator for Claude Project Planner.

Executes independent tasks within phases in parallel while maintaining
context integrity between phases.

Usage:
    python parallel-orchestrator.py execute <project_folder> <phase_num>
    python parallel-orchestrator.py status <project_folder>
    python parallel-orchestrator.py merge-context <project_folder> <phase_num>

Phase Parallelization Groups:
    Phase 1: research-lookup + competitive-analysis (parallel)
             then market-research-reports, diagrams (sequential)
    Phase 3: feasibility + risk-assessment + service-cost-analysis (parallel)
             then diagrams (sequential)
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Phase configuration with parallelization groups
PHASE_CONFIG = {
    1: {
        "name": "Market Research",
        "parallel_groups": [
            {
                "group_id": "1.1",
                "type": "parallel",
                "tasks": [
                    {"skill": "research-lookup", "output": "market_data.md"},
                    {"skill": "competitive-analysis", "output": "competitive_analysis.md"},
                ],
            },
            {
                "group_id": "1.2",
                "type": "sequential",
                "tasks": [
                    {"skill": "market-research-reports", "output": "market_overview.md"},
                ],
                "depends_on": "1.1",
            },
            {
                "group_id": "1.3",
                "type": "sequential",
                "tasks": [
                    {"skill": "project-diagrams", "output": "diagrams/market_positioning.mmd"},
                ],
                "depends_on": "1.2",
            },
        ],
    },
    2: {
        "name": "Architecture Design",
        "parallel_groups": [
            {
                "group_id": "2.1",
                "type": "sequential",
                "tasks": [
                    {"skill": "architecture-research", "output": "architecture_document.md"},
                ],
            },
            {
                "group_id": "2.2",
                "type": "sequential",
                "tasks": [
                    {"skill": "building-blocks", "output": "building_blocks.md"},
                ],
                "depends_on": "2.1",
            },
            {
                "group_id": "2.3",
                "type": "sequential",
                "tasks": [
                    {"skill": "project-diagrams", "output": "diagrams/architecture.mmd"},
                ],
                "depends_on": "2.2",
            },
        ],
    },
    3: {
        "name": "Feasibility & Costs",
        "parallel_groups": [
            {
                "group_id": "3.1",
                "type": "parallel",
                "tasks": [
                    {"skill": "feasibility-analysis", "output": "feasibility_analysis.md"},
                    {"skill": "risk-assessment", "output": "risk_assessment.md"},
                    {"skill": "service-cost-analysis", "output": "service_cost_analysis.md"},
                ],
            },
            {
                "group_id": "3.2",
                "type": "sequential",
                "tasks": [
                    {"skill": "project-diagrams", "output": "diagrams/cost_breakdown.mmd"},
                ],
                "depends_on": "3.1",
            },
        ],
    },
    4: {
        "name": "Implementation Planning",
        "parallel_groups": [
            {
                "group_id": "4.1",
                "type": "sequential",
                "tasks": [
                    {"skill": "sprint-planning", "output": "sprint_plan.md"},
                ],
            },
            {
                "group_id": "4.2",
                "type": "sequential",
                "tasks": [
                    {"skill": "project-diagrams", "output": "diagrams/timeline.mmd"},
                ],
                "depends_on": "4.1",
            },
        ],
    },
    5: {
        "name": "Go-to-Market",
        "parallel_groups": [
            {
                "group_id": "5.1",
                "type": "sequential",
                "tasks": [
                    {"skill": "marketing-campaign", "output": "marketing_campaign.md"},
                ],
            },
            {
                "group_id": "5.2",
                "type": "sequential",
                "tasks": [
                    {"skill": "project-diagrams", "output": "diagrams/campaign_timeline.mmd"},
                ],
                "depends_on": "5.1",
            },
        ],
    },
    6: {
        "name": "Review & Synthesis",
        "parallel_groups": [
            {
                "group_id": "6.1",
                "type": "sequential",
                "tasks": [
                    {"skill": "plan-review", "output": "plan_review.md"},
                ],
            },
        ],
    },
}

# Key findings extraction patterns for context sharing
KEY_FINDINGS_PATTERNS = {
    "research-lookup": [
        r"(?:market size|TAM|SAM|SOM)[:\s]+(\$?[\d.]+\s*(?:billion|million|B|M))",
        r"(?:growth rate|CAGR)[:\s]+([\d.]+%)",
        r"(?:key trend|major trend)[:\s]+(.+?)(?:\n|$)",
    ],
    "competitive-analysis": [
        r"(?:competitor|key player)[:\s]+([^,\n]+)",
        r"(?:market share)[:\s]+([\d.]+%)",
        r"(?:differentiator|gap)[:\s]+(.+?)(?:\n|$)",
    ],
    "architecture-research": [
        r"(?:tech stack|technology)[:\s]+([^,\n]+)",
        r"(?:pattern|architecture style)[:\s]+([^,\n]+)",
        r"(?:database|data store)[:\s]+([^,\n]+)",
    ],
    "building-blocks": [
        r"(?:component|block)[:\s]+([^,\n]+)",
        r"(?:dependency)[:\s]+([^,\n]+)",
        r"(?:estimate|hours)[:\s]+([\d]+)",
    ],
    "feasibility-analysis": [
        r"(?:viability|feasibility score)[:\s]+([\d.]+(?:/10)?)",
        r"(?:blocker|concern)[:\s]+(.+?)(?:\n|$)",
        r"(?:recommendation)[:\s]+(.+?)(?:\n|$)",
    ],
    "risk-assessment": [
        r"(?:risk|threat)[:\s]+([^,\n]+)",
        r"(?:severity|impact)[:\s]+([^,\n]+)",
        r"(?:mitigation)[:\s]+(.+?)(?:\n|$)",
    ],
    "service-cost-analysis": [
        r"(?:monthly cost|total cost)[:\s]+(\$?[\d,]+)",
        r"(?:service|provider)[:\s]+([^,\n]+)",
        r"(?:breakdown)[:\s]+(.+?)(?:\n|$)",
    ],
    "sprint-planning": [
        r"(?:sprint|iteration)[:\s]+([\d]+)",
        r"(?:MVP|milestone)[:\s]+([^,\n]+)",
        r"(?:velocity|points)[:\s]+([\d]+)",
    ],
}


class ParallelOrchestrator:
    """Orchestrates parallel task execution within planning phases."""

    def __init__(self, project_folder: Path):
        self.project_folder = Path(project_folder)
        self.context_dir = self.project_folder / ".context"
        self.state_file = self.project_folder / ".parallel_state.json"
        self._ensure_context_dir()

    def _ensure_context_dir(self) -> None:
        """Create context directory if it doesn't exist."""
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> dict:
        """Load parallel execution state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "created_at": datetime.now().isoformat(),
            "project_folder": str(self.project_folder),
            "phases": {},
        }

    def _save_state(self, state: dict) -> None:
        """Save parallel execution state."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_phase_input_context(self, phase_num: int) -> str:
        """Get input context for a phase from previous phase outputs."""
        context_parts = []

        # Gather outputs from all previous phases
        for prev_phase in range(1, phase_num):
            output_file = self.context_dir / f"phase{prev_phase}_output.md"
            if output_file.exists():
                with open(output_file) as f:
                    context_parts.append(f"## Phase {prev_phase} Context\n\n{f.read()}")

        return "\n\n---\n\n".join(context_parts)

    def save_phase_input_context(self, phase_num: int) -> Path:
        """Save input context for a phase."""
        context = self.get_phase_input_context(phase_num)
        input_file = self.context_dir / f"phase{phase_num}_input.md"

        with open(input_file, "w") as f:
            f.write(f"# Phase {phase_num} Input Context\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(context if context else "*No prior context available*")

        return input_file

    def extract_key_findings(self, skill: str, content: str) -> list[str]:
        """Extract key findings from task output using skill-specific patterns."""
        import re

        findings = []
        patterns = KEY_FINDINGS_PATTERNS.get(skill, [])

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches[:3]:  # Limit to top 3 matches per pattern
                if isinstance(match, tuple):
                    findings.append(match[0].strip())
                else:
                    findings.append(match.strip())

        return findings

    def merge_task_outputs(self, phase_num: int, task_results: list[dict]) -> Path:
        """Merge outputs from parallel tasks into phase output context."""
        output_parts = [f"# Phase {phase_num} Output Context\n"]
        output_parts.append(f"Generated: {datetime.now().isoformat()}\n")
        output_parts.append(f"Tasks completed: {len(task_results)}\n\n")

        for result in task_results:
            skill = result.get("skill", "unknown")
            status = result.get("status", "unknown")
            output_file = result.get("output_file")
            findings = result.get("key_findings", [])

            output_parts.append(f"## {skill}\n")
            output_parts.append(f"Status: {status}\n")

            if output_file and Path(output_file).exists():
                output_parts.append(f"Output: {output_file}\n")

            if findings:
                output_parts.append("\n### Key Findings\n")
                for finding in findings:
                    output_parts.append(f"- {finding}\n")

            output_parts.append("\n")

        output_file = self.context_dir / f"phase{phase_num}_output.md"
        with open(output_file, "w") as f:
            f.write("".join(output_parts))

        return output_file

    def execute_task(self, task: dict, phase_num: int, group_id: str) -> dict:
        """Execute a single task and return results."""
        skill = task["skill"]
        output = task["output"]
        start_time = time.time()

        result = {
            "skill": skill,
            "output": output,
            "group_id": group_id,
            "phase_num": phase_num,
            "started_at": datetime.now().isoformat(),
            "status": "pending",
            "key_findings": [],
            "error": None,
        }

        # Determine output path
        phase_dir_map = {
            1: "01_market_research",
            2: "02_architecture",
            3: "03_feasibility",
            4: "04_implementation",
            5: "05_go_to_market",
            6: "06_review",
        }
        phase_dir = self.project_folder / phase_dir_map.get(phase_num, f"phase{phase_num}")
        output_path = phase_dir / output

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result["output_file"] = str(output_path)

        # For now, we just mark the task as ready for execution
        # The actual skill execution is done by Claude Code, not this script
        # This script orchestrates and tracks the parallel execution

        result["status"] = "ready"
        result["duration_seconds"] = time.time() - start_time

        return result

    def execute_parallel_group(self, group: dict, phase_num: int) -> list[dict]:
        """Execute a parallel group of tasks."""
        tasks = group["tasks"]
        group_id = group["group_id"]
        group_type = group["type"]

        results = []

        if group_type == "parallel" and len(tasks) > 1:
            # Execute tasks in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
                futures = {
                    executor.submit(self.execute_task, task, phase_num, group_id): task
                    for task in tasks
                }

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
        else:
            # Execute sequentially
            for task in tasks:
                result = self.execute_task(task, phase_num, group_id)
                results.append(result)

        return results

    def execute_phase(self, phase_num: int) -> dict:
        """Execute all task groups in a phase respecting dependencies."""
        if phase_num not in PHASE_CONFIG:
            return {"error": f"Unknown phase: {phase_num}"}

        phase = PHASE_CONFIG[phase_num]
        state = self._load_state()

        # Initialize phase state
        phase_state = {
            "name": phase["name"],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "groups": {},
            "all_results": [],
        }

        # Save input context from previous phases
        input_context_file = self.save_phase_input_context(phase_num)
        phase_state["input_context"] = str(input_context_file)

        completed_groups: set[str] = set()
        all_results: list[dict] = []

        # Process groups in order, respecting dependencies
        for group in phase["parallel_groups"]:
            group_id = group["group_id"]
            depends_on = group.get("depends_on")

            # Check if dependency is satisfied
            if depends_on and depends_on not in completed_groups:
                phase_state["groups"][group_id] = {
                    "status": "blocked",
                    "blocked_by": depends_on,
                }
                continue

            # Execute the group
            group_results = self.execute_parallel_group(group, phase_num)
            all_results.extend(group_results)

            phase_state["groups"][group_id] = {
                "type": group["type"],
                "status": "completed",
                "tasks": group_results,
            }
            completed_groups.add(group_id)

        # Extract key findings from completed task outputs
        for result in all_results:
            output_file = result.get("output_file")
            if output_file and Path(output_file).exists():
                with open(output_file) as f:
                    content = f.read()
                result["key_findings"] = self.extract_key_findings(result["skill"], content)

        # Merge outputs into phase context
        output_context_file = self.merge_task_outputs(phase_num, all_results)
        phase_state["output_context"] = str(output_context_file)

        phase_state["completed_at"] = datetime.now().isoformat()
        phase_state["status"] = "completed"
        phase_state["all_results"] = all_results

        # Save state
        state["phases"][str(phase_num)] = phase_state
        self._save_state(state)

        return phase_state

    def get_status(self) -> dict:
        """Get current orchestration status."""
        state = self._load_state()

        status = {
            "project_folder": str(self.project_folder),
            "context_dir": str(self.context_dir),
            "phases": {},
        }

        for phase_num, config in PHASE_CONFIG.items():
            phase_key = str(phase_num)
            phase_status = state.get("phases", {}).get(phase_key, {})

            # Calculate parallelization info
            parallel_count = sum(
                1 for g in config["parallel_groups"] if g["type"] == "parallel"
            )
            total_tasks = sum(len(g["tasks"]) for g in config["parallel_groups"])

            status["phases"][phase_key] = {
                "name": config["name"],
                "total_tasks": total_tasks,
                "parallel_groups": parallel_count,
                "status": phase_status.get("status", "pending"),
                "started_at": phase_status.get("started_at"),
                "completed_at": phase_status.get("completed_at"),
            }

        return status

    def get_phase_execution_plan(self, phase_num: int) -> dict:
        """Get execution plan for a specific phase (for Claude Code to follow)."""
        if phase_num not in PHASE_CONFIG:
            return {"error": f"Unknown phase: {phase_num}"}

        config = PHASE_CONFIG[phase_num]
        plan = {
            "phase_num": phase_num,
            "name": config["name"],
            "groups": [],
            "total_tasks": 0,
            "parallel_tasks": 0,
        }

        for group in config["parallel_groups"]:
            group_info = {
                "group_id": group["group_id"],
                "type": group["type"],
                "depends_on": group.get("depends_on"),
                "tasks": [],
            }

            for task in group["tasks"]:
                group_info["tasks"].append({
                    "skill": task["skill"],
                    "output": task["output"],
                })
                plan["total_tasks"] += 1
                if group["type"] == "parallel":
                    plan["parallel_tasks"] += 1

            plan["groups"].append(group_info)

        return plan


def main():
    parser = argparse.ArgumentParser(
        description="Parallel Task Orchestrator for Claude Project Planner"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a phase with parallelization")
    execute_parser.add_argument("project_folder", help="Project folder path")
    execute_parser.add_argument("phase_num", type=int, help="Phase number to execute")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get orchestration status")
    status_parser.add_argument("project_folder", help="Project folder path")

    # Plan command - get execution plan for Claude Code
    plan_parser = subparsers.add_parser("plan", help="Get execution plan for a phase")
    plan_parser.add_argument("project_folder", help="Project folder path")
    plan_parser.add_argument("phase_num", type=int, help="Phase number")

    # Merge context command
    merge_parser = subparsers.add_parser("merge-context", help="Merge task outputs into phase context")
    merge_parser.add_argument("project_folder", help="Project folder path")
    merge_parser.add_argument("phase_num", type=int, help="Phase number")

    # Input context command
    input_parser = subparsers.add_parser("input-context", help="Get input context for a phase")
    input_parser.add_argument("project_folder", help="Project folder path")
    input_parser.add_argument("phase_num", type=int, help="Phase number")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    orchestrator = ParallelOrchestrator(Path(args.project_folder))

    if args.command == "execute":
        result = orchestrator.execute_phase(args.phase_num)
        print(json.dumps(result, indent=2))

    elif args.command == "status":
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "plan":
        plan = orchestrator.get_phase_execution_plan(args.phase_num)
        print(json.dumps(plan, indent=2))

    elif args.command == "merge-context":
        # Load existing results from state and merge
        state = orchestrator._load_state()
        phase_state = state.get("phases", {}).get(str(args.phase_num), {})
        results = phase_state.get("all_results", [])
        output_file = orchestrator.merge_task_outputs(args.phase_num, results)
        print(f"Context merged: {output_file}")

    elif args.command == "input-context":
        input_file = orchestrator.save_phase_input_context(args.phase_num)
        print(f"Input context saved: {input_file}")
        print("\n--- Content ---\n")
        with open(input_file) as f:
            print(f.read())


if __name__ == "__main__":
    main()
