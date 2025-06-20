# Simplification Plan: Markdown-Driven Agent Tree

## Vision Summary
Simplify the system to use markdown files as the primary interface between Claude and the problem decomposition process. Remove all unnecessary complexity, fallback logic, and external dependencies.

## Core Principles
1. **Single Solution Path**: No fallbacks, no alternative implementations
2. **Markdown as Interface**: All problem structure defined in markdown files
3. **Claude-Driven Decomposition**: Let Claude handle more of the logic through better prompts
4. **User Control**: Pause for review/modification before execution

## Phase 1: Remove Technical Debt
- [ ] Delete `src/mcp_client.py` entirely
- [ ] Delete `src/zen_mode.py` entirely
- [ ] Remove all MCP-related imports and logic from `agent_node.py`
- [ ] Remove `_call_gemini_for_decomposition()` from `agent_node.py`
- [ ] Remove all fallback logic patterns (if X fails, try Y)
- [ ] Clean up imports across all files

## Phase 2: Restructure for Markdown-First Approach

### New Directory Structure
```
workspace/
├── tasks/
│   └── <problem_name>.md          # Root problem description
└── <problem_name>/
    └── subproblems/
        ├── <subproblem_1>.md      # Each subtask
        ├── <subproblem_2>.md
        └── ...
```

### Markdown Format for Subproblems
```markdown
# <Subproblem Name>

## Type
complex | simple

## Problem
<Description in max 100 words>

## Possible Solution
<Approach in max 100 words>

## Notes
<Additional context in max 100 words>
```

## Phase 3: Rewrite Core Logic

### 3.1 Update Decomposition Prompt
- [ ] Create new prompt template that instructs Claude to:
  - Create the markdown file structure directly
  - Write concise descriptions (word limits)
  - Label each subproblem as simple/complex
  - Focus on clear problem breakdown

### 3.2 Simplify agent_tree.py
- [ ] Remove `solve_recursive()` function
- [ ] Create `decompose_with_claude()`:
  ```python
  def decompose_with_claude(problem: str, workspace_dir: str, parent_path: str = None):
      # Single Claude call to create all markdown files
      # Claude creates the entire structure in one go
  ```
- [ ] Create `execute_from_bottom_up()`:
  ```python
  def execute_from_bottom_up(workspace_dir: str):
      # Find all leaf nodes (simple problems)
      # Execute them first
      # Work up to complex problems
  ```

### 3.3 Simplify agent_node.py
- [ ] Remove all decomposition logic
- [ ] Keep only execution logic for simple tasks
- [ ] Remove depth tracking, is_leaf parameters
- [ ] Simplify to just `execute_task(task_description, context)`

### 3.4 Simplify context.py
- [ ] Reduce Context to minimal fields:
  - `root_problem`: Original problem
  - `parent_task`: Immediate parent task
  - `current_task`: Task being solved
- [ ] Remove sibling_tasks, parent_approach

## Phase 4: Implement Pause/Continue Flow

### 4.1 Main Execution Flow
```python
def solve_problem(problem: str):
    workspace_dir = create_workspace()
    
    # Phase 1: Decomposition
    print("Decomposing problem...")
    decompose_with_claude(problem, workspace_dir)
    
    # Show created structure
    print(f"\nWorkspace created: {workspace_dir}")
    print("Review and modify markdown files as needed.")
    
    # Pause for user review
    while True:
        user_input = input("\nType 'continue' to execute: ").strip().lower()
        if user_input == 'continue':
            break
    
    # Phase 2: Bottom-up execution
    print("\nExecuting tasks...")
    return execute_from_bottom_up(workspace_dir)
```

### 4.2 Execution Logic
- [ ] Parse markdown files to identify simple vs complex
- [ ] Execute all simple tasks first
- [ ] For complex tasks with completed subtasks:
  - Gather subtask solutions
  - Execute with integration context
- [ ] Continue until root is solved

## Phase 5: Testing & Refinement

### 5.1 Remove Old Tests
- [ ] Delete tests for removed components (MCP, Zen, etc.)
- [ ] Remove tests for old recursive logic

### 5.2 Create New Tests
- [ ] Test markdown parsing
- [ ] Test bottom-up execution order
- [ ] Test pause/continue flow
- [ ] Test with modified markdown files

### 5.3 Simplify Entry Point
- [ ] Single `agent_tree.py` file
- [ ] Remove all command-line flags
- [ ] Remove alternative execution modes

## Implementation Order

1. **Start with deletion** (Phase 1)
   - Remove all technical debt first
   - Get to minimal working system

2. **Build new markdown structure** (Phase 2-3)
   - Focus on Claude prompt that creates structure
   - Simple markdown parsing

3. **Implement pause/continue** (Phase 4)
   - Basic user interaction
   - Bottom-up execution

4. **Test and refine** (Phase 5)
   - Ensure robustness
   - Clean up remaining complexity

## Success Metrics
- [ ] No fallback logic anywhere in codebase
- [ ] Single execution path
- [ ] All problem structure in markdown files
- [ ] User can modify files during pause
- [ ] Execution respects user modifications
- [ ] Total codebase reduced by >50%

## Key Differences from Current System
1. **No recursive Python calls** - Claude creates entire structure at once
2. **No state management** - Markdown files are the state
3. **No complex Context propagation** - Minimal context only
4. **No depth tracking** - Structure determines execution order
5. **No is_leaf detection** - Markdown type field determines this

## Example Flow
```
User: "Build a web scraper"
→ Claude creates:
   - tasks/build_web_scraper.md
   - build_web_scraper/subproblems/parse_html.md (simple)
   - build_web_scraper/subproblems/handle_pagination.md (complex)
   - build_web_scraper/subproblems/save_data.md (simple)
→ System pauses
→ User reviews/edits markdown files
→ User types "continue"
→ System executes simple tasks first
→ System executes complex tasks with context
→ Final solution produced
```

This approach dramatically simplifies the codebase while maintaining the core functionality of hierarchical problem-solving with user control.