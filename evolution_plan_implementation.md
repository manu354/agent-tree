# Evolution Plan Implementation Checklist

## Phase 0: Reduce Technical Debt

### Simplify Existing Code
- [ ] Remove mcp_client.py entirely - use only Claude CLI
- [ ] Delete `_call_gemini_for_decomposition()` from agent_node.py
- [ ] Remove all MCP-related imports and fallback logic
- [ ] Consolidate duplicate Context creation code into single factory method

### Create Clean Abstractions
- [ ] Create `TreeNode` class to encapsulate directory operations:
  ```python
  class TreeNode:
      def __init__(self, path: str)
      def is_leaf(self) -> bool
      def get_children(self) -> List[TreeNode]
      def read_planning_md(self) -> dict
      def write_solution_md(self, solution: str)
  ```
- [ ] Create `MarkdownParser` class instead of loose functions:
  ```python
  class MarkdownParser:
      def parse_planning(self, content: str) -> dict
      def parse_solution(self, content: str) -> str
  ```

### Separate Concerns
- [ ] Move all file I/O operations to a `WorkspaceManager` class
- [ ] Extract Claude CLI execution to standalone `ClaudeExecutor` class
- [ ] Remove Context serialization logic (no longer needed)

## Phase 1: Refactor Core Functions

### agent_tree.py
- [x] Add `decompose_only=False` parameter to `solve_recursive()`
- [x] Add early return when `decompose_only=True` after creating planning.md
- [ ] Create `decompose_full_tree()` wrapper that calls `solve_recursive(decompose_only=True)`
- [x] Update `solve_problem()` to call `decompose_full_tree()` first
- [x] Add pause with "Type 'continue' to execute:" prompt after decomposition
- [x] Call `execute_from_markdown()` after user types 'continue'

## Phase 2: Implement Markdown Execution

### New Functions in agent_tree.py
- [x] Create `find_leaf_directories(workspace_dir)` - returns dirs with no subdirs (implemented inline)
- [x] Create `parse_planning_md(file_path)` - extracts task and subtasks from markdown (simplified)
- [x] Create `execute_from_markdown(workspace_dir)` - main execution function (as execute_from_filesystem)
- [ ] Create `integrate_bottom_up(workspace_dir)` - integrates solutions from leaves to root (partially done)

### parse_planning_md() Implementation
- [x] Read file content
- [x] Extract task from "# Task: ..." line using regex
- [ ] Extract subtasks from "## Subtasks:" section (not needed for current implementation)
- [ ] Return dict: `{"task": "...", "subtasks": [{"task": "...", "is_simple": bool}]}` (simplified)

### execute_from_markdown() Implementation
- [x] Find all leaf directories
- [x] For each leaf: read planning.md, create AgentNode, call solve_simple()
- [ ] Save solution.md in each leaf directory
- [x] Call integrate_bottom_up() to combine solutions (integrated into execute_from_filesystem)

### integrate_bottom_up() Implementation
- [ ] Start from leaf directories
- [ ] For each parent with completed children: read child solutions
- [ ] Create integration task with child solutions
- [ ] Save integrated solution.md
- [ ] Repeat until root is reached

## Phase 3: Testing

### Unit Tests
- [ ] Test `parse_planning_md()` with sample markdown
- [ ] Test `find_leaf_directories()` with mock filesystem
- [x] Test `decompose_only` mode creates files without executing (tested manually)

### Integration Test
- [ ] Create test that decomposes, modifies planning.md, then executes
- [ ] Verify modified content appears in final solution

### Manual Testing
- [x] Run full decompose/pause/edit/continue flow
- [ ] Test with complex multi-level problems (needs better decomposition prompts)
- [x] Verify all planning.md files are created before pause
- [ ] Verify user edits are incorporated in execution

## Phase 4: Cleanup

- [ ] Remove any unused imports
- [ ] Update main() to remove command-line flags
- [ ] Update tests to match new behavior
- [ ] Run existing test suite to ensure no regressions

## Phase 5: Further Simplification

### Reduce AgentNode Complexity
- [ ] Remove `depth` parameter - use TreeNode.get_depth() instead
- [ ] Merge `solve_simple()` and `integrate_solutions()` into single `execute()` method
- [ ] Remove `is_leaf` parameter - determine from filesystem

### Simplify Context Flow
- [ ] Remove `parent_approach` from Context - not used in execution phase
- [ ] Remove `sibling_tasks` from Context - can be read from filesystem if needed
- [ ] Keep only `root_problem` and `current_task` in Context

### Consolidate Entry Points
- [ ] Merge `agent_tree_simple.py` and other variants into single `agent_tree.py`
- [ ] Remove duplicate solve_problem implementations
- [ ] Single main() function with no branching logic

## Phase 6: Next Priority Tasks

### Fix Decomposition Logic
- [ ] Adjust decomposition prompt to encourage breaking down multi-component tasks
- [ ] Add examples in prompt of what should be decomposed vs solved directly
- [ ] Consider lowering the threshold for what's considered "complex"
- [ ] Test with problems that have clear sub-components

### Persist Solutions to Filesystem
- [ ] Modify `solve_simple()` to save solution to solution.md
- [ ] Modify `integrate_solutions()` to save integrated solution to solution.md
- [ ] Update `execute_from_filesystem()` to read solution.md files
- [ ] Ensure solution.md files are created in correct directories

### Test Edge Cases
- [ ] Test with problems that hit the 5-node limit
- [ ] Test with very deep recursion (max_depth)
- [ ] Test with problems that mix simple and complex subtasks
- [ ] Test error handling when planning.md is missing or malformed

### Clean Up Technical Debt
- [ ] Remove `_call_claude_for_decomposition()` fallback - use only one path
- [ ] Remove MCP client imports and HAS_MCP_CLIENT checks
- [ ] Simplify Context class to only essential fields
- [ ] Remove unused parameters like `is_leaf` where it can be determined from filesystem