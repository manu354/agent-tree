# Agent Tree Simple

A clean, context-aware implementation of recursive problem decomposition using Claude CLI.

## Features

- **Context Passing**: Each node knows the root goal, parent task, and sibling tasks
- **Claude CLI Integration**: Uses `claude code` for all LLM interactions  
- **Node Tracking**: Real-time display of node count (X/5) during execution
- **Structured Logging**: Clear visibility into tree execution
- **Error Handling**: Graceful retries and timeout management
- **Organized Output**: Creates workspace directories with all artifacts

## Usage

```bash
python agent_tree_simple.py "Your complex problem description"
```

## How It Works

1. **Assess Complexity**: Claude evaluates if the problem needs decomposition
2. **Decompose if Complex**: Break into 2-4 independent subtasks
3. **Pass Context**: Children receive full context about ancestors, siblings, and tree structure
4. **Solve Recursively**: Each subtask is solved with context awareness (max 5 nodes)
5. **Integrate Solutions**: Parent combines child solutions into final answer

## Context Example

Each child node receives:
```
=== PROBLEM TREE STRUCTURE ===
root/: Build expense tracking app
  reporting/: Create reporting module <- YOU ARE HERE
    - aggregate_data: Aggregate expense data
    - generate_charts: Generate charts
    - export_pdf: Export to PDF
==============================

=== CONTEXT FROM ANCESTORS ===
Root Goal: Build expense tracking app
Parent Task: Create reporting module
Parent's Approach: Split into data, visualization, export
Sibling Tasks:
  - Aggregate expense data
  - Generate charts
  - Export to PDF
===========================
```

## Running Tests

```bash
python -m pytest test_agent_tree_simple.py -v
```

All 24 tests should pass.

## Example

```bash
python example_context.py
```

This demonstrates how context flows through the tree during execution.