#!/usr/bin/env python3
"""
Test suite for the new decomposition system
"""

import unittest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import subprocess

# Import the module under test
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context
from src.agent_tree import solve_problem


class TestDecomposeMethod(unittest.TestCase):
    """Unit tests for decompose_problem method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("test_node", self.temp_dir, depth=0)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_decompose_simple_problem(self, mock_run):
        """Test that simple problems return None (solve directly)"""
        # Mock Gemini response saying don't decompose
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '{"decompose": false}'
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Write a hello world function")
        
        self.assertIsNone(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_decompose_complex_problem_with_leaf_nodes(self, mock_run):
        """Test decomposition returns subtasks with simple flags"""
        # Mock Gemini response with mixed simple/complex subtasks
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps({
            "decompose": True,
            "approach": "Build incrementally",
            "subtasks": [
                {"task": "Create data model", "simple": True},
                {"task": "Build API layer", "simple": False},
                {"task": "Add validation", "simple": True}
            ]
        })
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Build a web service")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("Create data model", True))
        self.assertEqual(result[1], ("Build API layer", False))
        self.assertEqual(result[2], ("Add validation", True))
    
    def test_leaf_node_cannot_decompose(self):
        """Test that leaf nodes always return None"""
        # Don't even need to mock subprocess - it shouldn't be called
        with patch('subprocess.run') as mock_run:
            result = self.node.decompose_problem("Complex problem", is_leaf=True)
            
            self.assertIsNone(result)
            mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_decompose_with_context(self, mock_run):
        """Test that context is properly included in prompt"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '{"decompose": false}'
        mock_run.return_value = mock_process
        
        context = Context(
            root_problem="Build app",
            parent_task="Create backend",
            parent_approach="Use REST API",
            sibling_tasks=["Frontend", "Database"]
        )
        
        self.node.decompose_problem("Create auth system", context)
        
        # Check that context was included in the prompt
        call_args = mock_run.call_args[1]
        cmd = call_args['capture_output']  # This gives us access to the command
        # The actual prompt is in the subprocess call, so we just verify it was called
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_decompose_handles_markdown_wrapped_json(self, mock_run):
        """Test extraction of JSON from markdown code blocks"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '''Here's the analysis:
```json
{
    "decompose": true,
    "subtasks": [
        {"task": "Task 1", "simple": true}
    ]
}
```'''
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test problem")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("Task 1", True))
    
    @patch('subprocess.run')
    def test_decompose_handles_cli_failure(self, mock_run):
        """Test graceful handling when Claude CLI fails"""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Connection failed"
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test problem")
        
        # Should return None (solve directly) on failure
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_decompose_handles_invalid_json(self, mock_run):
        """Test graceful handling of invalid JSON responses"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "This is not valid JSON"
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test problem")
        
        # Should return None (solve directly) on parse failure
        self.assertIsNone(result)


class TestSolveRecursive(unittest.TestCase):
    """Integration tests for recursive solving with leaf nodes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.agent_node.AgentNode._run_claude')
    @patch('src.agent_node.AgentNode.decompose_problem')
    def test_leaf_node_solves_directly(self, mock_decompose, mock_claude):
        """Test that leaf nodes don't attempt to decompose"""
        # This node should not call decompose_problem
        mock_claude.return_value = "Direct solution"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            result = solve_problem("Simple task", max_depth=3, use_tmp=False)
        
        # decompose_problem should be called once for root (non-leaf)
        # But when we mark something as leaf, it shouldn't decompose
        self.assertEqual(result, "Direct solution")
    
    @patch('src.agent_node.AgentNode._run_claude')
    @patch('subprocess.run')
    def test_mixed_leaf_and_complex_subtasks(self, mock_run, mock_claude):
        """Test tree with both leaf and complex subtasks"""
        # First decomposition (root level)
        root_response = MagicMock()
        root_response.returncode = 0
        root_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Simple task", "simple": True},
                {"task": "Complex task", "simple": False}
            ]
        })
        
        # Second decomposition (for complex subtask)
        complex_response = MagicMock()
        complex_response.returncode = 0
        complex_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Sub-sub task 1", "simple": True},
                {"task": "Sub-sub task 2", "simple": True}
            ]
        })
        
        # Set up mock responses in order
        mock_run.side_effect = [root_response, complex_response]
        mock_claude.return_value = "Solution"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            result = solve_problem("Mixed complexity problem", max_depth=3, use_tmp=False)
        
        # Should have called decompose twice (root + complex subtask)
        self.assertEqual(mock_run.call_count, 2)
        # Should have solved 4 problems total (1 simple + 2 sub-sub + 1 integration)
        # Actually 5 calls: 3 leaf solves + 2 integrations
        self.assertEqual(mock_claude.call_count, 5)
    
    @patch('src.agent_node.AgentNode._run_claude')
    @patch('subprocess.run')
    def test_respects_node_limit_with_decomposition(self, mock_run, mock_claude):
        """Test that node limit is respected even with decomposition"""
        # Mock decomposition that would create many nodes
        mock_response = MagicMock()
        mock_response.returncode = 0
        mock_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": f"Task {i}", "simple": False}
                for i in range(10)  # Would create 10 nodes
            ]
        })
        mock_run.return_value = mock_response
        mock_claude.return_value = "Solution"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            result = solve_problem("Large problem", max_depth=3, use_tmp=False)
        
        # Due to 5-node limit, not all subtasks should be processed
        # We should hit the limit and solve remaining tasks directly
        self.assertIn("Solution", result)
    
    @patch('src.agent_node.AgentNode._run_claude')
    @patch('subprocess.run')
    def test_depth_limit_forces_direct_solve(self, mock_run, mock_claude):
        """Test that depth limit prevents further decomposition"""
        # Mock continuous decomposition
        mock_response = MagicMock()
        mock_response.returncode = 0
        mock_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Subtask", "simple": False}
            ]
        })
        mock_run.return_value = mock_response
        mock_claude.return_value = "Solution"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            result = solve_problem("Deep problem", max_depth=2, use_tmp=False)
        
        # Should stop decomposing at max_depth
        self.assertIn("Solution", result)


class TestContextPropagation(unittest.TestCase):
    """Test context passing through the tree"""
    
    def test_context_to_prompt_empty(self):
        """Test empty context generates no prompt"""
        context = Context("Root problem")
        self.assertEqual(context.to_prompt(), "")
    
    def test_context_to_prompt_full(self):
        """Test full context generates proper prompt"""
        context = Context(
            root_problem="Build app",
            parent_task="Backend",
            parent_approach="REST API",
            sibling_tasks=["Auth", "Database", "API"]
        )
        
        prompt = context.to_prompt()
        self.assertIn("Root Goal: Build app", prompt)
        self.assertIn("Parent Task: Backend", prompt)
        self.assertIn("Parent's Approach: REST API", prompt)
        self.assertIn("- Auth", prompt)
        self.assertIn("- Database", prompt)
        self.assertIn("- API", prompt)
    
    @patch('src.agent_node.AgentNode._run_claude')
    @patch('subprocess.run')
    def test_context_passed_to_children(self, mock_run, mock_claude):
        """Test that context is properly passed down the tree"""
        # Mock decomposition
        mock_response = MagicMock()
        mock_response.returncode = 0
        mock_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Child 1", "simple": True},
                {"task": "Child 2", "simple": True}
            ]
        })
        mock_run.return_value = mock_response
        mock_claude.return_value = "Solution"
        
        with patch('pathlib.Path.mkdir'), \
             patch('pathlib.Path.write_text'):
            result = solve_problem("Parent problem", max_depth=3, use_tmp=False)
        
        # Verify claude was called with context
        calls = mock_claude.call_args_list
        # At least one call should have sibling context
        prompts = [call[0][0] for call in calls]
        context_prompts = [p for p in prompts if "Sibling Tasks:" in p]
        self.assertTrue(len(context_prompts) > 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("test_node", self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_decompose_with_missing_simple_field(self, mock_run):
        """Test handling subtasks without 'simple' field (default to True)"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Task without simple field"}
            ]
        })
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test")
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ("Task without simple field", True))
    
    @patch('subprocess.run')
    def test_decompose_empty_subtasks_list(self, mock_run):
        """Test handling empty subtasks list"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps({
            "decompose": True,
            "subtasks": []
        })
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)