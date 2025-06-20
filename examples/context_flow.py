#!/usr/bin/env python3
"""
Example demonstrating context passing in the agent tree
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import solve_problem
import logging

# Enable logging to see the tree execution
logging.basicConfig(level=logging.INFO, format='%(message)s')

if __name__ == "__main__":
    # Example problem that will decompose and show context passing
    problem = """Create a personal expense tracking application with the following features:
    - User authentication and profiles
    - Expense entry with categories and tags
    - Monthly budget tracking and alerts
    - Visual reports and analytics dashboard
    """
    
    print("Solving with context-aware agent tree...")
    print("=" * 80)
    
    # The solve_problem function now passes context down the tree
    # Each child node will know:
    # - The root problem (expense tracking app)
    # - Its parent's task and approach
    # - What its sibling tasks are handling
    
    solution = solve_problem(problem, max_depth=3)
    
    print("\n" + "=" * 80)
    print("Final Solution Preview:")
    print(solution[:500] + "..." if len(solution) > 500 else solution)
    
    print("\n" + "=" * 80)
    print("Key benefits of context passing:")
    print("1. Leaf nodes understand the bigger picture")
    print("2. No duplicate work between siblings")
    print("3. Solutions are better integrated")
    print("4. Each node can make informed decisions")