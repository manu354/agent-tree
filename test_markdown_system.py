#!/usr/bin/env python3
"""Test the new markdown-based decomposition system"""

from src.agent_tree import solve_problem

if __name__ == "__main__":
    # Test with a simple problem
    problem = "Calculate the factorial of 5"
    
    print(f"Testing with problem: {problem}")
    print("=" * 60)
    
    try:
        result = solve_problem(problem)
        print(f"\nFinal result:\n{result}")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()