"""
Agent node implementation for hierarchical problem solving
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from .context import Context
from .claude_client import ClaudeClient
from .markdown_utils import generate_problem_name, is_problem_complex, find_subproblem_files
from .prompts import build_decomposition_prompt, build_solution_prompt, build_integration_prompt

logger = logging.getLogger(__name__)


class AgentNode:
    """Minimal agent node using claude CLI"""
    
    def __init__(self, name: str, work_dir: Path, depth: int = 0):
        self.name = name
        self.work_dir = work_dir
        self.depth = depth
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.claude = ClaudeClient(work_dir, name, depth)
        
    def decompose_to_markdown(self, problem: str, context: Optional[Context] = None, 
                            parent_path: str = ".") -> List[str]:
        """Decompose a problem by creating markdown files
        
        Returns:
            List of created subproblem file paths
        """
        # Generate problem name for directory structure
        problem_name = generate_problem_name(problem)
        
        # Build decomposition prompt with parent path
        prompt = build_decomposition_prompt(problem, context, parent_path, problem_name)
        
        # Run Claude to create markdown files
        logger.info("Running Claude to create markdown structure")
        response = self.claude.run_prompt(prompt)
        
        # Find all created subproblem files
        return find_subproblem_files(self.work_dir, problem_name)

    
    def solve_simple(self, problem: str, context: Optional[Context] = None) -> str:
        """Use claude to solve a simple problem"""
        prompt = build_solution_prompt(problem, context)
        return self.claude.run_prompt(prompt)
    
    def integrate_solutions(self, problem: str, solutions: List[Tuple[str, str]], 
                          context: Optional[Context] = None) -> str:
        """Use claude to integrate sub-solutions"""
        prompt = build_integration_prompt(problem, solutions, context)
        return self.claude.run_prompt(prompt)
    
    
    def is_problem_complex(self, markdown_path: str) -> bool:
        """Check if a problem markdown file indicates it's complex"""
        return is_problem_complex(markdown_path)
    
