#!/usr/bin/env python3
"""Debug script to test complexity assessment"""

from agent_tree_simple import AgentNode, Context
from pathlib import Path
import tempfile

def test_complexity():
    with tempfile.TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir) / "test"
        node = AgentNode("test", work_dir)
        
        # Test a problem that should be complex
        problem = "Build a complete REST API with authentication"
        print(f"Testing problem: {problem}")
        
        complexity, subtasks, approach = node.assess_complexity(problem)
        
        print(f"\nResults:")
        print(f"Complexity: {complexity}")
        print(f"Subtasks: {subtasks}")
        print(f"Approach: {approach}")
        print(f"Subtasks is None: {subtasks is None}")
        print(f"Subtasks is empty list: {subtasks == []}")
        print(f"Boolean of subtasks: {bool(subtasks)}")

if __name__ == "__main__":
    test_complexity()