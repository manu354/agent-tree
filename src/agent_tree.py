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
from .markdown_utils import generate_problem_name

logger = logging.getLogger(__name__)


def solve_problem(
    problem: str,
    max_depth: int = 3,
    use_tmp: bool = True,
    workspace_dir: str = "workspace",
) -> str:
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

    # Create tasks folder
    tasks_dir = workspace / "tasks"
    tasks_dir.mkdir(exist_ok=True)

    # Initial problem is now documented in root/planning.md instead of problem.txt

    logger.info(f"Starting agent tree in {workspace}")

    # Track the total number of nodes created
    node_count = [0]  # Using list to make it mutable in nested function

    def solve_recursive(
        task: str,
        node_path: str,
        context: Optional[Context] = None,
        depth: int = 0,
        is_leaf: bool = False,
        decompose_only: bool = False,
    ) -> str:
        """Recursive solver with context passing and leaf node support

        Args:
            task: The task to solve
            node_path: Path to the node directory
            context: Context from parent
            depth: Current recursion depth
            is_leaf: Whether this is marked as a leaf node
            decompose_only: If True, only create planning.md files without executing
        """

        # Use tasks folder for all nodes
        node_dir = workspace / "tasks" / node_path
        node = AgentNode(node_path, node_dir, depth)

        # Increment node count
        node_count[0] += 1
        current_node_number = node_count[0]

        node_type = " (LEAF)" if is_leaf else ""
        logger.info(
            f"{' ' * depth}→ {node_path}: {task[:60]}...{node_type} (Node #{current_node_number})"
        )

        # Check if we've reached the 5-node limit
        if node_count[0] >= 5:
            if decompose_only:
                logger.info(
                    f"{' ' * depth}  Node limit (5) reached, planning.md created"
                )
                # Still need to create planning.md even at node limit
                node.decompose_to_markdown(task, context)
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
                node.decompose_to_markdown(task, context)
                return ""
            logger.info(f"{' ' * depth}  Max depth reached, solving directly")
            solution = node.solve_simple(task, context)
            # Solution is now documented in planning.md
            return solution

        # During decomposition phase, create markdown files
        if decompose_only:
            # Determine parent path for markdown files relative to tasks folder
            parent_path = str(node_dir.relative_to(workspace / "tasks"))

            # Create markdown files for this problem
            subproblem_files = node.decompose_to_markdown(task, context, parent_path)

            # If no subproblem files were created, this is a simple problem
            if not subproblem_files:
                logger.info(f"{' ' * depth}  No decomposition - simple problem")
                # Create a simple problem markdown file
                problem_name = generate_problem_name(task)
                problem_file = node_dir / f"{problem_name}.md"
                content = f"""# {task}

## Type
simple

## Problem
{task}

## Possible Solution
This will be solved directly during execution.

## Notes
Leaf node - no further decomposition needed.
"""
                problem_file.write_text(content)
                return ""

            # Process each subproblem file
            logger.info(f"{' ' * depth}  Created {len(subproblem_files)} subproblems")

            # First collect all sibling tasks
            sibling_tasks = []
            for subproblem_file in sorted(subproblem_files):
                with open(subproblem_file, "r") as f:
                    content = f.read()
                title_match = re.search(r"# ([^\n]+)", content)
                if title_match:
                    sibling_tasks.append(title_match.group(1).strip())

            # Read subproblems and recursively decompose complex ones
            for i, subproblem_file in enumerate(sorted(subproblem_files)):
                if node.is_problem_complex(subproblem_file):
                    # Read problem description from markdown
                    with open(subproblem_file, "r") as f:
                        content = f.read()

                    # Extract problem description (between ## Problem and next ##)
                    problem_match = re.search(r"## Problem\s*\n([^#]+)", content)
                    if problem_match:
                        problem_desc = problem_match.group(1).strip()
                    else:
                        # Fallback to title
                        title_match = re.search(r"# ([^\n]+)", content)
                        problem_desc = (
                            title_match.group(1).strip()
                            if title_match
                            else "Unknown problem"
                        )



                    # Recurse on complex problems
                    subproblem_name = Path(subproblem_file).stem
                    child_path = f"{node_path}/{subproblem_name}"
                    child_context = Context(
                        root_problem=context.root_problem if context else problem,
                        parent_task=task,
                        parent_approach="",
                        sibling_tasks=sibling_tasks,
                    )
                    solve_recursive(
                        problem_desc,
                        child_path,
                        child_context,
                        depth + 1,
                        is_leaf=False,
                        decompose_only=True,
                    )

            return ""

        # Execution phase - solve simple problem or integrate solutions
        # Check if this is a leaf directory (no subdirectories with markdown files)
        subdirs = [d for d in node_dir.iterdir() if d.is_dir() and any(d.glob("*.md"))]

        if not subdirs:
            # Leaf node - solve directly
            logger.info(f"{' ' * depth}  Solving directly (leaf node)")
            solution = node.solve_simple(task, context)
            return solution

        # Non-leaf node - solutions should already exist from bottom-up execution
        # Read solutions from subdirectories
        solutions = []
        for subdir in sorted(subdirs):
            # Find the main problem file in the subdirectory
            md_files = list(subdir.glob("*.md"))
            if md_files:
                # Read the problem description
                with open(md_files[0], "r") as f:
                    content = f.read()
                    title_match = re.search(r"# ([^\n]+)", content)
                    subtask_desc = (
                        title_match.group(1).strip()
                        if title_match
                        else "Unknown subtask"
                    )

                # Read the solution if it exists
                solution_file = subdir / "solution.md"
                if solution_file.exists():
                    solution = solution_file.read_text()
                else:
                    solution = "(No solution found)"

                solutions.append((subtask_desc, solution))

        # Integrate solutions
        logger.info(f"{' ' * depth}  Integrating {len(solutions)} solutions")
        integrated = node.integrate_solutions(task, solutions, context)

        # Save integrated solution
        (node_dir / "solution.md").write_text(integrated)

        return integrated

    # Phase 1: Decompose only
    root_context = Context(root_problem=problem)
    logger.info("\n=== PHASE 1: DECOMPOSITION ===")
    solve_recursive(problem, "root", root_context, decompose_only=True)

    logger.info("\n" + "="*50)
    logger.info(f"Decomposition complete! Total nodes created: {node_count[0]}")
    logger.info(f"Workspace: {workspace}")
    logger.info("="*50 + "\n")

    # Show tree structure after decomposition
    print("\nDecomposition tree structure:")
    _print_tree(workspace)

    # Pause for user review
    user_input = input(
        "\nPress Enter to continue with execution (or type 'exit' to stop): "
    )
    if user_input.lower() == "exit":
        logger.info("Execution cancelled by user")
        return "Execution cancelled"

    # Phase 2: Execute from bottom-up
    logger.info("\n=== PHASE 2: EXECUTION ===")

    final_solution = execute_bottom_up(workspace)

    logger.info("\n" + "="*50)
    logger.info("Execution complete!")
    logger.info(f"Workspace: {workspace}")
    logger.info("="*50 + "\n")

    # Create a final planning.md at workspace root that links to the root task
    final_planning = f"""# Agent Tree Execution

## Problem
{problem}

## Solution Tree
- [[tasks/root/planning|View complete solution tree]]

## Final Solution Summary
{final_solution[:500]}...

See [[tasks/root/planning]] for the complete hierarchical breakdown.
"""
    (workspace / "planning.md").write_text(final_planning)

    # Show final tree structure
    print("\nFinal tree structure:")
    _print_tree(workspace)

    return final_solution


def execute_bottom_up(workspace: Path) -> str:
    """Execute all tasks bottom-up from markdown files"""
    logger.info("Starting bottom-up execution")

    # Build execution order (post-order traversal)
    execution_order = []

    def find_leaf_dirs(path: Path, depth: int = 0):
        """Find all directories that contain .md files"""
        # Check if this directory has any .md files
        md_files = list(path.glob("*.md"))
        if not md_files:
            return

        # Check if this has subdirectories with .md files (non-leaf)
        has_md_subdirs = False
        for item in path.iterdir():
            if item.is_dir() and list(item.glob("*.md")):
                has_md_subdirs = True
                find_leaf_dirs(item, depth + 1)

        # Add to execution order (post-order - children first)
        execution_order.append((path, depth, not has_md_subdirs))

    # Start from root in tasks folder
    find_leaf_dirs(workspace / "tasks" / "root")

    logger.info(f"Found {len(execution_order)} nodes to execute")

    # Execute in order
    for node_dir, depth, is_leaf in execution_order:
        # Find the main problem markdown file
        md_files = [f for f in node_dir.glob("*.md") if f.name != "solution.md"]
        if not md_files:
            continue

        problem_file = md_files[0]

        # Read problem from markdown
        content = problem_file.read_text()
        title_match = re.search(r"# ([^\\n]+)", content)
        task = title_match.group(1).strip() if title_match else "Unknown task"

        # Create context
        context = Context(root_problem=task)  # Simplified for now

        # Get relative path for logging
        rel_path = str(node_dir.relative_to(workspace / "tasks"))

        logger.info(f"{' ' * depth}→ Executing {rel_path}: {task[:60]}...")

        # Create node and execute
        node = AgentNode(rel_path, node_dir, depth)

        if is_leaf:
            # Solve simple problem
            solution = node.solve_simple(task, context)
            (node_dir / "solution.md").write_text(solution)
        else:
            # Integrate solutions from children
            solutions = []

            # Read solutions from subdirectories
            for subdir in sorted(node_dir.iterdir()):
                if subdir.is_dir() and (subdir / "solution.md").exists():
                    # Get task name from the problem file
                    sub_md_files = [
                        f for f in subdir.glob("*.md") if f.name != "solution.md"
                    ]
                    if sub_md_files:
                        sub_content = sub_md_files[0].read_text()
                        sub_title_match = re.search(r"# ([^\\n]+)", sub_content)
                        subtask = (
                            sub_title_match.group(1).strip()
                            if sub_title_match
                            else "Unknown subtask"
                        )
                    else:
                        subtask = subdir.name

                    solution = (subdir / "solution.md").read_text()
                    solutions.append((subtask, solution))

            # Integrate solutions
            integrated = node.integrate_solutions(task, solutions, context)
            (node_dir / "solution.md").write_text(integrated)

    # Return the root solution
    root_solution_file = workspace / "tasks" / "root" / "solution.md"
    if root_solution_file.exists():
        return root_solution_file.read_text()
    else:
        return "No solution generated"


def _print_tree(path: Path, prefix: str = "", is_last: bool = True):
    """Pretty print directory tree structure"""
    if path.name.startswith("."):
        return

    print(prefix + path.name + "/")

    if path.is_dir():
        children = sorted([p for p in path.iterdir() if not p.name.startswith(".")])
        for i, child in enumerate(children):
            extension = "  " if is_last else "│ "
            _print_tree(child, prefix + extension, i == len(children) - 1)
