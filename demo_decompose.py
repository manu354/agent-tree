#!/usr/bin/env python3
"""
Demo script showing decompose module usage
"""

from decompose import decompose, node_count, seen_tasks

# Show the example task
print("=== DECOMPOSE MODULE DEMO ===\n")
print("Example task file: example_task.md")
print("Content:")
print("-" * 40)
with open("example_task.md", "r") as f:
    print(f.read())
print("-" * 40)

print("\nTo run decomposition on this task, you would call:")
print("  decompose('example_task.md')")
print("\nThis will:")
print("1. Call Claude CLI to analyze the task")
print("2. Create example_task_plan.md with the decomposition analysis") 
print("3. Create example_task_children/ folder with subtasks")
print("4. Recursively decompose any complex subtasks (up to 5 nodes total)")

print("\nGlobal tracking variables:")
print(f"- node_count: {node_count} (tracks total nodes created)")
print(f"- seen_tasks: {seen_tasks} (prevents duplicate processing)")

print("\nTo actually run the decomposition (requires Claude CLI):")
print("  python -c \"from decompose import decompose; decompose('example_task.md')\"")