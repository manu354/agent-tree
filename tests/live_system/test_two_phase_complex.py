#!/usr/bin/env python3
"""Test the two-phase execution with a complex problem that requires decomposition"""

import logging
import os
import pytest
from src.agent_tree import solve_problem


@pytest.mark.live_system
@pytest.mark.slow
def test_two_phase_complex_problem():
    """Test two-phase execution with a complex problem that requires decomposition"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Disable MCP client to avoid the mcp__zen__chat issue
    os.environ["DISABLE_MCP_CLIENT"] = "1"

    # Test with a complex problem that should decompose
    problem = "Build a simple REST API for a todo list application with CRUD operations"

    print("Testing two-phase agent tree execution with complex problem...")
    print("=" * 50)

    # Override input() to simulate user pressing enter
    import builtins

    original_input = builtins.input

    def mock_input(prompt):
        print(prompt)
        print("[AUTO-CONTINUING]")
        return ""

    builtins.input = mock_input

    try:
        result = solve_problem(problem, max_depth=3, use_tmp=True)

        print("\n\nFINAL RESULT:")
        print("=" * 50)
        print(result[:1000] + "..." if len(result) > 1000 else result)

        # Add assertions to make it a proper test
        assert result is not None
        assert len(result) > 0
        assert "todo" in result.lower() or "api" in result.lower()
    finally:
        # Restore original input
        builtins.input = original_input
