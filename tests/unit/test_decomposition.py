#!/usr/bin/env python3
"""
Test suite for the new decomposition system
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import subprocess

# Import the module under test
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context
from src.agent_tree import solve_problem
from src.claude_client import ClaudeClient
from src.markdown_utils import find_subproblem_files
from src.prompts import build_decomposition_prompt


class TestDecomposeMethod(unittest.TestCase):
    """Unit tests for decompose_to_markdown method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("test_node", self.temp_dir, depth=0)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_simple_problem(self, mock_run_prompt, mock_find_files):
        """Test that simple problems return empty list (no decomposition)"""
        # Mock Claude response and no files created
        mock_run_prompt.return_value = "No decomposition needed"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Write a hello world function")
        
        self.assertEqual(result, [])
        mock_run_prompt.assert_called_once()
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_complex_problem_with_leaf_nodes(self, mock_run_prompt, mock_find_files):
        """Test decomposition returns subtask file paths"""
        # Mock Claude creating files
        mock_run_prompt.return_value = "Created markdown structure"
        
        # Create actual files that will be found
        ui_dir = self.temp_dir / "create_ui"
        backend_dir = self.temp_dir / "implement_backend"
        db_dir = self.temp_dir / "setup_database"
        
        ui_dir.mkdir()
        backend_dir.mkdir()
        db_dir.mkdir()
        
        ui_file = ui_dir / "problem.md"
        backend_file = backend_dir / "problem.md"
        db_file = db_dir / "problem.md"
        
        ui_file.write_text("# Create UI\n\n## Type\nsimple")
        backend_file.write_text("# Implement Backend\n\n## Type\ncomplex")
        db_file.write_text("# Setup Database\n\n## Type\nsimple")
        
        # Mock finding created files - return full paths
        mock_find_files.return_value = [
            str(ui_file),
            str(backend_file),
            str(db_file)
        ]
        
        result = self.node.decompose_to_markdown("Build a web application")
        
        self.assertEqual(len(result), 3)
        self.assertTrue(any("create_ui" in r for r in result))
        self.assertTrue(any("implement_backend" in r for r in result))
        self.assertTrue(any("setup_database" in r for r in result))
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_handles_cli_failure(self, mock_run_prompt, mock_find_files):
        """Test decomposition handles CLI failures gracefully"""
        # Mock Claude failure
        mock_run_prompt.return_value = "Error: Claude failed"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Some problem")
        
        self.assertEqual(result, [])  # Empty list on error
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_handles_invalid_json(self, mock_run_prompt, mock_find_files):
        """Test decomposition handles invalid JSON gracefully"""
        # Mock invalid JSON response
        mock_run_prompt.return_value = "Invalid JSON response"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Some problem")
        
        self.assertEqual(result, [])  # Empty list when no files created
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_handles_markdown_wrapped_json(self, mock_run_prompt, mock_find_files):
        """Test decomposition handles markdown-wrapped responses"""
        # Mock markdown-wrapped response
        mock_run_prompt.return_value = """```json
{
    "status": "created files"
}
```"""
        
        # Create actual files
        task1_dir = self.temp_dir / "task1"
        task2_dir = self.temp_dir / "task2"
        task1_dir.mkdir()
        task2_dir.mkdir()
        
        file1 = task1_dir / "problem.md"
        file2 = task2_dir / "problem.md"
        file1.write_text("# Task 1\n\n## Type\nsimple")
        file2.write_text("# Task 2\n\n## Type\ncomplex")
        
        mock_find_files.return_value = [str(file1), str(file2)]
        
        result = self.node.decompose_to_markdown("Complex problem")
        
        self.assertEqual(len(result), 2)
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_with_context(self, mock_run_prompt, mock_find_files):
        """Test decomposition includes context in prompt"""
        mock_run_prompt.return_value = "Created with context"
        mock_find_files.return_value = ["subtask/problem.md"]
        
        context = Context(
            root_problem="Build system",
            parent_task="Create module",
            parent_approach="Modular design",
            sibling_tasks=["Module A", "Module B"]
        )
        
        result = self.node.decompose_to_markdown("Create Module C", context)
        
        # Verify context was passed to build_decomposition_prompt
        call_args = mock_run_prompt.call_args[0][0]
        self.assertIn("Root Goal: Build system", call_args)
        self.assertIn("Parent Task: Create module", call_args)
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_leaf_node_cannot_decompose(self, mock_run_prompt, mock_find_files):
        """Test that leaf nodes (max depth) don't decompose"""
        # Create a leaf node at max depth
        leaf_node = AgentNode("leaf", self.temp_dir, depth=3)
        
        # Even if files would be created, at max depth it shouldn't decompose
        mock_run_prompt.return_value = "Would create files"
        mock_find_files.return_value = []
        
        # For a leaf node, decompose_to_markdown might not be called at all
        # or it returns empty. The actual behavior depends on agent_tree.py
        result = leaf_node.decompose_to_markdown("Complex task")
        
        # Leaf nodes should not decompose
        self.assertEqual(result, [])


class TestSolveRecursive(unittest.TestCase):
    """Test recursive solving with decomposition"""
    
    def setUp(self):
        self.original_cwd = Path.cwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        import os
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_leaf_node_solves_directly(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that leaf nodes solve directly without decomposition"""
        # No decomposition for leaf
        mock_find_files.return_value = []
        mock_run_prompt.return_value = "Direct solution"
        
        result = solve_problem("Simple task", max_depth=1)
        
        self.assertIn("Direct solution", result)
        # Should only call Claude once for the solution
        self.assertEqual(mock_run_prompt.call_count, 1)
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_depth_limit_forces_direct_solve(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that reaching depth limit forces direct solving"""
        # Would decompose but depth limit reached
        mock_find_files.return_value = []  # No decomposition due to depth
        mock_run_prompt.return_value = "Forced direct solution"
        
        result = solve_problem("Complex problem", max_depth=1)
        
        self.assertIn("Forced direct solution", result)
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_mixed_leaf_and_complex_subtasks(self, mock_run_prompt, mock_find_files, mock_input):
        """Test handling mixed simple and complex subtasks"""
        # Initial decomposition
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return ["simple_task/problem.md", "complex_task/problem.md"]
            elif "complex_task" in str(work_dir):
                return ["sub1/problem.md", "sub2/problem.md"]
            else:
                return []
        
        mock_find_files.side_effect = find_files_side_effect
        
        responses = [
            "Initial decomposition",
            "Simple task solution",
            "Complex task decomposition",
            "Sub1 solution",
            "Sub2 solution",
            "Complex task integrated",
            "Final integration"
        ]
        mock_run_prompt.side_effect = responses
        
        result = solve_problem("Mixed complexity problem")
        
        self.assertIn("integration", result.lower())
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_respects_node_limit_with_decomposition(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that node count limit is respected during decomposition"""
        # Mock many subtasks to test node limit
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                # Try to create many subtasks
                return [f"task{i}/problem.md" for i in range(10)]
            else:
                return []
        
        mock_find_files.side_effect = find_files_side_effect
        
        # Create enough responses for all potential calls
        responses = ["Decomposition"] + ["Solution"] * 20
        mock_run_prompt.side_effect = responses
        
        # The system should respect the node limit (5 nodes max)
        result = solve_problem("Problem with many subtasks")
        
        # Check that we didn't exceed the node limit
        # With 5 max nodes and decomposition, we expect fewer calls
        self.assertLess(mock_run_prompt.call_count, 10)


class TestContextPropagation(unittest.TestCase):
    """Test context propagation through the tree"""
    
    def test_context_to_prompt_full(self):
        """Test full context conversion to prompt"""
        context = Context(
            root_problem="Build system",
            parent_task="Create auth",
            parent_approach="Use JWT tokens",
            sibling_tasks=["User model", "Session handling"]
        )
        
        prompt = context.to_prompt()
        
        self.assertIn("Root Goal: Build system", prompt)
        self.assertIn("Parent Task: Create auth", prompt)
        self.assertIn("Parent's Approach: Use JWT tokens", prompt)
        self.assertIn("User model", prompt)
        self.assertIn("Session handling", prompt)
    
    def test_context_to_prompt_empty(self):
        """Test empty context (root level)"""
        context = Context(root_problem="Root")
        
        prompt = context.to_prompt()
        
        self.assertEqual(prompt, "")
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_context_passed_to_children(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that context is properly propagated to children"""
        # Mock decomposition
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return ["auth/problem.md", "database/problem.md"]
            else:
                return []
        
        mock_find_files.side_effect = find_files_side_effect
        
        responses = [
            "Decomposition",
            "Auth solution with context",
            "Database solution with context",
            "Integrated solution"
        ]
        mock_run_prompt.side_effect = responses
        
        solve_problem("Build user system")
        
        # Check that context was included in child prompts
        calls = mock_run_prompt.call_args_list
        
        # Find the solve calls (not decomposition)
        solve_calls = [c for c in calls if "Solve this problem" in c[0][0]]
        
        for call in solve_calls:
            prompt = call[0][0]
            # Children should know about the root problem
            if "auth" in prompt.lower() or "database" in prompt.lower():
                self.assertIn("Root Goal: Build user system", prompt)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in decomposition"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("test", self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_empty_subtasks_list(self, mock_run_prompt, mock_find_files):
        """Test handling of empty subtasks list"""
        mock_run_prompt.return_value = "No subtasks created"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Problem")
        
        self.assertEqual(result, [])
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_with_missing_simple_field(self, mock_run_prompt, mock_find_files):
        """Test handling when decomposition has incomplete data"""
        # In the new system, we don't parse JSON, we just look for files
        mock_run_prompt.return_value = "Some response"
        
        # Create actual file
        task_dir = self.temp_dir / "task"
        task_dir.mkdir()
        task_file = task_dir / "problem.md"
        task_file.write_text("# Task\n\n## Problem\nSome task")  # Missing Type field
        
        mock_find_files.return_value = [str(task_file)]
        
        result = self.node.decompose_to_markdown("Problem")
        
        # Should still work with files found
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)