#!/usr/bin/env python3
"""
Comprehensive test suite for agent_tree_simple.py

Following best testing principles:
- Unit tests for individual components
- Integration tests for full workflows
- Mock external dependencies (claude CLI)
- Test edge cases and error conditions
- Clear test organization and naming
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
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context
from src.agent_tree import solve_problem


class TestAgentNode(unittest.TestCase):
    """Unit tests for AgentNode class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("test_node", self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_work_directory(self):
        """Test that AgentNode creates its work directory"""
        self.assertTrue(self.temp_dir.exists())
        self.assertTrue(self.temp_dir.is_dir())
    
    def test_init_with_nested_path(self):
        """Test that AgentNode can create nested directories"""
        nested_path = self.temp_dir / "level1" / "level2"
        node = AgentNode("nested_node", nested_path)
        self.assertTrue(nested_path.exists())
    
    @patch('subprocess.Popen')
    def test_run_claude_success(self, mock_popen):
        """Test successful claude CLI execution"""
        # Mock successful subprocess result
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Test output\n", ""]
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = self.node._run_claude("test prompt")
        
        self.assertEqual(result, "Test output")
        mock_popen.assert_called_once()
        
        # Verify the command structure
        call_args = mock_popen.call_args
        cmd = call_args[0][0]
        self.assertEqual(cmd[0], "claude")
        self.assertEqual(cmd[1], "--dangerously-skip-permissions")
        self.assertEqual(cmd[2], "-p")
        self.assertEqual(cmd[3], "test prompt")
    
    @patch('subprocess.Popen')
    def test_run_claude_failure(self, mock_popen):
        """Test claude CLI failure handling"""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [""]
        mock_process.wait.return_value = None
        mock_process.returncode = 1
        mock_process.stderr.read.return_value = "Command failed"
        mock_popen.return_value = mock_process
        
        result = self.node._run_claude("test prompt")
        
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Command failed", result)
    
    @patch('subprocess.Popen')
    def test_run_claude_timeout(self, mock_popen):
        """Test claude CLI timeout handling"""
        # This test is no longer applicable since Popen doesn't have timeout
        # But we can test exception handling
        mock_popen.side_effect = Exception("Timeout")
        
        result = self.node._run_claude("test prompt")
        
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Timeout", result)
    
    @patch('subprocess.Popen')
    def test_run_claude_exception(self, mock_popen):
        """Test claude CLI exception handling"""
        mock_popen.side_effect = Exception("Unexpected error")
        
        result = self.node._run_claude("test prompt")
        
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Unexpected error", result)
    
    @patch('subprocess.Popen')
    def test_run_claude_with_prompt(self, mock_popen):
        """Test that _run_claude passes prompt correctly"""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["output line 1\n", "output line 2\n", ""]
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = self.node._run_claude("test prompt")
        
        # Check command was called with prompt
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertIn("claude", args)
        self.assertIn("test prompt", args)
        self.assertEqual(result, "output line 1\noutput line 2")
    
    @patch('subprocess.run')
    def test_decompose_returns_none_for_simple(self, mock_run):
        """Test decomposition returns None for simple problems"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '{"decompose": false}'
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Write a hello world function")
        
        self.assertIsNone(result)  # Simple problems return None
    
    @patch('subprocess.run')
    def test_decompose_returns_subtasks(self, mock_run):
        """Test decomposition returns subtasks with labels"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_response = {
            "decompose": True,
            "subtasks": [
                {"task": "Create user interface", "simple": True},
                {"task": "Implement backend", "simple": False},
                {"task": "Setup database", "simple": True}
            ]
        }
        mock_process.stdout = json.dumps(mock_response)
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Build a web application")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("Create user interface", True))
        self.assertEqual(result[1], ("Implement backend", False))
        self.assertEqual(result[2], ("Setup database", True))
    
    @patch('subprocess.run')
    def test_decompose_handles_invalid_json(self, mock_run):
        """Test decomposition handles invalid JSON gracefully"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Invalid JSON response"
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Some problem")
        
        self.assertIsNone(result)  # Invalid JSON defaults to None
    
    @patch.object(AgentNode, '_run_claude')
    def test_solve_simple(self, mock_run_claude):
        """Test solving a simple problem"""
        mock_run_claude.return_value = "Here's the solution: print('Hello World')"
        
        result = self.node.solve_simple("Write a hello world program")
        
        self.assertIn("Hello World", result)
        mock_run_claude.assert_called_once()
    
    @patch.object(AgentNode, '_run_claude')
    def test_solve_simple_with_context(self, mock_run_claude):
        """Test solving a simple problem with context"""
        mock_run_claude.return_value = "Solution with context"
        
        context = Context(
            root_problem="Build user system",
            parent_task="Create auth module",
            parent_approach="Split into model, auth, and session",
            sibling_tasks=["User model", "Session management"]
        )
        result = self.node.solve_simple("Add user authentication", context)
        
        # Verify context was included in the prompt
        call_args = mock_run_claude.call_args[0][0]
        self.assertIn("Root Goal: Build user system", call_args)
        self.assertIn("Parent Task: Create auth module", call_args)
        self.assertIn("Add user authentication", call_args)
    
    @patch.object(AgentNode, '_run_claude')
    def test_integrate_solutions(self, mock_run_claude):
        """Test solution integration"""
        mock_run_claude.return_value = "Integrated solution"
        
        solutions = [
            ("Task 1", "Solution 1"),
            ("Task 2", "Solution 2")
        ]
        
        result = self.node.integrate_solutions("Original problem", solutions)
        
        self.assertEqual(result, "Integrated solution")
        
        # Verify the prompt includes all solutions
        call_args = mock_run_claude.call_args[0][0]
        self.assertIn("Original problem", call_args)
        self.assertIn("Task 1", call_args)
        self.assertIn("Solution 1", call_args)
        self.assertIn("Task 2", call_args)
        self.assertIn("Solution 2", call_args)


class TestSolveProblem(unittest.TestCase):
    """Integration tests for the main solve_problem function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.original_cwd = Path.cwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        # Change to temp directory to avoid cluttering the real workspace
        import os
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(AgentNode, '_run_claude')
    def test_solve_simple_problem_end_to_end(self, mock_run_claude):
        """Test solving a simple problem end-to-end"""
        # Mock the decomposition to return simple (no decomposition needed)
        mock_run_claude.return_value = '{"decompose": false}'
        
        # Mock the solution
        def side_effect(prompt, mode="ephemeral"):
            if '"decompose"' in prompt:
                return '{"decompose": false}'
            else:
                return "def hello_world():\n    print('Hello, World!')"
        
        mock_run_claude.side_effect = side_effect
        
        result = solve_problem("Write a hello world function")
        
        self.assertIn("Hello, World!", result)
        
        # Verify workspace was created (could be in current directory during tests)
        workspaces = list(Path("tmp").glob("agent_tree_*"))
        self.assertGreaterEqual(len(workspaces), 1)
        
        workspace = workspaces[0]
        # The mocked Claude doesn't actually create files, so we just verify the workspace exists
        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / "root").exists())
    
    @patch.object(AgentNode, '_run_claude')
    @patch('subprocess.run')
    def test_solve_complex_problem_end_to_end(self, mock_run, mock_run_claude):
        """Test solving a complex problem with decomposition"""
        
        # Mock decomposition for main problem
        main_decompose = MagicMock()
        main_decompose.returncode = 0
        main_decompose.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Create UI", "simple": True},
                {"task": "Setup backend", "simple": True}
            ]
        })
        mock_run.return_value = main_decompose
        
        def side_effect(prompt, mode="ephemeral"):
            # Solving Create UI subtask
            if "Create UI" in prompt and "Solve this problem" in prompt:
                return "UI: React component with form"
            
            # Solving Setup backend subtask  
            elif "Setup backend" in prompt and "Solve this problem" in prompt:
                return "Backend: Express.js server with routes"
            
            # Integration step
            elif "Integrate these" in prompt or ("Sub-solutions:" in prompt and "Original problem:" in prompt):
                return "Complete web app with UI and backend integrated"
            
            # Fallback
            else:
                return "Generic solution"
        
        mock_run_claude.side_effect = side_effect
        
        result = solve_problem("Build a simple web application")
        
        self.assertIn("integrated", result.lower())
        
        # Verify the tree structure was created
        workspaces = list(Path("tmp").glob("agent_tree_*"))
        self.assertTrue(len(workspaces) >= 1)
        
        # Find the most recent workspace
        workspace = max(workspaces, key=lambda p: p.stat().st_mtime)
        self.assertTrue((workspace / "root").exists())
        self.assertTrue((workspace / "root" / "sub1").exists())
        self.assertTrue((workspace / "root" / "sub2").exists())
    
    @patch.object(AgentNode, '_run_claude')
    def test_max_depth_limit(self, mock_run_claude):
        """Test that max depth limit is respected"""
        # Always return complex to test depth limiting
        mock_run_claude.return_value = '{"decompose": true, "approach": "Decompose", "subtasks": [{"task": "Sub 1", "simple": false}, {"task": "Sub 2", "simple": false}]}'
        
        def side_effect(prompt, mode="ephemeral"):
            if '"decompose"' in prompt:
                return '{"decompose": true, "approach": "Decompose", "subtasks": [{"task": "Sub 1", "simple": false}, {"task": "Sub 2", "simple": false}]}'
            else:
                return "Forced simple solution due to depth limit"
        
        mock_run_claude.side_effect = side_effect
        
        result = solve_problem("Complex problem", max_depth=1)
        
        # Should solve directly due to depth limit
        self.assertIn("depth limit", result.lower())
    


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("error_test", self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(AgentNode, '_run_claude')
    def test_empty_problem(self, mock_run_claude):
        """Test handling of empty problem string"""
        mock_run_claude.return_value = "Empty problem handled"
        
        result = self.node.solve_simple("")
        
        self.assertIsInstance(result, str)
        mock_run_claude.assert_called_once()
    
    @patch.object(AgentNode, '_run_claude')
    def test_very_long_problem(self, mock_run_claude):
        """Test handling of very long problem descriptions"""
        long_problem = "A" * 10000  # Very long problem
        mock_run_claude.return_value = "Long problem handled"
        
        result = self.node.solve_simple(long_problem)
        
        self.assertEqual(result, "Long problem handled")
    
    @patch.object(AgentNode, '_run_claude')
    def test_special_characters_in_problem(self, mock_run_claude):
        """Test handling of special characters in problem description"""
        special_problem = "Problem with 'quotes' and \"double quotes\" and \n newlines"
        mock_run_claude.return_value = "Special chars handled"
        
        result = self.node.solve_simple(special_problem)
        
        self.assertEqual(result, "Special chars handled")
    
    @patch('subprocess.run')
    def test_malformed_json_in_decomposition(self, mock_run):
        """Test handling of malformed JSON in decomposition"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = '{"decompose": true, "subtasks": [incomplete'
        mock_run.return_value = mock_process
        
        result = self.node.decompose_problem("Test problem")
        
        # Should default to None when JSON is malformed
        self.assertIsNone(result)


class TestContext(unittest.TestCase):
    """Test context passing functionality"""
    
    def test_context_creation(self):
        """Test Context object creation and string representation"""
        context = Context(
            root_problem="Build a system",
            parent_task="Create module",
            parent_approach="Split into parts",
            sibling_tasks=["Part 1", "Part 2"]
        )
        
        prompt = context.to_prompt()
        
        self.assertIn("Root Goal: Build a system", prompt)
        self.assertIn("Parent Task: Create module", prompt)
        self.assertIn("Parent's Approach: Split into parts", prompt)
        self.assertIn("Part 1", prompt)
        self.assertIn("Part 2", prompt)
    
    def test_empty_context(self):
        """Test context with no parent task"""
        context = Context(root_problem="Root task")
        
        prompt = context.to_prompt()
        
        self.assertEqual(prompt, "")  # Empty when no parent
    
    @patch.object(AgentNode, '_call_gemini_for_decomposition')
    @patch.object(AgentNode, '_run_claude')
    def test_context_passed_to_children(self, mock_run_claude, mock_gemini):
        """Test that context is properly passed down the tree"""
        # Mock the decomposition to return subtasks
        mock_gemini.return_value = [("Task A", True), ("Task B", True)]
        
        # Set up responses for Claude calls
        responses = [
            # Task A solution (leaf node, no decomposition)
            "Solution A with context awareness",
            # Task B solution (leaf node, no decomposition)
            "Solution B with context awareness",
            # Integration
            "Integrated solution"
        ]
        
        mock_run_claude.side_effect = responses
        
        result = solve_problem("Root problem")
        
        # Check that context was passed in the prompts
        calls = mock_run_claude.call_args_list
        
        # Find the Task A solve call
        task_a_solve_call = None
        for call in calls:
            if len(call[0]) > 0 and "Task A" in call[0][0] and "Root Goal: Root problem" in call[0][0]:
                task_a_solve_call = call
                break
        
        self.assertIsNotNone(task_a_solve_call, "Context should be passed to child tasks")
        
        # Verify the context content
        prompt = task_a_solve_call[0][0]
        self.assertIn("Root Goal: Root problem", prompt)
        self.assertIn("Parent Task: Root problem", prompt)
        # Parent's approach is now empty in the new implementation
        self.assertIn("Task B", prompt)  # Should know about sibling


class TestIntegration(unittest.TestCase):
    """Integration tests that test the system as a whole"""
    
    def setUp(self):
        self.original_cwd = Path.cwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        import os
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    @patch.object(AgentNode, '_run_claude')
    def test_realistic_workflow(self, mock_run_claude, mock_run):
        """Test a realistic problem-solving workflow"""
        # Mock decomposition response
        decompose_response = MagicMock()
        decompose_response.returncode = 0
        decompose_response.stdout = json.dumps({
            "decompose": True,
            "subtasks": [
                {"task": "Design data model", "simple": True},
                {"task": "Create API endpoints", "simple": True},
                {"task": "Build frontend", "simple": True}
            ]
        })
        mock_run.return_value = decompose_response
        
        # Mock solution responses
        responses = [
            # Subtask 1 solution
            "Data model: User table with id, name, email fields",
            # Subtask 2 solution
            "API: REST endpoints for CRUD operations on users",
            # Subtask 3 solution
            "Frontend: React app with user management interface",
            # Integration
            "Complete user management system with database, API, and frontend"
        ]
        
        mock_run_claude.side_effect = responses
        
        result = solve_problem("Create a user management system")
        
        # Verify the final result contains integrated solution
        self.assertIn("Complete user management system", result)
        
        # Verify all claude calls were made
        self.assertEqual(mock_run_claude.call_count, len(responses))
        
        # Verify workspace structure
        workspaces = list(Path("tmp").glob("agent_tree_*"))
        self.assertEqual(len(workspaces), 1)
        
        workspace = workspaces[0]
        # The mocked Claude doesn't actually create files, so we just verify the workspace structure
        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / "root").exists())


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)