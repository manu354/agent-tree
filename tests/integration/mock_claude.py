#!/usr/bin/env python3
"""
Mock Claude CLI for testing the agent-tree system.
This script simulates Claude's responses for different types of prompts.
"""

import sys
import os
import re
import json
from pathlib import Path


def extract_prompt_type(prompt):
    """Determine what type of response is expected based on the prompt"""
    if "helping decompose a complex task" in prompt:
        return "decompose"
    elif "solving a specific task" in prompt:
        return "solve"
    elif "Your task is to implement" in prompt:
        return "implement"
    return "unknown"


def extract_task_info(prompt):
    """Extract task information from the prompt"""
    # Extract task name from markdown header
    task_match = re.search(r'# (.+)', prompt)
    task_name = task_match.group(1) if task_match else "Unknown Task"
    
    # Extract file path from prompt
    file_match = re.search(r'Task file: (.+\.md)', prompt)
    file_path = file_match.group(1) if file_match else None
    
    return task_name, file_path


def generate_decompose_response(task_name, file_path):
    """Generate a mock decomposition response"""
    base_name = Path(file_path).stem if file_path else "task"
    
    # Create different responses based on task complexity
    if "calculator" in task_name.lower():
        return f"""I'll decompose this calculator task into subtasks.

Creating {base_name}_plan.md with the decomposition plan...
Creating {base_name}_children/ directory...

The task has been decomposed into 3 subtasks:
1. parse_expression.md - Complex task for parsing mathematical expressions
2. handle_operations.md - Simple task for performing calculations
3. display_result.md - Simple task for formatting output

All files have been created successfully."""
    
    elif "simple" in task_name.lower():
        return f"""This is a simple task that doesn't need decomposition.

Creating {base_name}_plan.md to mark this as a simple task...

Task marked as simple and ready to be solved directly."""
    
    else:
        # Generic decomposition
        return f"""I'll decompose this task into manageable subtasks.

Creating {base_name}_plan.md with the decomposition plan...
Creating {base_name}_children/ directory...

The task has been decomposed into 2 subtasks:
1. subtask1.md - Simple subtask
2. subtask2.md - Simple subtask

All files have been created successfully."""


def generate_solve_response(task_name, prompt):
    """Generate a mock solve response"""
    # Check if there are dependent solutions in the prompt
    if "Dependent Solutions:" in prompt:
        return f"""I'll solve this task using the provided dependent solutions.

Based on the dependent solutions, I've implemented the {task_name}.

The solution integrates:
- The parsed expression functionality
- The operation handling logic
- The result display formatting

Plan file has been updated with progress and solution."""
    
    else:
        # Simple task solution
        return f"""I'll implement this {task_name} directly.

Implementation complete. The solution:
- Handles the core functionality
- Includes error handling
- Follows best practices

Plan file has been updated with progress and solution."""


def create_decompose_files(prompt):
    """Actually create the files that Claude would create during decomposition"""
    task_name, file_path = extract_task_info(prompt)
    
    if not file_path:
        return
    
    base_dir = Path(file_path).parent
    base_name = Path(file_path).stem
    
    # Create plan file
    plan_path = base_dir / f"{base_name}_plan.md"
    
    if "calculator" in task_name.lower():
        # Create complex decomposition
        plan_content = f"""# {task_name} - Decomposition Plan

## Type
complex

## Overview
This task requires breaking down into subtasks for:
1. Expression parsing
2. Operation handling
3. Result display

## Subtasks
- [Parse Expression](calculator_children/parse_expression.md)
- [Handle Operations](calculator_children/handle_operations.md)
- [Display Result](calculator_children/display_result.md)

## Status
[ ] Not started
"""
        
        # Create children directory
        children_dir = base_dir / f"{base_name}_children"
        children_dir.mkdir(exist_ok=True)
        
        # Create child task files
        (children_dir / "parse_expression.md").write_text("""# Parse Mathematical Expression

## Type
complex

## Description
Parse user input to extract numbers and operations.

## Dependencies
None

## Dependents
- [Build a Calculator CLI](../calculator.md)
""")
        
        (children_dir / "handle_operations.md").write_text("""# Handle Mathematical Operations

## Type
simple

## Description
Perform the actual calculations.

## Dependencies
- [Parse Expression](parse_expression.md)

## Dependents
- [Build a Calculator CLI](../calculator.md)
""")
        
        (children_dir / "display_result.md").write_text("""# Display Calculation Result

## Type
simple

## Description
Format and display the result to the user.

## Dependencies
- [Handle Operations](handle_operations.md)

## Dependents
- [Build a Calculator CLI](../calculator.md)
""")
        
    elif "simple" in task_name.lower():
        # Simple task - no decomposition
        plan_content = f"""# {task_name} - Decomposition Plan

## Type
simple

## Overview
This task can be solved directly without decomposition.

## Status
[ ] Not started
"""
    
    else:
        # Generic decomposition
        plan_content = f"""# {task_name} - Decomposition Plan

## Type
complex

## Overview
This task has been broken down into subtasks.

## Subtasks
- [Subtask 1]({base_name}_children/subtask1.md)
- [Subtask 2]({base_name}_children/subtask2.md)

## Status
[ ] Not started
"""
        
        # Create children directory and files
        children_dir = base_dir / f"{base_name}_children"
        children_dir.mkdir(exist_ok=True)
        
        (children_dir / "subtask1.md").write_text(f"""# Subtask 1

## Type
simple

## Description
First part of {task_name}

## Dependencies
None

## Dependents
- [{task_name}](../{Path(file_path).name})
""")
        
        (children_dir / "subtask2.md").write_text(f"""# Subtask 2

## Type
simple

## Description
Second part of {task_name}

## Dependencies
- [Subtask 1](subtask1.md)

## Dependents
- [{task_name}](../{Path(file_path).name})
""")
    
    plan_path.write_text(plan_content)


def create_solve_files(prompt):
    """Update plan files that Claude would update during solve"""
    # Extract current task file from prompt
    current_file_match = re.search(r'Current task file: (.+\.md)', prompt)
    if not current_file_match:
        return
    
    current_task_path = Path(current_file_match.group(1))
    task_name = current_task_path.stem
    
    # Find corresponding plan file
    plan_path = current_task_path.parent / f"{task_name}_plan.md"
    
    if "calculator" in task_name.lower():
        solution_content = f"""# Solution: {task_name}

## Implementation

```python
def calculator_cli():
    \"\"\"Command-line calculator implementation\"\"\"
    while True:
        expr = input("Enter expression (or 'quit'): ")
        if expr.lower() == 'quit':
            break
        
        try:
            result = eval(expr)  # Simple implementation
            print(f"Result: {{result}}")
        except Exception as e:
            print(f"Error: {{e}}")

if __name__ == "__main__":
    calculator_cli()
```

## Integration
This solution integrates the parsed expressions, handles operations, and displays results.
"""
    else:
        solution_content = f"""# Solution: {task_name}

## Implementation

The task has been implemented successfully.

```python
# Implementation code here
def solution():
    return "Task completed"
```

## Notes
Solution completed as requested.
"""
    
    # Update or create the plan file instead of solution.md
    if not plan_path.exists():
        # Create plan file with solution
        plan_content = f"""# {task_name} - Plan

## Status
[x] Completed

## Progress
{solution_content}
"""
        plan_path.write_text(plan_content)
    else:
        # Update existing plan file
        existing_content = plan_path.read_text()
        
        # Add progress section
        if "## Progress" not in existing_content:
            existing_content += "\n## Progress\n"
        
        # Update status and add solution
        existing_content = existing_content.replace("[ ] Not started", "[x] Completed")
        existing_content = existing_content.replace("## Progress", f"## Progress\n\n{solution_content}")
        
        plan_path.write_text(existing_content)


def main():
    """Main entry point for mock Claude"""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Error: No arguments provided")
        sys.exit(1)
    
    # Skip flags and find prompt
    prompt = None
    for i, arg in enumerate(sys.argv):
        if arg == '-p' and i + 1 < len(sys.argv):
            prompt = sys.argv[i + 1]
            break
    
    if not prompt:
        print("Error: No prompt provided")
        sys.exit(1)
    
    # Determine response type
    prompt_type = extract_prompt_type(prompt)
    task_name, file_path = extract_task_info(prompt)
    
    # Generate appropriate response
    if prompt_type == "decompose":
        print(generate_decompose_response(task_name, file_path))
        create_decompose_files(prompt)
    elif prompt_type == "solve" or prompt_type == "implement":
        print(generate_solve_response(task_name, prompt))
        create_solve_files(prompt)
    else:
        print(f"Mock Claude: Handling {task_name}")
        print("Task processed successfully.")


if __name__ == "__main__":
    main()