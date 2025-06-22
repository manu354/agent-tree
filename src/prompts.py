"""
Prompts for the agent tree system
"""

from typing import Optional
from .context import Context


def build_decomposition_prompt(
    problem: str, context: Optional[Context], parent_path: str, problem_name: str
) -> str:
    """Build the decomposition prompt for markdown-first approach"""
    context_prompt = context.to_prompt() if context else ""

    return f"""{context_prompt}You are decomposing this problem: {problem}

Create a markdown structure:

1. First, create a summary file at this path:
   `tasks/{parent_path}/{problem_name}.md`
2. Then create subproblem files at:
   `tasks/{parent_path}/{problem_name}/subproblems/<subproblem_name>1.md`
   `tasks/{parent_path}/{problem_name}/subproblems/<subproblem_name>2.md`
   etc.

Each subproblem file MUST follow this exact format:

# [Subproblem Name]

## Type
[simple or complex]

## Problem
[Description - MAX 100 WORDS]

## Possible Solution
[Approach - MAX 100 WORDS]

## Notes
[Context - MAX 100 WORDS]

Label as "simple" if it's a single-step task that can be solved directly.
Label as "complex" if it needs further decomposition.

Be critical of your decomposition - ensure you're solving the real problem and breaking it down meaningfully.

Use these tools to create the files:
- Write tool for creating each markdown file"""


def build_solution_prompt(problem: str, context: Optional[Context]) -> str:
    """Build prompt for solving a simple problem"""
    context_prompt = context.to_prompt() if context else ""
    
    return f"""{context_prompt}Solve this problem:
{problem}

Be critical and think for yourself - ensure your solution addresses the bigger picture and root goal.
Provide a concrete solution with implementation details."""



def build_integration_prompt(
    problem: str, solutions: list, context: Optional[Context]
) -> str:
    """Build prompt for integrating sub-solutions"""
    context_prompt = context.to_prompt() if context else ""

    solutions_text = "\n\n".join(
        [f"### {task}\nSolution: {solution}" for task, solution in solutions]
    )

    return f"""{context_prompt}Original problem: {problem}

Sub-solutions:
{solutions_text}

Be critical - evaluate whether these solutions truly address the root problem effectively.
Integrate these sub-solutions into a complete, cohesive solution."""

