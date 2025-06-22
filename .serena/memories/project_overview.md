# Agent Tree Simple Project Overview

## Purpose
Agent Tree Simple is a hierarchical problem-solving system that uses Claude CLI to decompose complex problems into manageable subtasks. The system creates a tree of agent nodes where each node can either solve a problem directly or decompose it further.

## Core Features
- **Context-aware decomposition**: Each node knows root goal, parent task, and sibling tasks
- **Claude CLI integration**: Uses `claude code` subprocess calls for all LLM interactions
- **Recursive problem solving**: Automatically breaks down complex problems into simpler ones
- **Bottom-up solution integration**: Child solutions are integrated by parent nodes
- **Organized output**: Creates timestamped workspace directories with all artifacts

## Architecture
- **src/agent_tree.py**: Main orchestration and entry point
- **src/agent_node.py**: Individual node logic for decomposition and solving
- **src/context.py**: Context propagation system (parent → children)
- **src/claude_client.py**: Claude CLI interaction wrapper
- **src/prompts.py**: Prompt templates for decomposition and solving
- **src/markdown_utils.py**: Markdown parsing and formatting utilities

## Key Limits
- Max tree depth: 3 levels (configurable)
- Max nodes per tree: 5 (hardcoded during development)
- Claude CLI timeout: 120 seconds per call
- Decomposition: 1-4 subtasks per node