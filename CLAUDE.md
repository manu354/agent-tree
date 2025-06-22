# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Tree Simple is a hierarchical problem-solving system that uses Claude CLI to decompose complex problems into manageable subtasks. The system creates a tree of agent nodes where each node can either solve a problem directly or decompose it further.

## Key Commands

### Running Tests

The test suite is organized into two categories:
- **Unit tests** (`tests/unit/`): Test individual components with mocked dependencies
- **Live system tests** (`tests/live_system/`): Run the full agent tree system with real Claude CLI

```bash
# Run unit tests only (default)
python -m pytest -v

# Run specific unit test file
python -m pytest tests/unit/test_agent_tree_simple.py -v

# Run ALL tests including live system tests
python -m pytest -c pytest-all.ini -v

# Run only live system tests
python -m pytest tests/live_system/ -v -m live_system

# Skip slow tests
python -m pytest -v -m "not slow"
```

### Running the System
```bash
# Main usage
python agent_tree_simple.py "Your complex problem description"
```

### Development Tools
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Architecture Overview

### Core Components

1. **Context System** (`src/context.py`)
   - Passes information from parent to child nodes
   - Contains: root problem, parent task, parent approach, sibling tasks
   - Unidirectional flow (parent → children)
   - goal is to minimze context to just what is relevant for the task at hand, maximise specificity and conciseness, minimize unnecesary or unrelated detail. Root -> parent path + knowledge of siblings is a heuristic for this.

2. **Agent Node** (`src/agent_node.py`)
   - Handles problem decomposition decisions
   - Executes solutions for leaf nodes
   - Integrates child solutions for branch nodes
   - Uses Claude CLI via subprocess for all LLM interactions

3. **Tree Orchestration** (`src/agent_tree.py`)
   - Entry point: `solve_problem()` function
   - Manages workspace creation and organization
   - Controls recursion depth (default: 3) and node limits
   - Handles bottom-up solution integration


### Key Design Patterns

1. **Recursive Decomposition**: Each node decides if a problem needs breaking down
2. **Context Propagation**: Children receive full context about ancestors and siblings
3. **Workspace Organization**: Each execution creates a timestamped directory structure
4. **Graceful Degradation**: Falls back to Claude CLI if optional components fail

### Important Limits

- Maximum tree depth: 3 levels (configurable)
- Maximum nodes per tree: 5 (hardcoded during development phase)
- Claude CLI timeout: 120 seconds per call (todo, increase to 10 minutes)
- Decomposition: 1-4 subtasks per node

### Output Structure
```
tmp/agent_tree_TIMESTAMP/      # or workspace/agent_tree_TIMESTAMP/
├── problem.txt               # Original problem
├── final_solution.txt        # Integrated solution
└── root/
    ├── solution.txt          # Root node's work
    └── sub1/
        └── solution.txt      # Child solutions
```


# RULES
1. NEVER have more than 1 solution for the same problem. That means never have a new and old version at the saem time. Instead, evolve the system incrementally towards the desired state. Never have fallbacks. 
2. Minimize added complexity to the system when new features are added. Try reduce the complexity by re-architecting, introducing abstractions that hide complexity and seperating concerns. 
3. Add high quality unit tests for any non-trivial changes. These will undergo mutation testing so make sure they are actually testing the method well. Make sure they pass.