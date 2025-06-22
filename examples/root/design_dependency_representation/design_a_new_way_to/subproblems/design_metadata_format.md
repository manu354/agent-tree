# Design Metadata Format

## Type
complex

## Problem
Design a metadata format for expressing task dependencies in markdown files. Must support parallel groups, sequential chains, and dependencies between tasks. Should be human-readable and machine-parseable.

## Possible Solution
Add a "## Dependencies" section to markdown files with formats like: "depends_on: [task1, task2]", "parallel_with: [task3, task4]", or "execution_order: 1". Consider YAML-like syntax in markdown.

## Notes
Balance between expressiveness and simplicity. Must not require complex parsing. Consider how Claude will generate this during decomposition. Think about validation and error handling.