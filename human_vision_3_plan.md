# Human Vision 3 Implementation Plan

## Vision Summary
Transform the system to use markdown files as the primary interface for problem decomposition. Claude creates markdown files directly, user can edit them during pause, then system executes bottom-up.

## Key Requirements from human_vision_3.txt
1. Claude creates markdown files directly via prompts
2. Specific file structure: `/tasks/<problem_name>.md` and `/<problem_name>/subproblems/<subproblem_name>x.md`
3. Concise markdown format with word limits
4. Label problems as simple/complex in markdown
5. Pause after decomposition for user editing
6. Execute bottom-up after user continues

## Phase 1: Remove Technical Debt (30 min) ✅ COMPLETE

### Immediate Deletions
- [x] Delete `src/mcp_client.py`
- [x] Delete `src/zen_mode.py` 
- [x] Remove `_call_gemini_for_decomposition()` from `agent_node.py`
- [x] Remove all MCP imports and fallback logic
- [x] Remove all "if X fails, try Y" patterns

## Phase 2: Implement Markdown-First Decomposition (2 hours) ✅ COMPLETE

### New File Structure
```
workspace/
└── <problem_name>/
│   └── <problem_name>.md
    └── subproblems/
        ├── <subproblem_1>.md
        ├── <subproblem_2>.md
        └── ...
```

### Markdown Format for Subproblems
```markdown
# [Subproblem Name]

## Type
simple | complex

## Problem
[Description in max 100 words]

## Possible Solution
[Approach in max 100 words]

## Notes
[Additional context in max 100 words]
```

### New Decomposition Prompt
```python
DECOMPOSITION_PROMPT = """
You are decomposing this problem: {problem}

Create a markdown structure:

1. First, create a summary file at this path:
   `{parent_path}/{problem_name}.md`
   
2. Then create subproblem files at:
   `{parent_path}/{problem_name}/subproblems/<subproblem_name>1.md`
   `{parent_path}/{problem_name}/subproblems/<subproblem_name>2.md`
   etc.

Each subproblem file MUST follow this exact format:

# [Subproblem Name]

## Type
[simple or complex]

## Problem
[Description - MAX 100 WORDS]

## Possible Solution
[Approach - MAX 100 WORDS]

## Notes
[Context - MAX 100 WORDS]

Label as "simple" if it's a single-step task that can be solved directly.
Label as "complex" if it needs further decomposition.

BE CRITICAL of your decomposition. Actually break down the problem into meaningful subtasks.

Use these tools to create the files:
- Write tool for creating each markdown file
"""
```

### Update agent_tree.py decompose()
- [x] Change decomposition to use new prompt
- [x] Have Claude use Write tool to create markdown files directly (it will do this automatically, its smart)
- [x] Remove JSON parsing - Claude creates files instead
- [x] Use simplest approach to check for whether a subproblem is complex or not, search for "simple" or "complex" and whichever word appears fist is the type. If neither exist, default to simple.
- [x] After decomposition, return immediately (no recursion yet)
- [x] add good unit tests, make sure they pass
- [x] review solution, can we reduce complexity? 

## Phase 3: Implement Pause and Edit Flow (1 hour)

### Main Execution Flow
```python
def solve_problem(problem: str):
    workspace_dir = create_workspace()
    
    # Phase 1: Full tree decomposition
    print("Decomposing problem...")
    decompose_all_nodes(problem, workspace_dir)
    
    # Show structure
    print(f"\nWorkspace created: {workspace_dir}")
    print("Review and modify markdown files as needed.")
    show_tree_structure(workspace_dir)
    
    # Pause
    while True:
        user_input = input("\nType 'continue' to execute: ").strip().lower()
        if user_input == 'continue':
            break
    
    # Phase 2: Bottom-up execution
    print("\nExecuting tasks...")
    return execute_bottom_up(workspace_dir)
```

### Recursive Decomposition Before Pause
```python
def decompose_all_nodes(problem: str, workspace_dir: str, depth=0):
    # Create initial structure
    node = AgentNode(workspace_dir)
    node.decompose_to_markdown(problem)
    
    # Find complex subproblems
    complex_problems = find_complex_problems(workspace_dir)
    
    # Recurse on complex problems (until depth/count limit)
    for subproblem_path in complex_problems:
        if depth < MAX_DEPTH and total_nodes < MAX_NODES:
            subproblem = read_markdown_problem(subproblem_path)
            decompose_all_nodes(subproblem, subproblem_path, depth+1)
```

## Phase 4: Bottom-Up Execution (1.5 hours)

### Post-Order Traversal Implementation
```python
def execute_bottom_up(workspace_dir: str):
    # Build execution stack (post-order traversal)
    execution_stack = []
    
    def build_stack(path):
        subproblem_dirs = find_subproblem_directories(path)
        
        # Add children first (post-order)
        for child in subproblem_dirs:
            build_stack(child)
        
        # Then add current node
        execution_stack.append(path)
    
    build_stack(workspace_dir)
    
    # Execute from bottom up
    for node_path in execution_stack:
        execute_node(node_path)
    
    return read_final_solution(workspace_dir)
```

### Execute Node Function
```python
def execute_node(node_path: str):
    # Read the problem markdown
    problem_md = read_problem_markdown(node_path)
    
    if problem_md['type'] == 'simple':
        # Direct execution
        solution = claude_solve_simple(problem_md['problem'])
    else:
        # Integrate child solutions
        child_solutions = read_child_solutions(node_path)
        solution = claude_integrate(problem_md['problem'], child_solutions)
    
    # Save solution
    write_solution_markdown(node_path, solution)
```

## Phase 5: Simplified Context (30 min)

### Minimal Context for Execution
```python
@dataclass
class Context:
    root_problem: str      # Original problem
    parent_goal: str       # Parent's goal (from markdown)
    current_task: str      # Current task
    sibling_summaries: List[str]  # One-line summaries of siblings
```

### Context Creation from Markdown
- [ ] Read context from markdown files instead of passing through code
- [ ] Include parent goal and root goal as specified
- [ ] Add "be critical of suggested solution" to execution prompts

## Phase 6: Cleanup and Testing (1 hour)

### Remove Old Code
- [ ] Delete old recursive solve logic
- [ ] Remove planning.md format (replaced by individual markdowns)
- [ ] Remove JSON-based decomposition
- [ ] Consolidate into single agent_tree.py file

### Test Cases
- [ ] Test that Claude creates correct file structure
- [ ] Test pause allows file editing
- [ ] Test bottom-up execution order
- [ ] Test with problems hitting depth/count limits
- [ ] Verify word limits are respected in markdown files

## Implementation Order

1. **Phase 2 first**: Get Claude creating markdown files
2. **Phase 4 next**: Implement bottom-up execution 
3. **Phase 3**: Add pause/continue flow
4. **Phase 1**: Remove technical debt
5. **Phase 5-6**: Polish and test

## Key Differences from Current System

1. **Claude creates files directly** - No JSON intermediary
2. **Individual markdown files** - Not single planning.md
3. **Explicit simple/complex labels** - In markdown format
4. **Full decomposition before pause** - All nodes decomposed first
5. **True bottom-up execution** - Using post-order traversal

## Success Criteria

- [ ] File structure matches vision exactly
- [ ] All markdown files created before pause
- [ ] User can edit any markdown file during pause
- [ ] Execution respects user's edits
- [ ] Word limits enforced (100 words per section)
- [ ] Bottom-up execution with context propagation

## Example Flow

```
User: "Build a web scraper"

System creates:
/tasks/build_web_scraper.md
/build_web_scraper/subproblems/parse_html.md (simple)
/build_web_scraper/subproblems/handle_pagination.md (complex)
/build_web_scraper/subproblems/save_data.md (simple)
/handle_pagination/subproblems/detect_next_button.md (simple)
/handle_pagination/subproblems/iterate_pages.md (simple)

[PAUSE - User can edit any .md file]

User types "continue"

Execution order:
1. parse_html.md (simple - direct solve)
2. detect_next_button.md (simple - direct solve)
3. iterate_pages.md (simple - direct solve)
4. handle_pagination.md (complex - integrate children)
5. save_data.md (simple - direct solve)
6. build_web_scraper (complex - integrate all)
```

This directly implements your vision from human_vision_3.txt with markdown files as the primary interface. 