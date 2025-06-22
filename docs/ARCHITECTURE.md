# System Architecture

## Overview

The Agent Tree system implements hierarchical problem decomposition using a tree of Claude agents.

## Core Architecture

### 1. Context Management (`src/context.py`)
- **Purpose**: Propagate information down the tree
- **Contents**: Root goal, parent task, sibling tasks, tree structure
- **Tree Visualization**: Shows complete problem hierarchy with "YOU ARE HERE" marker
- **Flow**: Parent → Children (unidirectional)

### 2. Agent Nodes (`src/agent_node.py`)
- **Decomposition**: Analyzes if problem needs breaking down
- **Solving**: Handles leaf nodes and simple problems
- **Integration**: Combines child solutions

### 3. Tree Orchestration (`src/agent_tree.py`)
- **Recursion Control**: Depth and node limits
- **Node Tracking**: Real-time progress display (X/5)
- **Workspace Management**: Organized output structure
- **Solution Flow**: Bottom-up integration

## Decomposition Decision Flow

```mermaid
graph TD
    A[Receive Problem] --> B{Is Leaf Node?}
    B -->|Yes| C[Solve Directly]
    B -->|No| D[Ask Gemini/Claude]
    D --> E{Needs Decomposition?}
    E -->|No| C
    E -->|Yes| F[Create Subtasks]
    F --> G{For Each Subtask}
    G --> H[Mark as Simple/Complex]
    H --> I[Recurse with Context]
    I --> J[Integrate Solutions]
```

## Node Types

### 1. Root Node
- Entry point for problem
- No parent context
- Creates initial decomposition

### 2. Branch Nodes
- Can decompose further (`is_leaf=False`)
- Pass context to children
- Integrate child solutions

### 3. Leaf Nodes
- Cannot decompose (`is_leaf=True`)
- Solve directly
- Return solution to parent

## Communication Flow

### 1. Downward (Context)
```
Root Problem
    ↓
Parent Task + Approach
    ↓
Sibling Awareness
    ↓
Tree Structure Visualization
```

### 2. Upward (Solutions)
```
Leaf Solutions
    ↑
Integrated Solutions
    ↑
Final Solution
```

## External Integrations

### Claude CLI
- Primary LLM for solving
- Integration tasks
- Fallback for decomposition

### Gemini (via MCP)
- Fast decomposition decisions
- JSON-structured responses
- Optional optimization

## Limits & Constraints

1. **Depth Limit**: Max 3 levels (configurable)
2. **Node Limit**: Max 5 nodes per tree (tracked in real-time)
3. **Timeout**: 2 minutes per Claude call
4. **Context Size**: Full ancestor chain + tree structure

## Node Tracking System

The system displays real-time progress as nodes are created:

1. **Node Counter**: Maintained at tree level
2. **Display Format**: "🚀 Executing Claude on complex problem X/5..."
3. **Implementation**:
   - Each `AgentNode` receives a `node_number` parameter
   - `ClaudeClient` displays the count during execution
   - Counter increments before node creation
4. **Visibility**: Users see progress toward 5-node limit

## Error Handling

1. **Graceful Degradation**
   - MCP fails → Claude CLI fallback
   - JSON parse fails → Solve directly

2. **Resource Protection**
   - Node count tracking
   - Depth limit enforcement
   - Process termination on timeout

## Output Structure

Each execution creates:
```
workspace/
└── agent_tree_TIMESTAMP/
    ├── planning.md         # Final integrated solution
    └── tasks/
        └── root/
            ├── root_problem.md  # Root problem description
            ├── solution.md      # Root's work
            └── subproblems/
                ├── sub1.md      # Subproblem descriptions
                └── sub2.md
```

During execution, users see:
- Tree structure visualization after decomposition
- Real-time node count (X/5) as problems are processed
- Clear logging of which node is being executed