#!/usr/bin/env python3
"""
Basic usage example of agent tree
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import solve_problem


def main():
    """Run basic examples"""
    
    # Example 1: Simple problem (solved directly)
    print("=" * 80)
    print("Example 1: Simple Problem")
    print("=" * 80)
    
    result = solve_problem("Write a Python function to calculate the factorial of a number")
    print(f"\nFinal result: {result[:200]}...")
    
    print("\n" + "=" * 80 + "\n")
    
    # Example 2: Complex problem (decomposed)
    print("=" * 80)
    print("Example 2: Complex Problem")
    print("=" * 80)
    
    result = solve_problem(
        "Create a simple expense tracking system with functions to add expenses, "
        "calculate totals, and export to CSV"
    )
    print(f"\nFinal result: {result[:200]}...")


if __name__ == "__main__":
    main()