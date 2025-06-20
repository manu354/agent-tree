# Minimal Complexity Evolution Plan: Pause/Resume After Tree Decomposition

## Core Insight
The markdown files and directory structure ARE the tree state. We don't need additional persistence or state management.

## Goal
Enable pausing after tree decomposition completes, allowing users to review/modify planning.md files before execution continues.

## Implementation Plan (< 100 lines of code)

### 1. Add Decompose-Only Flag to `solve_recursive`
```python
def solve_recursive(problem, workspace_dir, node_path="root", context=None, 
                   depth=0, max_depth=3, is_leaf=False, decompose_only=False):
    # ... existing code ...
    
    # After creating planning.md via decompose_problem():
    if decompose_only and subtasks:
        # Create subdirectories and recurse for decomposition only
        for i, subtask in enumerate(subtasks):
            solve_recursive(subtask["task"], workspace_dir, sub_path, 
                          new_context, depth + 1, max_depth, 
                          subtask.get("is_simple", False), decompose_only=True)
        return None  # Don't execute, just decompose
    
    # ... rest of existing execution code ...
```

### 2. Add Execute-From-Markdown Function
```python
def execute_from_markdown(workspace_dir):
    """Execute the tree by reading planning.md files."""
    
    def find_leaf_dirs(path):
        """Find directories with no subdirectories."""
        leaves = []
        for root, dirs, files in os.walk(path):
            if not dirs and "planning.md" in files:
                leaves.append(root)
        return leaves
    
    def parse_planning_md(file_path):
        """Extract task from planning.md."""
        with open(file_path, 'r') as f:
            content = f.read()
            # Extract task from "# Task: ..." line
            match = re.search(r'^# Task: (.+)$', content, re.MULTILINE)
            return match.group(1) if match else "Unknown task"
    
    # Execute all leaf nodes
    leaf_dirs = find_leaf_dirs(workspace_dir)
    for leaf_dir in leaf_dirs:
        planning_md = os.path.join(leaf_dir, "planning.md")
        task = parse_planning_md(planning_md)
        
        # Re-create minimal context
        context = Context(root_problem="From planning.md", 
                         parent_task=task,
                         sibling_tasks=[])
        
        node = AgentNode(task, leaf_dir, context)
        solution = node.solve_simple()
        
        # Save solution alongside planning.md
        with open(os.path.join(leaf_dir, "solution.md"), 'w') as f:
            f.write(f"# Solution\n\n{solution}")
    
    # Integrate bottom-up (reuse existing integrate_solutions logic)
    return integrate_from_filesystem(workspace_dir)
```

### 3. Modify `solve_problem` for Two-Phase Execution
```python
def solve_problem(problem, max_depth=3, pause_after_decomposition=False):
    workspace_dir = create_workspace()
    
    # Phase 1: Decomposition only
    if pause_after_decomposition:
        solve_recursive(problem, workspace_dir, depth=0, max_depth=max_depth, 
                       decompose_only=True)
        
        print(f"\n{'='*50}")
        print("DECOMPOSITION COMPLETE")
        print(f"{'='*50}")
        print(f"Workspace: {workspace_dir}")
        print("\nYou can now:")
        print("- Review planning.md files in each directory")
        print("- Modify task descriptions or approaches")
        print("- Add context or constraints")
        print(f"{'='*50}")
        input("\nPress Enter to continue with execution...")
        
        # Phase 2: Execute from markdown
        return execute_from_markdown(workspace_dir)
    
    # Original behavior (no pause)
    return solve_recursive(problem, workspace_dir, depth=0, max_depth=max_depth)
```

### 4. Add Command-Line Flag
```python
# In agent_tree.py (main file)
parser.add_argument('--pause-after-decomposition', action='store_true',
                    help='Pause after decomposition to allow editing planning.md files')

# Pass to solve_problem
solution = solve_problem(args.problem, args.max_depth, 
                        pause_after_decomposition=args.pause_after_decomposition)
```

## What This Achieves

1. **Minimal Changes**: ~80 lines of new code, mostly reading functions
2. **No State Management**: Filesystem is the state
3. **User-Friendly**: Edit familiar markdown files with any editor
4. **Backward Compatible**: Default behavior unchanged
5. **Simple Mental Model**: Decompose → Pause → Execute

## Example Usage

```bash
$ python agent_tree.py "Build a REST API" --pause-after-decomposition

Creating workspace: workspace/agent_tree_20240620_150000/
Decomposing problem...

==================================================
DECOMPOSITION COMPLETE
==================================================
Workspace: workspace/agent_tree_20240620_150000/

You can now:
- Review planning.md files in each directory
- Modify task descriptions or approaches
- Add context or constraints
==================================================

Press Enter to continue with execution...

[User edits planning.md files in another terminal/editor]

Executing from markdown files...
Processing: Create database schema
Processing: Implement API endpoints
Processing: Add authentication
Integrating solutions...
Complete! See workspace/agent_tree_20240620_150000/root/solution.md
```

## Why This Is The Right Approach

1. **Leverages Existing Structure**: The markdown files already contain all needed information
2. **No Duplication**: No separate state files or complex objects
3. **Direct Manipulation**: Users edit the actual planning files, not some intermediate format
4. **Minimal Learning Curve**: Just edit markdown files during the pause
5. **Easy to Debug**: Can manually inspect/run any subtree by reading its planning.md

## Testing Strategy

```python
def test_pause_resume():
    # Create a test problem
    problem = "Create a calculator"
    
    # Run decomposition only
    workspace = create_workspace()
    solve_recursive(problem, workspace, decompose_only=True)
    
    # Verify planning.md files created
    assert os.path.exists(f"{workspace}/root/planning.md")
    
    # Modify a planning file
    planning_file = f"{workspace}/root/add/planning.md"
    with open(planning_file, 'a') as f:
        f.write("\n<!-- User note: Use binary addition -->")
    
    # Execute from markdown
    solution = execute_from_markdown(workspace)
    
    # Verify execution completed
    assert os.path.exists(f"{workspace}/root/solution.md")
```

## Future Enhancements (Not MVP)
- Watch mode: Auto-detect when user saves planning.md files
- Tree visualization: ASCII art of the decomposition tree
- Selective execution: Run only specific subtrees
- Resume from partial execution: Save progress markers