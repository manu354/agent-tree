#!/usr/bin/env python3
"""Test the two-phase execution of agent tree - simpler version"""

import logging
import os
from src.agent_tree import solve_problem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Disable MCP client to avoid the mcp__zen__chat issue
os.environ['DISABLE_MCP_CLIENT'] = '1'

# Test with a simple problem
problem = "Create a Python function to calculate the factorial of a number"

print("Testing two-phase agent tree execution...")
print("="*50)

# Override input() to simulate user pressing enter
import builtins
original_input = builtins.input

def mock_input(prompt):
    print(prompt)
    print("[AUTO-CONTINUING]")
    return ""

builtins.input = mock_input

try:
    result = solve_problem(problem, max_depth=2, use_tmp=True)
    
    print("\n\nFINAL RESULT:")
    print("="*50)
    print(result)
finally:
    # Restore original input
    builtins.input = original_input