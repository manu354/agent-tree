#!/usr/bin/env python3
"""
Test suite for verifying node limit enforcement
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.agent_tree import solve_problem
from src.claude_client import ClaudeClient


class TestNodeLimit(unittest.TestCase):
    """Test that the 5-node limit is properly enforced"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.claude_client_patcher = patch("src.claude_client.ClaudeClient")
        self.MockClaudeClient = self.claude_client_patcher.start()
        self.addCleanup(self.claude_client_patcher.stop)
        self.mock_client = MagicMock()
        self.MockClaudeClient.return_value = self.mock_client

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("builtins.input", return_value="")
    @patch("src.agent_node.AgentNode.decompose_to_markdown")
    @patch("src.agent_node.AgentNode.is_problem_complex")
    def test_node_limit_stops_at_5_nodes(
        self, mock_is_complex, mock_decompose, mock_input
    ):
        """Test that exactly 5 nodes are created when limit is reached"""
        
        # Track how many times decompose_to_markdown is called
        decompose_call_count = 0
        created_files = []
        
        def decompose_side_effect(task, context, parent_path=""):
            nonlocal decompose_call_count
            decompose_call_count += 1
            
            # Root node creates 3 subproblems
            if decompose_call_count == 1:
                files = []
                for i in range(3):
                    file_path = self.temp_dir / f"sub{i}.md"
                    file_path.write_text(f"# Subproblem {i}\n## Type\ncomplex\n## Problem\nSub {i}")
                    files.append(str(file_path))
                created_files.extend(files)
                return files
            # Second node creates 2 more subproblems (this would exceed limit)
            elif decompose_call_count == 2:
                files = []
                for i in range(2):
                    file_path = self.temp_dir / f"sub2_{i}.md"
                    file_path.write_text(f"# Subproblem 2-{i}\n## Type\ncomplex\n## Problem\nSub 2-{i}")
                    files.append(str(file_path))
                created_files.extend(files)
                return files
            else:
                return []
        
        # Make all problems complex initially
        mock_is_complex.return_value = True
        mock_decompose.side_effect = decompose_side_effect
        
        # Mock Claude responses
        self.mock_client.run_prompt.return_value = "Solution"
        
        # Run solve_problem
        result = solve_problem("Test problem")
        
        # Verify exactly 5 nodes were created:
        # 1. Root node
        # 2-4. Three subproblems from root
        # 5. First subproblem of the first child (then it should stop)
        self.assertEqual(decompose_call_count, 5)
        
    @patch("builtins.input", return_value="")
    @patch("src.agent_node.AgentNode.decompose_to_markdown")
    @patch("src.agent_node.AgentNode.is_problem_complex")
    def test_node_limit_with_deep_tree(
        self, mock_is_complex, mock_decompose, mock_input
    ):
        """Test node limit with a deep tree structure"""
        
        node_creation_count = []
        
        def decompose_side_effect(task, context, parent_path=""):
            # Track which node is creating subproblems
            node_creation_count.append(task)
            
            # Each node creates just 1 subproblem (to test deep tree)
            if len(node_creation_count) <= 4:  # First 4 calls create subproblems
                file_path = self.temp_dir / f"deep{len(node_creation_count)}.md"
                file_path.write_text(f"# Deep {len(node_creation_count)}\n## Type\ncomplex\n## Problem\nDeep")
                return [str(file_path)]
            else:
                return []
        
        mock_is_complex.return_value = True
        mock_decompose.side_effect = decompose_side_effect
        self.mock_client.run_prompt.return_value = "Solution"
        
        result = solve_problem("Deep test problem")
        
        # In a deep tree, we create 4 nodes that successfully decompose
        # The 5th node hits the limit early and doesn't contribute to our mock count
        # This confirms the node limit is working correctly
        self.assertEqual(len(node_creation_count), 4)
        
        # Verify we created the expected tree structure (4 levels deep)
        self.assertTrue((self.temp_dir / "deep1.md").exists())
        self.assertTrue((self.temp_dir / "deep2.md").exists())
        self.assertTrue((self.temp_dir / "deep3.md").exists())
        self.assertTrue((self.temp_dir / "deep4.md").exists())
        
    @patch("builtins.input", return_value="")
    @patch("src.agent_node.AgentNode.decompose_to_markdown")
    @patch("src.agent_node.AgentNode.is_problem_complex") 
    def test_node_limit_with_wide_tree(
        self, mock_is_complex, mock_decompose, mock_input
    ):
        """Test node limit with a wide tree (many siblings)"""
        
        decompose_call_count = 0
        
        def decompose_side_effect(task, context, parent_path=""):
            nonlocal decompose_call_count
            decompose_call_count += 1
            
            # Root creates 10 subproblems (way more than limit)
            if decompose_call_count == 1:
                files = []
                for i in range(10):
                    file_path = self.temp_dir / f"wide{i}.md"
                    file_path.write_text(f"# Wide {i}\n## Type\ncomplex\n## Problem\nWide")
                    files.append(str(file_path))
                return files
            else:
                return []
        
        mock_is_complex.return_value = True  
        mock_decompose.side_effect = decompose_side_effect
        self.mock_client.run_prompt.return_value = "Solution"
        
        result = solve_problem("Wide test problem")
        
        # Should create 1 root + 4 children = 5 nodes total
        # Even though root tried to create 10 children
        self.assertEqual(decompose_call_count, 5)


if __name__ == "__main__":
    unittest.main()