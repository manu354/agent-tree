# Module Contracts

## Purpose
This document defines the interfaces between modules so they can be developed in parallel.

## Module Interfaces

### decompose.py
```python
def decompose(task_file: str) -> None:
    """
    Decomposes a task file into subtasks.
    
    Args:
        task_file: Path to the .md task file
        
    Side effects:
        - Creates {name}_plan.md
        - Creates {name}_children/ folder with subtask .md files
        - Recursively decomposes complex subtasks
    """
```

### solve.py
```python
def solve(task_file: str) -> None:
    """
    Solves a task tree starting from the given task file.
    
    Args:
        task_file: Path to the root .md task file
        
    Side effects:
        - Updates plan files with progress and solutions
        - Creates/modifies code files as needed
        - Processes dependencies and children first
    """
```

## File Structure Contract

### Input
Any `.md` file with task description

### After Decompose
```
task_name.md                # Original (unchanged)
task_name_plan.md          # Decomposition analysis
task_name_children/        # Folder with subtasks
    subtask1.md           # Contains "## Type" section
    subtask2.md           # May contain "### Dependents" section
```

### After Solve
Same structure, but `*_plan.md` files updated with:
- Progress notes
- Implementation decisions  
- Final summary

## Task File Format
```markdown
# Task Title

## Type
[simple or complex]

## Summary
[One line description]

## Task
[Detailed description]

### Dependents
- [Other Task](../path/to/task.md)
```

## Testing Independently

Each module can create test fixtures:

**For decompose testing:**
```python
# Create a test task file
with open('test_task.md', 'w') as f:
    f.write('# Test Task\n\nDescription here')
    
# Run decompose
decompose('test_task.md')

# Verify outputs created
```

**For solve testing:**
```python
# Create test structure manually
os.makedirs('test_task_children')
# ... create test files

# Run solve  
solve('test_task.md')

# Verify plan files updated
```