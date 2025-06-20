"""
Main agent tree orchestration logic
"""

import logging
import re
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
                       depth: int = 0, is_leaf: bool = False, decompose_only: bool = False) -> str:
        """Recursive solver with context passing and leaf node support
        
        Args:
            task: The task to solve
            node_path: Path to the node directory
            context: Context from parent
            depth: Current recursion depth
            is_leaf: Whether this is marked as a leaf node
            decompose_only: If True, only create planning.md files without executing
        """
        
        node_dir = workspace / node_path
        node = AgentNode(node_path, node_dir, depth)
        
        # Increment node count
        node_count[0] += 1
        current_node_number = node_count[0]
        
        node_type = " (LEAF)" if is_leaf else ""
        logger.info(f"{' ' * depth}→ {node_path}: {task[:60]}...{node_type} (Node #{current_node_number})")
        
        # Check if we've reached the 5-node limit
        if node_count[0] >= 5:
            if decompose_only:
                logger.info(f"{' ' * depth}  Node limit (5) reached, planning.md created")
                # Still need to create planning.md even at node limit
                node.decompose_problem(task, context, is_leaf=True)
                return ""
            logger.info(f"{' ' * depth}  Node limit (5) reached, solving directly")
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Check depth limit
        if depth >= max_depth:
            if decompose_only:
                logger.info(f"{' ' * depth}  Max depth reached, planning.md created")
                # Still need to create planning.md even at max depth
                node.decompose_problem(task, context, is_leaf=True)
                return ""
            logger.info(f"{' ' * depth}  Max depth reached, solving directly")
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Decompose the problem (returns None for leaf nodes or simple problems)
        subtasks = node.decompose_problem(task, context, is_leaf)
        
        if subtasks is None:
            # Solve directly (either leaf node or problem assessed as simple)
            if decompose_only:
                logger.info(f"{' ' * depth}  Creating planning.md for leaf node")
                # Create a basic planning.md for leaf nodes during decomposition
                planning_content = f"""# Task: {task}

## Status
This is a leaf node - will be solved directly during execution phase.

## Context
{context.to_prompt() if context else 'No parent context'}
"""
                (node.work_dir / "planning.md").write_text(planning_content)
                return ""  # Return empty string during decomposition phase
            logger.info(f"{' ' * depth}  Solving directly" + (" (leaf node)" if is_leaf else ""))
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution
        
        # Complex - decompose and recurse
        logger.info(f"{' ' * depth}  Decomposing into {len(subtasks)} subtasks")
        
        # During decomposition phase, create planning.md with the decomposition plan
        if decompose_only:
            # Create planning.md with links to subtasks
            subtask_links = []
            for i, (subtask_desc, is_simple) in enumerate(subtasks):
                child_path = f"sub{i+1}"
                leaf_marker = " (leaf)" if is_simple else ""
                subtask_links.append(f"- [[{child_path}/planning|{subtask_desc}]]{leaf_marker}")
            
            planning_content = f"""# Task: {task}

## Decomposition Plan
{chr(10).join(subtask_links)}

## Context
{context.to_prompt() if context else 'No parent context'}
"""
            (node.work_dir / "planning.md").write_text(planning_content)
        
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
                                     depth + 1, is_leaf=is_simple, decompose_only=decompose_only)
            solutions.append((subtask_desc, solution))
        
        # If decompose_only, we're done after creating all planning.md files
        if decompose_only:
            logger.info(f"{' ' * depth}  Decomposition complete for {node_path}")
            return ""
        
        # Integrate solutions with context
        logger.info(f"{' ' * depth}  Integrating {len(solutions)} solutions")
        integrated = node.integrate_solutions(task, solutions, context)
        # Integration is now documented in planning.md
        return integrated
    
    # Phase 1: Decompose only
    root_context = Context(root_problem=problem)
    logger.info("\n=== PHASE 1: DECOMPOSITION ===")
    solve_recursive(problem, "root", root_context, decompose_only=True)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Decomposition complete! Total nodes created: {node_count[0]}")
    logger.info(f"Workspace: {workspace}")
    logger.info(f"{'='*50}\n")
    
    # Show tree structure after decomposition
    print(f"\nDecomposition tree structure:")
    _print_tree(workspace)
    
    # Pause for user review
    user_input = input("\nPress Enter to continue with execution (or type 'exit' to stop): ")
    if user_input.lower() == 'exit':
        logger.info("Execution cancelled by user")
        return "Execution cancelled"
    
    # Phase 2: Execute from filesystem
    logger.info("\n=== PHASE 2: EXECUTION ===")
    # Reset node count for execution phase
    execution_node_count = [0]
    
    def execute_from_filesystem(node_path: str, depth: int = 0) -> str:
        """Execute tasks from planning.md files in the filesystem"""
        nonlocal execution_node_count
        execution_node_count[0] += 1
        
        node_dir = workspace / node_path
        planning_file = node_dir / "planning.md"
        
        if not planning_file.exists():
            logger.error(f"No planning.md found at {planning_file}")
            return ""
        
        # Read planning.md to get task
        content = planning_file.read_text()
        task_match = re.search(r'# Task: (.+)', content)
        if not task_match:
            logger.error(f"No task found in {planning_file}")
            return ""
        
        task = task_match.group(1)
        logger.info(f"{' ' * depth}→ Executing {node_path}: {task[:60]}...")
        
        # Check if this is a leaf node (no subdirectories)
        subdirs = [d for d in node_dir.iterdir() if d.is_dir() and d.name.startswith('sub')]
        
        if not subdirs:
            # Leaf node - execute directly
            node = AgentNode(node_path, node_dir, depth)
            # The solve_simple will read from planning.md and execute
            solution = node.solve_simple(task, root_context)
            return solution
        
        # Non-leaf node - execute children first
        solutions = []
        for subdir in sorted(subdirs):
            child_path = f"{node_path}/{subdir.name}"
            solution = execute_from_filesystem(child_path, depth + 1)
            # Get the actual subtask from the child's planning.md
            child_planning = (workspace / child_path / "planning.md").read_text()
            child_task_match = re.search(r'# Task: (.+)', child_planning)
            child_task = child_task_match.group(1) if child_task_match else "Unknown task"
            solutions.append((child_task, solution))
        
        # Integrate solutions
        logger.info(f"{' ' * depth}  Integrating {len(solutions)} solutions")
        node = AgentNode(node_path, node_dir, depth)
        integrated = node.integrate_solutions(task, solutions, root_context)
        return integrated
    
    final_solution = execute_from_filesystem("root")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Execution complete! Nodes processed: {execution_node_count[0]}")
    logger.info(f"Workspace: {workspace}")
    logger.info(f"{'='*50}\n")
    
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
    
    # Show final tree structure
    print(f"\nFinal tree structure:")
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