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
from unittest.mock import patch, MagicMock, call, mock_open
from pathlib import Path
import subprocess

# Import the module under test
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context
from src.agent_tree import solve_problem
from src.claude_client import ClaudeClient
from src.markdown_utils import generate_problem_name, find_subproblem_files
from src.prompts import build_decomposition_prompt


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
    def test_claude_client_run_prompt_success(self, mock_popen):
        """Test successful claude CLI execution via ClaudeClient"""
        # Mock successful subprocess result
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Test output\n", ""]
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = self.node.claude.run_prompt("test prompt")
        
        self.assertEqual(result, "Test output")
        mock_popen.assert_called_once()
        
        # Verify the command structure
        call_args = mock_popen.call_args[0][0]
        self.assertEqual(call_args[0], "claude")
        self.assertEqual(call_args[1], "--dangerously-skip-permissions")
        self.assertEqual(call_args[2], "-p")
        self.assertEqual(call_args[3], "test prompt")
    
    @patch('subprocess.Popen')
    def test_claude_client_run_prompt_failure(self, mock_popen):
        """Test claude CLI failure handling"""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [""]
        mock_process.wait.return_value = None
        mock_process.returncode = 1
        mock_process.stderr.read.return_value = "Command failed"
        mock_popen.return_value = mock_process
        
        result = self.node.claude.run_prompt("test prompt")
        
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Command failed", result)
    
    @patch('subprocess.Popen')
    def test_claude_client_run_prompt_exception(self, mock_popen):
        """Test claude CLI exception handling"""
        mock_popen.side_effect = Exception("Unexpected error")
        
        result = self.node.claude.run_prompt("test prompt")
        
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Unexpected error", result)
    
    @patch('subprocess.Popen')
    def test_claude_client_with_multiple_output_lines(self, mock_popen):
        """Test that ClaudeClient handles multiple output lines"""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["output line 1\n", "output line 2\n", ""]
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = self.node.claude.run_prompt("test prompt")
        
        # Check command was called with prompt
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertIn("claude", args)
        self.assertIn("test prompt", args)
        self.assertEqual(result, "output line 1\noutput line 2")
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_to_markdown_returns_files(self, mock_run_prompt, mock_find_files):
        """Test decompose_to_markdown returns list of created files"""
        # Mock Claude creating markdown files
        mock_run_prompt.return_value = "Created markdown files"
        
        # Create the proper directory structure that find_subproblem_files expects
        problem_name = "test_problem"
        subproblems_dir = self.temp_dir / problem_name / "subproblems"
        subproblems_dir.mkdir(parents=True)
        
        file1 = subproblems_dir / "01_subtask_one.md"
        file2 = subproblems_dir / "02_subtask_two.md"
        file1.write_text("# Subtask One\n\n## Type\nsimple")
        file2.write_text("# Subtask Two\n\n## Type\ncomplex")
        
        # Mock finding the created files - return full paths
        mock_find_files.return_value = [
            str(file1),
            str(file2)
        ]
        
        result = self.node.decompose_to_markdown("Test problem")
        
        self.assertEqual(len(result), 2)
        self.assertTrue(any("01_subtask_one.md" in r for r in result))
        self.assertTrue(any("02_subtask_two.md" in r for r in result))
        
        # Verify find_subproblem_files was called with correct args
        mock_find_files.assert_called_once()
        call_args = mock_find_files.call_args[0]
        self.assertEqual(call_args[0], self.temp_dir)  # work_dir
        self.assertEqual(call_args[1], problem_name)  # problem_name
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decompose_to_markdown_empty_result(self, mock_run_prompt, mock_find_files):
        """Test decompose_to_markdown when no files are created"""
        mock_run_prompt.return_value = "No decomposition needed"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Simple problem")
        
        self.assertEqual(result, [])
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_solve_simple(self, mock_run_prompt):
        """Test solving a simple problem"""
        mock_run_prompt.return_value = "Here's the solution: print('Hello World')"
        
        result = self.node.solve_simple("Write a hello world program")
        
        self.assertIn("Hello World", result)
        mock_run_prompt.assert_called_once()
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_solve_simple_with_context(self, mock_run_prompt):
        """Test solving a simple problem with context"""
        mock_run_prompt.return_value = "Solution with context"
        
        context = Context(
            root_problem="Build user system",
            parent_task="Create auth module",
            parent_approach="Split into model, auth, and session",
            sibling_tasks=["User model", "Session management"]
        )
        result = self.node.solve_simple("Add user authentication", context)
        
        # Verify context was included in the prompt
        call_args = mock_run_prompt.call_args[0][0]
        self.assertIn("Root Goal: Build user system", call_args)
        self.assertIn("Parent Task: Create auth module", call_args)
        self.assertIn("Add user authentication", call_args)
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_integrate_solutions(self, mock_run_prompt):
        """Test solution integration"""
        mock_run_prompt.return_value = "Integrated solution"
        
        solutions = [
            ("Task 1", "Solution 1"),
            ("Task 2", "Solution 2")
        ]
        
        result = self.node.integrate_solutions("Original problem", solutions)
        
        self.assertEqual(result, "Integrated solution")
        
        # Verify the prompt includes all solutions
        call_args = mock_run_prompt.call_args[0][0]
        self.assertIn("Original problem", call_args)
        self.assertIn("Task 1", call_args)
        self.assertIn("Solution 1", call_args)
        self.assertIn("Task 2", call_args)
        self.assertIn("Solution 2", call_args)
    
    def test_is_problem_complex(self):
        """Test is_problem_complex method"""
        # Create test markdown files
        simple_file = self.temp_dir / "simple.md"
        simple_file.write_text("# Task\n\n## Type\nsimple\n")
        
        complex_file = self.temp_dir / "complex.md"
        complex_file.write_text("# Task\n\n## Type\ncomplex\n")
        
        self.assertFalse(self.node.is_problem_complex(str(simple_file)))
        self.assertTrue(self.node.is_problem_complex(str(complex_file)))


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
    
    @patch('builtins.input', return_value='')  # Mock pressing Enter to continue
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_solve_simple_problem_end_to_end(self, mock_run_prompt, mock_find_files, mock_input):
        """Test solving a simple problem end-to-end"""
        # Mock no decomposition (empty file list)
        mock_find_files.return_value = []
        
        # Mock the solution
        mock_run_prompt.return_value = "def hello_world():\n    print('Hello, World!')"
        
        result = solve_problem("Write a hello world function")
        
        self.assertIn("Hello, World!", result)
        
        # Verify workspace was created
        workspaces = list(Path(".").glob("agent_tree_*"))
        self.assertGreaterEqual(len(workspaces), 1)
        
        workspace = workspaces[0]
        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / "root").exists())
    
    @patch('builtins.input', return_value='')  # Mock pressing Enter to continue
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_solve_complex_problem_end_to_end(self, mock_run_prompt, mock_find_files, mock_input):
        """Test solving a complex problem with decomposition"""
        
        # First call - decomposition creates files
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return ["sub1/problem.md", "sub2/problem.md"]
            else:
                return []  # Leaf nodes don't decompose further
        
        mock_find_files.side_effect = find_files_side_effect
        
        # Mock Claude responses
        responses = [
            # Initial decomposition
            "Created markdown structure",
            # Solving sub1
            "UI: React component with form",
            # Solving sub2  
            "Backend: Express.js server with routes",
            # Integration
            "Complete web app with UI and backend integrated"
        ]
        
        mock_run_prompt.side_effect = responses
        
        result = solve_problem("Build a simple web application")
        
        self.assertIn("integrated", result.lower())
        
        # Verify the tree structure was created
        workspaces = list(Path(".").glob("agent_tree_*"))
        self.assertTrue(len(workspaces) >= 1)
        
        workspace = max(workspaces, key=lambda p: p.stat().st_mtime)
        self.assertTrue((workspace / "root").exists())
        self.assertTrue((workspace / "root" / "sub1").exists())
        self.assertTrue((workspace / "root" / "sub2").exists())
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_max_depth_limit(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that max depth limit is respected"""
        # Always return files to simulate complex problems
        mock_find_files.return_value = ["sub1/problem.md", "sub2/problem.md"]
        
        # Mock responses
        mock_run_prompt.return_value = "Forced simple solution due to depth limit"
        
        result = solve_problem("Complex problem", max_depth=1)
        
        # At depth 1, root should solve directly without decomposition
        # The mock should be called for the root solve only
        self.assertEqual(mock_run_prompt.call_count, 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.node = AgentNode("error_test", self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_empty_problem(self, mock_run_prompt):
        """Test handling of empty problem string"""
        mock_run_prompt.return_value = "Empty problem handled"
        
        result = self.node.solve_simple("")
        
        self.assertIsInstance(result, str)
        mock_run_prompt.assert_called_once()
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_very_long_problem(self, mock_run_prompt):
        """Test handling of very long problem descriptions"""
        long_problem = "A" * 10000  # Very long problem
        mock_run_prompt.return_value = "Long problem handled"
        
        result = self.node.solve_simple(long_problem)
        
        self.assertEqual(result, "Long problem handled")
    
    @patch.object(ClaudeClient, 'run_prompt')
    def test_special_characters_in_problem(self, mock_run_prompt):
        """Test handling of special characters in problem description"""
        special_problem = "Problem with 'quotes' and \"double quotes\" and \n newlines"
        mock_run_prompt.return_value = "Special chars handled"
        
        result = self.node.solve_simple(special_problem)
        
        self.assertEqual(result, "Special chars handled")
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_decomposition_error_handling(self, mock_run_prompt, mock_find_files):
        """Test handling of errors during decomposition"""
        # Mock Claude error
        mock_run_prompt.return_value = "Error: Claude failed"
        mock_find_files.return_value = []
        
        result = self.node.decompose_to_markdown("Test problem")
        
        # Should return empty list on error
        self.assertEqual(result, [])


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
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_context_passed_to_children(self, mock_run_prompt, mock_find_files, mock_input):
        """Test that context is properly passed down the tree"""
        # Mock the decomposition to return subtasks
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return ["task_a/problem.md", "task_b/problem.md"]
            else:
                return []  # Leaf nodes
        
        mock_find_files.side_effect = find_files_side_effect
        
        # Set up responses for Claude calls
        responses = [
            # Initial decomposition
            "Created subtasks",
            # Task A solution
            "Solution A with context awareness",
            # Task B solution
            "Solution B with context awareness",
            # Integration
            "Integrated solution"
        ]
        
        mock_run_prompt.side_effect = responses
        
        result = solve_problem("Root problem")
        
        # Check that context was passed in the prompts
        calls = mock_run_prompt.call_args_list
        
        # The solve calls should include context
        solve_calls = [c for c in calls if "Root Goal:" in c[0][0]]
        self.assertGreaterEqual(len(solve_calls), 2, "Context should be passed to child tasks")


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
    
    @patch('builtins.input', return_value='')
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_realistic_workflow(self, mock_run_prompt, mock_find_files, mock_input):
        """Test a realistic problem-solving workflow"""
        # Mock decomposition creating three subtasks
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return [
                    "data_model/problem.md",
                    "api_endpoints/problem.md", 
                    "frontend/problem.md"
                ]
            else:
                return []  # Leaf nodes
        
        mock_find_files.side_effect = find_files_side_effect
        
        # Mock solution responses
        responses = [
            # Initial decomposition
            "Created project structure",
            # Subtask 1 solution
            "Data model: User table with id, name, email fields",
            # Subtask 2 solution
            "API: REST endpoints for CRUD operations on users",
            # Subtask 3 solution
            "Frontend: React app with user management interface",
            # Integration
            "Complete user management system with database, API, and frontend"
        ]
        
        mock_run_prompt.side_effect = responses
        
        result = solve_problem("Create a user management system")
        
        # Verify the final result contains integrated solution
        self.assertIn("Complete user management system", result)
        
        # Verify all claude calls were made
        self.assertEqual(mock_run_prompt.call_count, len(responses))
        
        # Verify workspace structure
        workspaces = list(Path(".").glob("agent_tree_*"))
        self.assertEqual(len(workspaces), 1)
        
        workspace = workspaces[0]
        self.assertTrue(workspace.exists())
        self.assertTrue((workspace / "root").exists())


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)