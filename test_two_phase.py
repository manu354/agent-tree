#!/usr/bin/env python3
"""Test the two-phase execution of agent tree"""

import logging
from src.agent_tree import solve_problem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Test with a simple problem
problem = "Create a Python function to calculate the factorial of a number"

print("Testing two-phase agent tree execution...")
print("="*50)

result = solve_problem(problem, max_depth=2, use_tmp=True)

print("\n\nFINAL RESULT:")
print("="*50)
print(result)