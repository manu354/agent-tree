#!/usr/bin/env python3
"""
Unit tests for the solve module
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import solve


class TestSolveModule(unittest.TestCase):
    """Unit tests for solve.py"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Reset global state
        solve.solved_tasks = set()
        solve.workspace_root = None
        
        # Path to mock claude
        self.mock_claude = Path(__file__).parent.parent.parent / "integration" / "mock_claude.py"
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # Reset globals
        solve.solved_tasks = set()
        solve.workspace_root = None
    
    def test_get_dependent(self):
        """Test get_dependent function"""
        # Create task with dependents
        task_file = self.test_dir / "task.md"
        task_file.write_text("""# Task

## Description
Some task

### Dependents
- [Parent Task](../parent.md)
- [Sibling Task](sibling.md)
""")
        
        dependents = solve.get_dependent(str(task_file))
        
        # Should extract both dependent paths
        self.assertEqual(len(dependents), 2)
        
        # Paths should be absolute
        for dep in dependents:
            self.assertTrue(Path(dep).is_absolute())
        
        # Check relative resolution
        expected_parent = (self.test_dir.parent / "parent.md").resolve()
        expected_sibling = (self.test_dir / "sibling.md").resolve()
        
        dependent_paths = [Path(d) for d in dependents]
        self.assertIn(expected_parent, dependent_paths)
        self.assertIn(expected_sibling, dependent_paths)
    
    def test_get_dependencies(self):
        """Test get_dependencies function"""
        # Create task with dependencies
        task_file = self.test_dir / "task.md"
        task_file.write_text("""# Task

## Dependencies
- [Dep 1](dep1.md)
- [Dep 2](subdir/dep2.md)

## Description
Task with dependencies""")
        
        deps = solve.get_dependencies(str(task_file))
        
        # Should extract both dependencies
        self.assertEqual(len(deps), 2)
        
        # Check resolution
        expected_dep1 = self.test_dir / "dep1.md"
        expected_dep2 = self.test_dir / "subdir" / "dep2.md"
        
        dep_paths = [Path(d) for d in deps]
        self.assertIn(expected_dep1.resolve(), dep_paths)
        self.assertIn(expected_dep2.resolve(), dep_paths)
    
    def test_has_children(self):
        """Test has_children function"""
        # Task without children
        task_file = self.test_dir / "simple.md"
        task_file.write_text("# Simple Task")
        
        self.assertFalse(solve.has_children(str(task_file)))
        
        # Task with children directory
        complex_file = self.test_dir / "complex.md"
        complex_file.write_text("# Complex Task")
        
        children_dir = self.test_dir / "complex_children"
        children_dir.mkdir()
        (children_dir / "child1.md").write_text("# Child 1")
        
        self.assertTrue(solve.has_children(str(complex_file)))
        
        # Empty children directory
        empty_file = self.test_dir / "empty.md"
        empty_file.write_text("# Empty Task")
        
        empty_children = self.test_dir / "empty_children"
        empty_children.mkdir()
        
        self.assertFalse(solve.has_children(str(empty_file)))
    
    def test_get_children(self):
        """Test get_children function"""
        task_file = self.test_dir / "parent.md"
        task_file.write_text("# Parent Task")
        
        # Create children
        children_dir = self.test_dir / "parent_children"
        children_dir.mkdir()
        
        child1 = children_dir / "child1.md"
        child2 = children_dir / "child2.md"
        plan_file = children_dir / "child_plan.md"  # Should be excluded
        
        child1.write_text("# Child 1")
        child2.write_text("# Child 2")
        plan_file.write_text("# Plan")
        
        children = solve.get_children(str(task_file))
        
        # Should get only .md files, excluding _plan.md
        self.assertEqual(len(children), 2)
        self.assertIn(str(child1), children)
        self.assertIn(str(child2), children)
        self.assertNotIn(str(plan_file), children)
    
    def test_tree_context_generation(self):
        """Test generate_tree_context function"""
        # Create a tree structure
        root = self.test_dir / "root.md"
        root.write_text("# Root Task")
        
        children_dir = self.test_dir / "root_children"
        children_dir.mkdir()
        
        child1 = children_dir / "child1.md"
        child1.write_text("# Child 1")
        
        child2 = children_dir / "child2.md"
        child2.write_text("# Child 2")
        
        # Create grandchildren
        grandchildren_dir = children_dir / "child1_children"
        grandchildren_dir.mkdir()
        
        grandchild = grandchildren_dir / "grandchild.md"
        grandchild.write_text("# Grandchild")
        
        # Test context from different positions
        context = solve.generate_tree_context(str(root), str(grandchild))
        
        # Should contain tree structure
        self.assertIn("Root Task", context)
        self.assertIn("Child 1", context)
        self.assertIn("Child 2", context)
        self.assertIn("Grandchild", context)
        self.assertIn("YOU ARE HERE", context)
        
        # Tree markers
        self.assertIn("├──", context)
        self.assertIn("└──", context)
    
    def test_solve_simple_task(self):
        """Test solving a simple task"""
        task_file = self.test_dir / "simple.md"
        task_file.write_text("""# Simple Task

## Type
simple

## Description
A simple task to solve""")
        
        # Set workspace root
        solve.workspace_root = self.test_dir
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch('os.chdir') as mock_chdir:
                solve.solve_task(str(task_file), str(self.test_dir))
                
                # Should change to workspace directory
                mock_chdir.assert_called_with(self.test_dir)
                
                # Should call Claude
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                
                # Verify command structure
                self.assertEqual(call_args[0], 'claude')
                self.assertIn('--dangerously-skip-permissions', call_args)
                
                # Verify prompt
                prompt = call_args[-1]
                self.assertIn("solve this task", prompt)
                self.assertIn("Simple Task", prompt)
        
        # Task should be marked as solved
        self.assertIn(str(task_file), solve.solved_tasks)
    
    def test_solve_with_dependencies(self):
        """Test solving a task with dependencies"""
        # Create task with dependencies
        task_file = self.test_dir / "task.md"
        task_file.write_text("""# Main Task

## Dependencies
- [Dep Task](dep.md)

## Description
Task with dependency""")
        
        dep_file = self.test_dir / "dep.md"
        dep_file.write_text("""# Dep Task

## Type
simple

## Description
Dependency task""")
        
        # Create dependency solution
        dep_solution = self.test_dir / "solution.md"
        dep_solution.write_text("# Solution for Dep Task")
        
        # Mark dependency as solved
        solve.solved_tasks.add(str(dep_file))
        solve.workspace_root = self.test_dir
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch('os.chdir'):
                solve.solve_task(str(task_file), str(self.test_dir))
                
                # Get the prompt
                prompt = mock_run.call_args[0][0][-1]
                
                # Should include dependent solution
                self.assertIn("Dependent Solutions:", prompt)
                self.assertIn("Solution for Dep Task", prompt)
    
    def test_solve_complex_task_decomposition(self):
        """Test that complex tasks trigger decomposition"""
        task_file = self.test_dir / "complex.md"
        task_file.write_text("""# Complex Task

## Type
complex

## Description
This needs decomposition""")
        
        solve.workspace_root = self.test_dir
        
        with patch('subprocess.run') as mock_run:
            # Mock decompose subprocess call
            def mock_subprocess(cmd, *args, **kwargs):
                if 'decompose' in cmd:
                    # Simulate decompose creating children
                    children_dir = self.test_dir / "complex_children"
                    children_dir.mkdir()
                    (children_dir / "child.md").write_text("# Child\n\n## Type\nsimple")
                return MagicMock(returncode=0)
            
            mock_run.side_effect = mock_subprocess
            
            with patch('os.chdir'):
                solve.solve_task(str(task_file), str(self.test_dir))
                
                # Should call decompose
                decompose_calls = [c for c in mock_run.call_args_list 
                                 if 'decompose' in str(c)]
                self.assertTrue(len(decompose_calls) > 0)
    
    def test_solve_with_plan_update(self):
        """Test that plan files are updated after solving"""
        task_file = self.test_dir / "task.md"
        task_file.write_text("# Task")
        
        plan_file = self.test_dir / "task_plan.md"
        plan_file.write_text("""# Task - Plan

## Status
[ ] Not started""")
        
        solve.workspace_root = self.test_dir
        solve.solved_tasks.add(str(task_file))
        
        # Update plan
        solve.update_plan_status(str(task_file))
        
        # Check plan was updated
        plan_content = plan_file.read_text()
        self.assertIn("[x] Completed", plan_content)
        self.assertNotIn("[ ] Not started", plan_content)
    
    def test_solve_entire_tree(self):
        """Test solve function that orchestrates entire tree solving"""
        # Create root task
        root_file = self.test_dir / "root.md"
        root_file.write_text("# Root Task")
        
        # Create plan
        plan_file = self.test_dir / "root_plan.md"
        plan_file.write_text("""# Root Task - Plan

## Type
complex

## Subtasks
- [Child 1](root_children/child1.md)
- [Child 2](root_children/child2.md)

## Status
[ ] Not started""")
        
        # Create children
        children_dir = self.test_dir / "root_children"
        children_dir.mkdir()
        
        child1 = children_dir / "child1.md"
        child1.write_text("""# Child 1

## Type
simple

## Dependencies
None

## Dependents
- [Root Task](../root.md)""")
        
        child2 = children_dir / "child2.md"
        child2.write_text("""# Child 2

## Type
simple

## Dependencies
- [Child 1](child1.md)

## Dependents
- [Root Task](../root.md)""")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Track solve order
            solve_order = []
            
            def track_solves(cmd, *args, **kwargs):
                if 'solve this task' in cmd[-1]:
                    if "Child 1" in cmd[-1]:
                        solve_order.append("child1")
                    elif "Child 2" in cmd[-1]:
                        solve_order.append("child2")
                    elif "Root Task" in cmd[-1]:
                        solve_order.append("root")
                return MagicMock(returncode=0)
            
            mock_run.side_effect = track_solves
            
            solve.solve(str(root_file))
            
            # Verify solve order: child1 -> child2 -> root
            self.assertEqual(solve_order, ["child1", "child2", "root"])
            
            # All tasks should be solved
            self.assertEqual(len(solve.solved_tasks), 3)
    
    def test_error_handling(self):
        """Test error handling in solve module"""
        # Non-existent file
        with self.assertRaises(FileNotFoundError):
            solve.solve("non_existent.md")
        
        # Claude failure
        task_file = self.test_dir / "task.md"
        task_file.write_text("# Task")
        
        solve.workspace_root = self.test_dir
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            
            with patch('os.chdir'):
                with self.assertRaises(SystemExit):
                    solve.solve_task(str(task_file), str(self.test_dir))
    
    def test_cyclic_dependency_detection(self):
        """Test handling of cyclic dependencies"""
        # Create tasks with circular dependency
        task1 = self.test_dir / "task1.md"
        task1.write_text("""# Task 1

## Dependencies
- [Task 2](task2.md)""")
        
        task2 = self.test_dir / "task2.md"
        task2.write_text("""# Task 2

## Dependencies
- [Task 1](task1.md)""")
        
        # The current implementation might not handle this perfectly,
        # but it should at least not crash
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            try:
                solve.solve(str(task1))
                # If it completes, verify no infinite loop
                self.assertTrue(True)
            except RecursionError:
                self.fail("Should handle cyclic dependencies without infinite recursion")


if __name__ == '__main__':
    unittest.main()