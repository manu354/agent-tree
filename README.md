# Agent Tree

A simplified hierarchical problem-solving system using Claude CLI. Breaks down complex tasks into manageable subtasks with human review between planning and execution.

## Features

- **Two-Phase Approach**: Separate decomposition and solving phases
- **Human-in-the-Loop**: Review and modify task plans before execution
- **Claude CLI Integration**: Uses `claude` for all LLM interactions
- **Dependency Resolution**: Handles task dependencies intelligently
- **Context-Aware Solving**: Each task knows its place in the hierarchy
- **Clean Architecture**: Simple, modular design

## Installation

Requires Claude CLI to be installed and configured.

## Usage

### Phase 1: Decompose a Complex Task

```bash
python agent_tree.py decompose your_task.md
```

This creates:
- `your_task_plan.md` - Analysis and decomposition plan
- `your_task_children/` - Folder containing subtask files

### Phase 2: Human Review

Review the generated files and modify as needed:
- Adjust task descriptions
- Add/remove dependencies
- Change complexity markers
- Refine the plan

### Phase 3: Solve the Task Tree

```bash
python agent_tree.py solve your_task.md
```

This:
- Processes tasks in dependency order (leaves first)
- Updates plan files with progress and solutions
- Handles both simple and complex tasks

## How It Works

### Decomposition
1. Claude analyzes the task and creates a plan
2. Generates subtask files marked as "simple" or "complex"
3. Recursively decomposes complex subtasks (max 5 Claude calls)

### Solving
1. Builds a tree view of all tasks with one-line summaries
2. Processes dependencies and children before parents
3. Each task sees where it fits in the overall system
4. Updates plan files with implementation details

## Example

```bash
# 1. Create your task file
echo "# Build a URL shortener service" > url_shortener.md

# 2. Decompose it
python agent_tree.py decompose url_shortener.md

# 3. Review and edit the generated files
# ... make any changes you want ...

# 4. Solve it
python agent_tree.py solve url_shortener.md
```

## File Structure

```
url_shortener.md                    # Original task
url_shortener_plan.md               # Decomposition and progress
url_shortener_children/
├── create_api.md                   # Subtask (might be complex)
├── create_api_plan.md              # Its plan and progress
├── implement_storage.md            # Subtask (simple)
└── implement_storage_plan.md       # Its progress
```

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
- [Other Task](path/to/task.md)
```

## Development

The system is designed for simplicity:
- `agent_tree.py` - Entry point with subcommands
- `decompose.py` - Handles task decomposition
- `solve.py` - Handles task execution

During development, errors are allowed to crash for easier debugging.