"""
SWE-bench inspired benchmark tests for the Agent Tree system.

This module contains both synthetic and real-world inspired benchmark tests
to validate the agent tree's ability to handle complex, hierarchical software
engineering tasks that require multi-file modifications and coordinated changes.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context


class MockClaudeResponse:
    """Mock responses for claude CLI to create deterministic benchmarks."""
    
    def __init__(self, response_map: Dict[str, Dict[str, any]]):
        self.response_map = response_map
        self.call_history = []
    
    def get_response(self, prompt: str) -> Dict[str, any]:
        """Return pre-programmed responses based on prompt content."""
        self.call_history.append(prompt)
        
        # Find the best matching response
        for key, response in self.response_map.items():
            if key.lower() in prompt.lower():
                return response
        
        # Default response
        return {
            "approach": "Unable to process this request",
            "should_decompose": False,
            "subtasks": []
        }


class FileSystemTools:
    """Tools for file system operations in benchmarks."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def create_file(self, path: str, content: str) -> None:
        """Create a file with given content."""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    def read_file(self, path: str) -> str:
        """Read a file's content."""
        full_path = self.base_path / path
        return full_path.read_text()
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return (self.base_path / path).exists()


class TestSWEBenchmark(unittest.TestCase):
    """Benchmark tests inspired by SWE-bench challenges."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.fs_tools = FileSystemTools(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_synthetic_web_app(self):
        """Create a mini web application with a multi-file bug."""
        # Controller layer
        controller_content = '''
class UserController:
    def __init__(self, service):
        self.service = service
    
    def get_user_profile(self, user_id, use_new_format=False):
        """Get user profile with optional new format."""
        user_data = self.service.fetch_user(user_id, use_new_format)
        
        if use_new_format:
            # Bug: Not handling the new format properly
            return {
                "id": user_data["id"],
                "name": user_data["name"],
                # Missing: should include full_name when available
            }
        else:
            return user_data
'''
        
        # Service layer
        service_content = '''
class UserService:
    def __init__(self, datastore):
        self.datastore = datastore
    
    def fetch_user(self, user_id, use_new_format=False):
        """Fetch user data from datastore."""
        raw_data = self.datastore.get_user(user_id, use_new_format)
        
        # Bug: Not processing the full_name field
        return {
            "id": raw_data["id"],
            "name": raw_data["name"],
            # Missing: should format full_name when use_new_format is True
        }
'''
        
        # Data layer
        datastore_content = '''
class UserDatastore:
    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "John", "first_name": "John", "last_name": "Doe"},
            2: {"id": 2, "name": "Jane", "first_name": "Jane", "last_name": "Smith"},
        }
    
    def get_user(self, user_id, use_new_format=False):
        """Get user data from storage."""
        user = self.users.get(user_id, {})
        
        if use_new_format:
            # Bug: Constructing full_name but not returning it
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            # Should add: user["full_name"] = full_name.strip()
        
        return user
'''
        
        # Test file
        test_content = '''
import unittest
from controller import UserController
from service import UserService
from datastore import UserDatastore

class TestUserProfile(unittest.TestCase):
    def setUp(self):
        self.datastore = UserDatastore()
        self.service = UserService(self.datastore)
        self.controller = UserController(self.service)
    
    def test_old_format(self):
        """Test that old format still works."""
        result = self.controller.get_user_profile(1, use_new_format=False)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "John")
        self.assertNotIn("full_name", result)
    
    def test_new_format(self):
        """Test that new format includes full_name."""
        result = self.controller.get_user_profile(1, use_new_format=True)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "John")
        # This test will fail due to the bug
        self.assertEqual(result["full_name"], "John Doe")
'''
        
        # Write files
        self.fs_tools.create_file("controller.py", controller_content)
        self.fs_tools.create_file("service.py", service_content)
        self.fs_tools.create_file("datastore.py", datastore_content)
        self.fs_tools.create_file("test_user.py", test_content)
    
    def create_mock_responses_for_synthetic_app(self) -> MockClaudeResponse:
        """Create mock claude responses for the synthetic app bug fix."""
        responses = {
            "implement the use_new_format feature": {
                "approach": "Fix the use_new_format feature flag implementation across all layers of the application.",
                "should_decompose": True,
                "subtasks": [
                    "Update datastore.py to return full_name field when use_new_format is True",
                    "Update service.py to process and format the full_name field",
                    "Update controller.py to include full_name in the response",
                    "Verify all tests pass"
                ]
            },
            "update datastore.py": {
                "approach": "Modify the get_user method to include full_name in the response when use_new_format is True.",
                "should_decompose": False,
                "subtasks": [],
                "implementation": '''
# In datastore.py, update the get_user method:
if use_new_format:
    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
    user["full_name"] = full_name.strip()
'''
            },
            "update service.py": {
                "approach": "Modify the fetch_user method to handle and pass through the full_name field.",
                "should_decompose": False,
                "subtasks": [],
                "implementation": '''
# In service.py, update the fetch_user method:
if use_new_format and "full_name" in raw_data:
    return {
        "id": raw_data["id"],
        "name": raw_data["name"],
        "full_name": raw_data["full_name"]
    }
'''
            },
            "update controller.py": {
                "approach": "Modify get_user_profile to include full_name in the response when available.",
                "should_decompose": False,
                "subtasks": [],
                "implementation": '''
# In controller.py, update get_user_profile:
if use_new_format and "full_name" in user_data:
    return {
        "id": user_data["id"],
        "name": user_data["name"],
        "full_name": user_data["full_name"]
    }
'''
            },
            "verify all tests": {
                "approach": "Run the test suite to ensure all tests pass.",
                "should_decompose": False,
                "subtasks": [],
                "result": "All tests pass successfully"
            }
        }
        return MockClaudeResponse(responses)
    
    @patch('subprocess.run')
    def test_synthetic_web_app_bug_fix(self, mock_run):
        """Test fixing a multi-file bug in a synthetic web application."""
        # Create the buggy application
        self.create_synthetic_web_app()
        
        # Create mock responses
        mock_responses = self.create_mock_responses_for_synthetic_app()
        
        # Setup mock subprocess to return our mock responses
        def mock_subprocess_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            
            # Read the prompt from the file (claude CLI uses file input)
            if len(cmd) > 2:
                prompt_file = cmd[2]
                try:
                    with open(prompt_file, 'r') as f:
                        prompt_text = f.read()
                except:
                    prompt_text = ""
            else:
                prompt_text = ""
            
            # Get appropriate response based on what's being asked
            if "analyze this problem" in prompt_text.lower() or "decompose" in prompt_text.lower():
                # This is a decomposition request
                response = {
                    "decompose": True,
                    "approach": "Fix the use_new_format feature flag implementation across all layers",
                    "subtasks": [
                        {"task": "Update datastore.py to return full_name field when use_new_format is True", "simple": True},
                        {"task": "Update service.py to process and format the full_name field", "simple": True}, 
                        {"task": "Update controller.py to include full_name in the response", "simple": True},
                        {"task": "Verify all tests pass", "simple": True}
                    ]
                }
            else:
                # Get response from our mock
                response = mock_responses.get_response(prompt_text)
            
            # Convert response to JSON for claude output
            result.stdout = json.dumps(response)
            
            return result
        
        mock_run.side_effect = mock_subprocess_run
        
        # Create context
        context = Context(
            root_problem="Implement the use_new_format feature flag correctly across the application"
        )
        
        # Create agent tree and execute
        root_node = AgentNode("fix_new_format_feature", self.test_dir / "work")
        
        # Execute the task - we'll test the individual methods
        result = root_node.decompose_problem(
            "Fix the use_new_format feature implementation", 
            context
        )
        
        # Verify that the mock was called appropriately
        self.assertGreater(mock_run.call_count, 0)
        
        # Verify the response structure
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)
        # Check first subtask
        self.assertEqual(result[0][0], "Update datastore.py to return full_name field when use_new_format is True")
    
    def test_complex_refactoring_task(self):
        """Test a complex refactoring task inspired by real SWE-bench problems."""
        # Create a more complex codebase with architectural issues
        
        # Old monolithic module
        old_module = '''
class Calculator:
    """A calculator with all operations in one class (code smell)."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a, b):
        result = a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        result = a / b
        self.history.append(f"divide({a}, {b}) = {result}")
        return result
    
    def power(self, a, b):
        result = a ** b
        self.history.append(f"power({a}, {b}) = {result}")
        return result
    
    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = []
    
    # Complex operations that depend on basic ones
    def calculate_average(self, numbers):
        if not numbers:
            return 0
        total = sum(numbers)
        return self.divide(total, len(numbers))
    
    def calculate_variance(self, numbers):
        if not numbers:
            return 0
        avg = self.calculate_average(numbers)
        squared_diffs = [self.power(self.subtract(x, avg), 2) for x in numbers]
        return self.calculate_average(squared_diffs)
'''
        
        self.fs_tools.create_file("calculator.py", old_module)
        
        # Create mock responses for refactoring
        refactor_responses = {
            "refactor calculator": {
                "approach": "Refactor the monolithic Calculator class following SOLID principles by separating concerns.",
                "should_decompose": True,
                "subtasks": [
                    "Extract operation interfaces and create separate operation classes",
                    "Create a history management system separate from operations",
                    "Create a calculator facade that composes operations",
                    "Update complex operations to use the new structure",
                    "Ensure backward compatibility"
                ]
            },
            "extract operation interfaces": {
                "approach": "Create separate operation classes following Single Responsibility Principle.",
                "should_decompose": True,
                "subtasks": [
                    "Create operations/base.py with abstract operation interface",
                    "Create operations/basic.py with Add, Subtract, Multiply, Divide classes",
                    "Create operations/advanced.py with Power class"
                ]
            },
            "history management": {
                "approach": "Extract history tracking to a separate concern.",
                "should_decompose": False,
                "subtasks": [],
                "implementation": "Create history.py with HistoryManager class"
            },
            "calculator facade": {
                "approach": "Create a new Calculator class that uses composition.",
                "should_decompose": False,
                "subtasks": [],
                "implementation": "Update calculator.py to use the new operation classes and history manager"
            }
        }
        
        mock_responses = MockClaudeResponse(refactor_responses)
        
        # Test that we can create the refactoring plan
        response = mock_responses.get_response("refactor calculator following SOLID principles")
        
        self.assertTrue(response["should_decompose"])
        self.assertEqual(len(response["subtasks"]), 5)
        self.assertIn("Extract operation interfaces", response["subtasks"][0])


if __name__ == '__main__':
    unittest.main()