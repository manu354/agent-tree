"""
Markdown utilities for agent tree system
"""

import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def generate_problem_name(problem: str) -> str:
    """Generate a safe directory name from problem description"""
    # Take first few words and make them filesystem safe
    words = problem.lower().split()[:5]
    name = '_'.join(words)
    # Remove non-alphanumeric characters
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name[:50]  # Limit length


def is_problem_complex(markdown_path: str) -> bool:
    """Check if a problem markdown file indicates it's complex"""
    try:
        with open(markdown_path, 'r') as f:
            content = f.read().lower()
        
        # Find first occurrence of 'simple' or 'complex'
        simple_idx = content.find('simple')
        complex_idx = content.find('complex')
        
        # If neither found, default to simple
        if simple_idx == -1 and complex_idx == -1:
            return False
            
        # If only one found, use that
        if simple_idx == -1:
            return True
        if complex_idx == -1:
            return False
            
        # Both found, use whichever comes first
        return complex_idx < simple_idx
        
    except Exception as e:
        logger.warning(f"Could not read {markdown_path}: {e}")
        return False  # Default to simple


def find_subproblem_files(work_dir: Path, problem_name: str) -> List[str]:
    """Find all subproblem markdown files for a given problem"""
    subproblems_dir = work_dir / problem_name / "subproblems"
    
    if not subproblems_dir.exists():
        return []
        
    # Return list of created markdown files
    subproblem_files = list(subproblems_dir.glob("*.md"))
    return [str(f) for f in subproblem_files]