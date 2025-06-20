#!/usr/bin/env python3
"""Test the new markdown-based decomposition system automatically"""

from src.agent_tree import solve_problem
from unittest.mock import patch

if __name__ == "__main__":
    # Test with a simple problem
    problem = "Calculate the factorial of 5"
    
    print(f"Testing with problem: {problem}")
    print("=" * 60)
    
    # Mock the input to automatically continue
    with patch('builtins.input', return_value=''):
        try:
            result = solve_problem(problem)
            print(f"\nFinal result:\n{result}")
        except Exception as e:
            print(f"\nError during test: {e}")
            import traceback
            traceback.print_exc()