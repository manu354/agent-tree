#!/usr/bin/env python3
"""Test the new markdown-based decomposition system"""

import pytest
from src.agent_tree import solve_problem


@pytest.mark.live_system
def test_markdown_simple_problem():
    """Test markdown system with a simple problem"""
    # Test with a simple problem
    problem = "Calculate the factorial of 5"

    print(f"Testing with problem: {problem}")
    print("=" * 60)

    result = solve_problem(problem)
    print(f"\nFinal result:\n{result}")

    # Add assertions
    assert result is not None
    assert "120" in str(result) or "factorial" in result.lower()


if __name__ == "__main__":
    # Allow running as a script for manual testing
    test_markdown_simple_problem()
