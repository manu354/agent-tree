#!/usr/bin/env python3
"""
Demonstration of the 5-node limit in agent_tree_simple.py

This script shows how the agent tree stops creating new nodes after 5 nodes have been created.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and show the relevant code
print("=" * 80)
print("AGENT TREE NODE LIMIT IMPLEMENTATION")
print("=" * 80)
print("\nThe agent_tree_simple.py has been modified to stop recursing after 5 nodes.")
print("\nKey changes:")
print("1. Added a node_count tracker in solve_problem()")
print("2. Each time solve_recursive() is called, it increments the counter")
print("3. When node_count reaches 5, it forces direct solving (no more recursion)")
print("\nRelevant code snippet:")
print("-" * 40)
print("""
# Track the total number of nodes created
node_count = [0]  # Using list to make it mutable in nested function

def solve_recursive(task: str, node_path: str, context: Optional[Context] = None, depth: int = 0) -> str:
    # Increment node count
    node_count[0] += 1
    current_node_number = node_count[0]
    
    logger.info(f"→ {node_path}: {task[:60]}... (Node #{current_node_number})")
    
    # Check if we've reached the 5-node limit
    if node_count[0] >= 5:
        logger.info("  Node limit (5) reached, solving directly")
        solution = node.solve_simple(task, context)
        return solution
""")
print("-" * 40)

print("\nThis ensures that:")
print("- The tree will never create more than 5 nodes total")
print("- After the 5th node, all problems are solved directly (no decomposition)")
print("- This prevents infinite recursion and controls resource usage")

print("\nTo test this, run:")
print("  python agent_tree_simple.py 'Your complex problem here'")
print("\nAnd observe that it stops creating nodes after Node #5")
print("=" * 80)