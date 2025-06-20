# Evolution Plan: Pause/Resume After Tree Decomposition (MVP)

## Critical Analysis of Original Plan

The original plan was over-engineered for an MVP:
- **Unnecessary State Objects**: TreeState, NodeState, execution_queue add complexity when the filesystem already represents the tree
- **Redundant Persistence**: Creating tree_state.json duplicates information already in planning.md files
- **Complex Change Detection**: Tracking modification times and comparing content is overkill - just re-read the files
- **5 Phases**: Too many implementation phases for a simple pause/resume feature

**Key Insight**: The markdown files and directory structure ARE the tree state. We should use them as the single source of truth.

## Vision Summary
Enable the system to pause after completing all tree decomposition (when all branches end in leaf nodes), allowing users to explore and modify the generated `.md` files before resuming execution with incorporated feedback.

## Current State Analysis

### What Works Well
- `.md` files created during decomposition document the plan
- Directory structure mirrors the tree hierarchy
- Context flows properly through the tree

### What Needs Enhancement
- No pause/resume capability
- Execution immediately follows decomposition

## MVP Implementation Plan (80/20 Approach)

### Core Insight
The markdown files and directory structure ARE the tree state. We don't need additional persistence or state management for MVP.

### Phase 1: Simple Two-Phase Execution
**Goal**: Split decomposition and execution with minimal changes.

1. **Modify `solve_problem()` in agent_tree.py**:
   ```python
   def solve_problem(problem, max_depth=3):
       workspace_dir = create_workspace()
       
       # Phase 1: Decomposition only
       decompose_full_tree(problem, workspace_dir, max_depth)
       
       # Always pause - this is now default behavior
       print(f"\n=== DECOMPOSITION COMPLETE ===")
       print(f"Workspace: {workspace_dir}")
       print("Review and modify planning.md files as needed.")
       
       while True:
           user_input = input("Type 'continue' to execute: ").strip().lower()
           if user_input == 'continue':
               break
       
       # Phase 2: Execute from markdown files
       return execute_from_markdown(workspace_dir)
   ```

2. **New simple functions**:
   - `decompose_full_tree()`: Only creates planning.md files, no execution
   - `execute_from_markdown()`: Reads planning.md files and executes

### Phase 2: Read Tree from Markdown
**Goal**: Use existing markdown files as the source of truth.

1. **Simple planning.md format** (already exists):
   ```markdown
   # Task: [Description]
   
   ## Subtasks:
   1. [Subtask 1] (simple)
   2. [Subtask 2] (complex)
   ```

2. **Parse function**:
   ```python
   def read_node_from_markdown(planning_md_path):
       # Extract task description
       # Extract subtasks and their types
       # Return as simple dict
   ```

3. **Tree traversal**:
   ```python
   def execute_from_markdown(workspace_dir):
       # Walk directory tree
       # Find leaf nodes (no subdirectories)
       # Execute leaves, then integrate upward
   ```

### Implementation Steps

1. **Refactor solve_recursive() to separate concerns**:
   ```python
   def solve_recursive(task, node_path, context, depth, is_leaf, decompose_only=False):
       # Create planning.md as before
       if decompose_only:
           # Stop after creating planning.md and subdirectories
           return None
       else:
           # Continue with execution
           return solution
   ```

2. **Simple markdown parser**:
   ```python
   def parse_planning_md(file_path):
       with open(file_path) as f:
           content = f.read()
       
       # Extract task from "# Task: ..."
       # Extract subtasks from "## Subtasks:" section
       # Return {"task": "...", "subtasks": [...]}
   ```

3. **Execution from filesystem**:
   ```python
   def execute_from_markdown(workspace_dir):
       # Find all leaf directories (no subdirs)
       leaf_dirs = find_leaf_directories(workspace_dir)
       
       # Execute each leaf
       for leaf_dir in leaf_dirs:
           planning_md = os.path.join(leaf_dir, "planning.md")
           task_info = parse_planning_md(planning_md)
           solution = agent_node.solve_simple(task_info["task"])
           save_solution(leaf_dir, solution)
       
       # Integrate upward from leaves to root
       return integrate_bottom_up(workspace_dir)
   ```

## Why This Approach is Better

1. **No Additional State Management**: Markdown files ARE the state
2. **User-Friendly**: Users can edit familiar markdown files
3. **Minimal Code Changes**: Mostly reuses existing code
4. **No Serialization Complexity**: Filesystem is the persistence layer
5. **Natural Pause Point**: Just stop after decomposition phase

## Testing Strategy

1. **Unit Tests**:
   - Test markdown parsing
   - Test directory traversal
   - Test decompose-only mode

2. **Integration Test**:
   ```python
   def test_pause_resume():
       # Run decomposition only
       workspace = solve_problem(problem, pause_after_decomposition=False, decompose_only=True)
       
       # Modify a planning.md file
       modify_planning_file(workspace)
       
       # Run execution from markdown
       solution = execute_from_markdown(workspace)
       
       # Verify modification was incorporated
   ```

## Success Criteria

- System pauses after decomposition ✓
- Users can modify planning.md files ✓
- Execution reads from modified files ✓
- No complex state management ✓
- Minimal code changes ✓

## Example Usage

```bash
# Run normally - pause is now default
$ python agent_tree.py "Build a todo app"

Creating workspace: workspace/agent_tree_20240620_143022/
Decomposing problem...
Created: workspace/agent_tree_20240620_143022/root/planning.md
Created: workspace/agent_tree_20240620_143022/root/frontend/planning.md
Created: workspace/agent_tree_20240620_143022/root/backend/planning.md
Created: workspace/agent_tree_20240620_143022/root/database/planning.md

=== DECOMPOSITION COMPLETE ===
Workspace: workspace/agent_tree_20240620_143022/
Review and modify planning.md files as needed.
Type 'continue' to execute: continue

Executing from markdown files...
Solving: Create frontend UI components
Solving: Create backend API endpoints  
Solving: Design database schema
Integrating solutions...
Final solution saved to: workspace/agent_tree_20240620_143022/root/solution.md
```

## Future Considerations (Not MVP)

- Add command to re-run decomposition for specific nodes
- Support for partial execution
- Better visualization of tree structure
- Integration with VSCode for editing

## Summary

This MVP approach achieves the pause/resume vision with:
- **~50 lines of new code** instead of ~500
- **No new data structures** - filesystem is the database
- **No state management** - markdown files are the state
- **Natural user interface** - edit familiar markdown files
- **Maximum reuse** of existing code

The key insight is recognizing that the filesystem and markdown files already contain all the information needed. Adding layers of abstraction would only complicate the system without adding value for the MVP.