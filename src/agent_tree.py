"""
Main agent tree orchestration logic
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .context import Context
from .agent_node import AgentNode

logger = logging.getLogger(__name__)


def solve_problem(problem: str, max_depth: int = 3, use_tmp: bool = True, 
                 workspace_dir: str = "workspace") -> str:
    """Main entry point - solve a problem using agent tree
    
    Args:
        problem: The problem description to solve
        max_depth: Maximum recursion depth (default 3)
        use_tmp: Use tmp directory for workspace (default True)
        workspace_dir: Directory name for workspace (default "workspace")
    
    Returns:
        The final integrated solution
    """
    
    # Create workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine workspace location
    cwd = Path.cwd()
    if use_tmp and not (cwd.name.startswith("benchmark_") or cwd.parent.name == "tmp"):
        # Create in tmp directory
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        workspace = tmp_dir / f"agent_tree_{timestamp}"
    else:
        # Create in current directory or specified workspace
        if workspace_dir and not use_tmp:
            workspace_root = Path(workspace_dir)
            workspace_root.mkdir(exist_ok=True)
            workspace = workspace_root / f"agent_tree_{timestamp}"
        else:
            workspace = Path(f"agent_tree_{timestamp}")
    
    workspace.mkdir(exist_ok=True)
    
    # Initial problem is now documented in root/planning.md instead of problem.txt
    
    logger.info(f"Starting agent tree in {workspace}")
    
    # Track the total number of nodes created
    node_count = [0]  # Using list to make it mutable in nested function
    
    def solve_recursive(task: str, node_path: str, context: Optional[Context] = None, 
                       depth: int = 0, is_leaf: bool = False) -> str:
        """Recursive solver with context passing and leaf node support"""
        
        node_dir = workspace / node_path
        node = AgentNode(node_path, node_dir, depth)
        
        # Increment node count
        node_count[0] += 1
        current_node_number = node_count[0]
        
        node_type = " (LEAF)" if is_leaf else ""
        logger.info(f"{' ' * depth}→ {node_path}: {task[:60]}...{node_type} (Node #{current_node_number})")
        
        # Check if we've reached the 5-node limit
        if node_count[0] >= 5:
            logger.info(f"{' ' * depth}  Node limit (5) reached, solving directly")
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Check depth limit
        if depth >= max_depth:
            logger.info(f"{' ' * depth}  Max depth reached, solving directly")
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Decompose the problem (returns None for leaf nodes or simple problems)
        subtasks = node.decompose_problem(task, context, is_leaf)
        
        if subtasks is None:
            # Solve directly (either leaf node or problem assessed as simple)
            logger.info(f"{' ' * depth}  Solving directly" + (" (leaf node)" if is_leaf else ""))
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Complex - decompose and recurse
        logger.info(f"{' ' * depth}  Decomposing into {len(subtasks)} subtasks")
        
        # Extract just task descriptions for sibling context
        sibling_task_descriptions = [task_desc for task_desc, _ in subtasks]
        
        # Create context for children
        child_context = Context(
            root_problem=context.root_problem if context else problem,
            parent_task=task,
            parent_approach="",  # We removed approach from decompose_problem
            sibling_tasks=sibling_task_descriptions
        )
        
        solutions = []
        for i, (subtask_desc, is_simple) in enumerate(subtasks):
            child_path = f"{node_path}/sub{i+1}"
            solution = solve_recursive(subtask_desc, child_path, child_context, 
                                     depth + 1, is_leaf=is_simple)
            solutions.append((subtask_desc, solution))
        
        # Integrate solutions with context
        logger.info(f"{' ' * depth}  Integrating {len(solutions)} solutions")
        integrated = node.integrate_solutions(task, solutions, context)
        # Integration is now documented in planning.md
        return integrated
    
    # Start solving from root
    root_context = Context(root_problem=problem)
    final_solution = solve_recursive(problem, "root", root_context)
    
    # Create a final planning.md at workspace root that links to the root task
    final_planning = f"""# Agent Tree Execution

## Problem
{problem}

## Solution Tree
- [[root/planning|View complete solution tree]]

## Final Solution Summary
{final_solution[:500]}...

See [[root/planning]] for the complete hierarchical breakdown.
"""
    (workspace / "planning.md").write_text(final_planning)
    
    # Print summary
    print(f"\nAgent Tree Execution Summary")
    print("=" * 24)
    print(f"Problem: {problem[:60]}...")
    print(f"Workspace: {workspace}")
    print(f"Planning documentation saved to: {workspace}/planning.md")
    
    # Show tree structure
    print(f"\nTree structure:")
    _print_tree(workspace)
    
    return final_solution


def _print_tree(path: Path, prefix: str = "", is_last: bool = True):
    """Pretty print directory tree structure"""
    if path.name.startswith('.'):
        return
        
    print(prefix + path.name + "/")
    
    if path.is_dir():
        children = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
        for i, child in enumerate(children):
            extension = "  " if is_last else "│ "
            _print_tree(child, prefix + extension, i == len(children) - 1)