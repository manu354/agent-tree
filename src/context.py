"""
Context management for agent tree nodes
"""

from typing import List

import re
from pathlib import Path


def build_tree_structure(workspace_path: Path, current_node_path: str = "") -> str:
    """Build a string representation of the current tree structure with summaries"""
    tree_lines = []
    
    def extract_problem_summary(md_file: Path) -> str:
        """Extract a one-sentence summary from a markdown file"""
        try:
            content = md_file.read_text()
            # First try to extract from ## Summary section
            summary_match = re.search(r'## Summary\s*\n([^\n#]+)', content)
            if summary_match:
                summary = summary_match.group(1).strip()
                # Return the full summary (should already be concise)
                return summary
            # Fallback to ## Problem section for backward compatibility
            problem_match = re.search(r'## Problem\s*\n([^\n#]+)', content)
            if problem_match:
                summary = problem_match.group(1).strip()
                # Take first sentence
                first_sentence = summary.split('.')[0].strip()
                return first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
            # Fallback to title
            title_match = re.search(r'# ([^\n]+)', content)
            if title_match:
                return title_match.group(1).strip()
            return "No description"
        except:
            return "Cannot read"
    
    def traverse_dir(path: Path, prefix: str = "", node_path: str = ""):
        """Recursively traverse directory and build tree representation"""
        # Skip non-task directories
        if path.name == "subproblems":
            # Process subproblem files
            md_files = sorted(path.glob("*.md"))
            for md_file in md_files:
                summary = extract_problem_summary(md_file)
                # Check if this is the current node
                full_path = f"{node_path}/{md_file.stem}" if node_path else md_file.stem
                is_current = current_node_path and full_path == current_node_path
                marker = " <- YOU ARE HERE" if is_current else ""
                tree_lines.append(f"{prefix}- {md_file.stem}: {summary}{marker}")
        else:
            # Process directories that might contain tasks
            subdirs = sorted([d for d in path.iterdir() if d.is_dir() and d.name != "subproblems"])
            for subdir in subdirs:
                # Check if this directory has a corresponding .md file
                md_file = path / f"{subdir.name}.md"
                if md_file.exists():
                    summary = extract_problem_summary(md_file)
                else:
                    summary = "No description"
                
                # Check if this is the current node
                full_path = f"{node_path}/{subdir.name}" if node_path else subdir.name
                is_current = current_node_path and full_path == current_node_path
                marker = " <- YOU ARE HERE" if is_current else ""
                tree_lines.append(f"{prefix}{subdir.name}/: {summary}{marker}")
                
                # Recursively process subdirectory
                new_node_path = f"{node_path}/{subdir.name}" if node_path else subdir.name
                traverse_dir(subdir, prefix + "  ", new_node_path)
    
    tasks_dir = workspace_path / "tasks"
    if tasks_dir.exists():
        tree_lines.append("=== PROBLEM TREE STRUCTURE ===")
        traverse_dir(tasks_dir, "", "")
        tree_lines.append("==============================")
    
    return "\n".join(tree_lines)

class Context:
    """Context passed down the tree"""

    def __init__(
        self,
        root_problem: str,
        parent_task: str = "",
        parent_approach: str = "",
        sibling_tasks: List[str] = None,
        tree_structure: str = "",
    ):
        self.root_problem = root_problem
        self.parent_task = parent_task
        self.parent_approach = parent_approach
        self.sibling_tasks = sibling_tasks or []
        self.tree_structure = tree_structure

    def to_prompt(self) -> str:
        """Convert to prompt text"""
        prompt_parts = []
        
        # Add tree structure if available
        if self.tree_structure:
            prompt_parts.append(self.tree_structure)
        
        # Add ancestor context if not root
        if self.parent_task:
            siblings = "\n".join(f"  - {task}" for task in self.sibling_tasks)
            prompt_parts.append(f"""=== CONTEXT FROM ANCESTORS ===
Root Goal: {self.root_problem}
Parent Task: {self.parent_task}
Parent's Approach: {self.parent_approach}
Sibling Tasks:
{siblings}
===========================""")
        
        if prompt_parts:
            return "\n\n".join(prompt_parts) + "\n\n"
        return ""