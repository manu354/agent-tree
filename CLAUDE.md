# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Tree Simple is a hierarchical problem-solving system that uses Claude CLI to decompose complex problems into manageable subtasks. The system creates a tree of agent nodes where each node can either solve a problem directly or decompose it further.

## Key Commands

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agent_tree_simple.py -v

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

### External Integrations

- **Primary LLM**: Claude CLI (`claude code`) - used for all solving and integration
- **Optional Decomposition**: Gemini Flash via MCP (when available) - faster decomposition decisions
- **Fallback**: Always uses Claude CLI if MCP/Gemini unavailable

### Key Design Patterns

1. **Recursive Decomposition**: Each node decides if a problem needs breaking down
2. **Context Propagation**: Children receive full context about ancestors and siblings
3. **Workspace Organization**: Each execution creates a timestamped directory structure
4. **Graceful Degradation**: Falls back to Claude CLI if optional components fail

### Important Limits

- Maximum tree depth: 3 levels (configurable)
- Maximum nodes per tree: 5 (hardcoded)
- Claude CLI timeout: 120 seconds per call
- Decomposition: 2-4 subtasks per node

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