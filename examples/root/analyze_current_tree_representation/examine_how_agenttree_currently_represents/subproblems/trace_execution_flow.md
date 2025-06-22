# Trace Execution Flow

## Type
simple

## Problem
Trace through the complete execution flow of agent-tree from problem decomposition to solution integration, documenting exactly how tasks are scheduled and executed. Focus on identifying where parallel assumptions are made.

## Possible Solution
Follow solve_problem() through decomposition phase and execute_bottom_up() through execution phase. Document the post-order traversal logic and how it enforces parallel-by-default behavior regardless of actual task dependencies.

## Notes
Key files: agent_tree.py (solve_problem, execute_bottom_up), agent_node.py (decompose_to_markdown). Focus on execution order and assumptions about task independence.