"""
Solve module for agent-tree system.
Solves a decomposed task tree by working bottom-up with dependency resolution.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Set, Optional, Tuple


# Global state
solved_tasks: Set[str] = set()
workspace_root: Optional[Path] = None


def get_dependent(task_file: str) -> List[str]:
    """
    Read a markdown file and extract dependent tasks.
    
    Args:
        task_file: Path to the markdown file
        
    Returns:
        List of dependent file paths
    """
    try:
        with open(task_file, 'r') as f:
            content = f.read()
        
        # Find ### Dependents section
        dependent_match = re.search(r'### Dependents\s*\n(.*?)(?:\n##|\n#|\Z)', content, re.DOTALL)
        if not dependent_match:
            return []
        
        dependent_section = dependent_match.group(1)
        
        # Extract markdown links [Task Name](path/to/task.md)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', dependent_section)
        
        # Resolve relative paths to absolute paths
        task_dir = Path(task_file).parent
        dependent_files = []
        for _, path in links:
            # Resolve relative path from task file location
            abs_path = (task_dir / path).resolve()
            dependent_files.append(str(abs_path))
        
        return dependent_files
    except Exception as e:
        print(f"Error reading dependents from {task_file}: {e}")
        return []


def has_child_or_dependency(task_file: str) -> bool:
    """
    Check if a task has children or dependencies.
    
    Args:
        task_file: Path to the task file
        
    Returns:
        True if task has children directory or dependents
    """
    # Check for children directory
    task_path = Path(task_file)
    task_name = task_path.stem
    children_dir = task_path.parent / f"{task_name}_children"
    
    if children_dir.exists() and children_dir.is_dir():
        # Check if there are any .md files in children directory
        md_files = list(children_dir.glob("*.md"))
        if md_files:
            return True
    
    # Check for dependents
    dependents = get_dependent(task_file)
    if dependents:
        return True
    
    return False


def extract_name(task_file: str) -> str:
    """Extract the base name from a task file path."""
    return Path(task_file).stem


def generate_tree_with_summaries(root_path: Path, current_task: str) -> str:
    """
    Generate a tree view of all tasks with their summaries.
    
    Args:
        root_path: Root workspace path
        current_task: Path to current task to mark with [YOU ARE HERE]
        
    Returns:
        Formatted tree string
    """
    lines = []
    current_task_path = Path(current_task).resolve()
    
    def walk_tree(path: Path, prefix: str = "", is_last: bool = True):
        """Recursively walk the tree and build visualization."""
        # Skip non-directories and hidden files
        if path.name.startswith('.'):
            return
        
        # Get all .md files in this directory (excluding _plan.md files)
        md_files = [f for f in path.glob("*.md") if not f.name.endswith("_plan.md")]
        
        # Process each .md file
        for i, md_file in enumerate(sorted(md_files)):
            is_last_file = (i == len(md_files) - 1)
            
            # Read first line as summary
            try:
                with open(md_file, 'r') as f:
                    first_line = f.readline().strip()
                    # Remove # prefix if present
                    summary = first_line.lstrip('#').strip()
                    if len(summary) > 60:
                        summary = summary[:57] + "..."
            except:
                summary = "Unable to read summary"
            
            # Check if this is the current task
            is_current = md_file.resolve() == current_task_path
            marker = " [YOU ARE HERE]" if is_current else ""
            
            # Build the line
            connector = "└── " if is_last_file else "├── "
            line = f"{prefix}{connector}{md_file.name} - \"{summary}\"{marker}"
            lines.append(line)
            
            # Check for children directory
            children_dir = md_file.parent / f"{md_file.stem}_children"
            if children_dir.exists() and children_dir.is_dir():
                # Determine new prefix for children
                extension = "    " if is_last_file else "│   "
                walk_tree(children_dir, prefix + extension)
    
    # Start from root
    lines.append(f"{root_path.name}/")
    walk_tree(root_path, "")
    
    return "\n".join(lines)


def solve_prompt(task_file: str, tree_context: str) -> str:
    """
    Create a prompt for solving a specific task.
    
    Args:
        task_file: Path to the task file
        tree_context: Tree visualization showing task context
        
    Returns:
        Formatted prompt string
    """
    # Read task content
    with open(task_file, 'r') as f:
        task_content = f.read()
    
    # Determine plan file path
    task_path = Path(task_file)
    plan_file = task_path.parent / f"{task_path.stem}_plan.md"
    
    prompt = f"""You are solving a specific task within a larger system.

Here's where your task fits in the overall structure:
{tree_context}

Current task file: {task_file}
Task content:
{task_content}

Related plan file: {plan_file}

Instructions:
1. Read the task carefully
2. You can read other task files if you need context about dependencies or integration
3. Implement the solution by creating/editing necessary code files
4. Update the plan file with:
   - Progress notes
   - Any decisions made
   - Summary of what was implemented
   
Focus on solving just this specific task. Other tasks in the tree will be handled separately."""
    
    return prompt


def agent(prompt: str, working_dir: str) -> str:
    """
    Call Claude CLI with the given prompt.
    
    Args:
        prompt: The prompt to send to Claude
        working_dir: Directory to run Claude in
        
    Returns:
        Claude's response
    """
    # Use Claude CLI in headless mode
    cmd = ["claude", "--dangerously-skip-permissions", "-p", prompt]
    
    print(f"\n{'='*80}")
    print(f"🌳 CLAUDE CALL - Working Directory: {working_dir}")
    print(f"{'='*80}")
    print("📝 INPUT PROMPT:")
    print("-" * 40)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 40)
    
    print("\n🚀 Executing Claude...")
    print("⏳ Running headless, please wait...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Claude failed: {result.stderr}")
            return f"Error: {result.stderr}"
        
        print("✅ Claude completed successfully")
        print(f"{'='*80}\n")
        
        return result.stdout
        
    except subprocess.TimeoutExpired:
        print("❌ Claude timed out after 10 minutes")
        return "Error: Claude timed out"
    except Exception as e:
        print(f"❌ Claude error: {e}")
        return f"Error: {str(e)}"


def solve(task_file: str) -> None:
    """
    Solve a task tree starting from the given task file.
    
    Args:
        task_file: Path to the root .md task file
    """
    global workspace_root
    
    # Set workspace root if not already set
    if workspace_root is None:
        # Find workspace root by looking for parent with no more .md files above
        current = Path(task_file).parent
        while current.parent != current:
            parent_md_files = list(current.parent.glob("*.md"))
            if not parent_md_files:
                workspace_root = current
                break
            current = current.parent
        
        # Fallback to task file's parent
        if workspace_root is None:
            workspace_root = Path(task_file).parent
    
    # Skip if already solved
    if task_file in solved_tasks:
        return
    
    print(f"\n🔍 Processing: {task_file}")
    
    # Process dependencies first
    dependents = get_dependent(task_file)
    for dependent in dependents:
        if dependent not in solved_tasks:
            print(f"  → Solving dependency: {dependent}")
            solve(dependent)
    
    # Process children (if any)
    task_path = Path(task_file)
    children_dir = task_path.parent / f"{extract_name(task_file)}_children"
    
    if children_dir.exists() and children_dir.is_dir():
        child_files = [str(f) for f in children_dir.glob("*.md") if not f.name.endswith("_plan.md")]
        
        for child_file in sorted(child_files):
            if child_file not in solved_tasks:
                print(f"  → Solving child: {child_file}")
                solve(child_file)
    
    # Now solve this task
    print(f"\n📋 Solving task: {task_file}")
    
    # Generate tree context
    tree_context = generate_tree_with_summaries(workspace_root, task_file)
    
    # Create prompt
    prompt = solve_prompt(task_file, tree_context)
    
    # Call agent
    working_dir = os.path.dirname(task_file)
    response = agent(prompt, working_dir)
    
    # Mark as solved
    solved_tasks.add(task_file)
    print(f"✅ Completed: {task_file}")


def main():
    """Main entry point for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python solve.py <task_file.md>")
        sys.exit(1)
    
    task_file = sys.argv[1]
    
    if not os.path.exists(task_file):
        print(f"Error: Task file '{task_file}' not found")
        sys.exit(1)
    
    print(f"Starting solve process for: {task_file}")
    solve(task_file)
    print(f"\nSolve complete! Total tasks solved: {len(solved_tasks)}")


if __name__ == "__main__":
    main()