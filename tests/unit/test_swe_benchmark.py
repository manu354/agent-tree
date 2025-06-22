"""
SWE-bench inspired benchmark tests for the Agent Tree system.

This module contains both synthetic and real-world inspired benchmark tests
to validate the agent tree's ability to handle complex, hierarchical software
engineering tasks that require multi-file modifications and coordinated changes.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.agent_node import AgentNode
from src.context import Context
from src.claude_client import ClaudeClient
from src.markdown_utils import find_subproblem_files


class MockClaudeResponse:
    """Mock responses for claude CLI to create deterministic benchmarks."""
    
    def __init__(self, response_map: Dict[str, str]):
        self.response_map = response_map
        self.call_history = []
    
    def get_response(self, prompt: str) -> str:
        """Return pre-programmed responses based on prompt content."""
        self.call_history.append(prompt)
        
        # Find the best matching response
        for key, response in self.response_map.items():
            if key.lower() in prompt.lower():
                return response
        
        # Default response
        return "Unable to process this request"


class FileSystemTools:
    """Tools for file system operations in benchmarks."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def create_file(self, path: str, content: str):
        """Create a file with the given content."""
        file_path = self.base_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    def read_file(self, path: str) -> str:
        """Read a file's content."""
        return (self.base_path / path).read_text()
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return (self.base_path / path).exists()


class TestSWEBenchmark(unittest.TestCase):
    """Test cases inspired by SWE-bench challenges."""
    
    def setUp(self):
        """Create temporary workspace."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.fs_tools = FileSystemTools(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.markdown_utils.find_subproblem_files')
    @patch.object(ClaudeClient, 'run_prompt')
    def test_synthetic_web_app_bug_fix(self, mock_run_prompt, mock_find_files):
        """Test fixing a synthetic multi-file web app bug."""
        # Create initial project structure
        self.fs_tools.create_file("app.py", """
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    # BUG: Should pass user data to template
    return render_template('index.html')
""")
        
        self.fs_tools.create_file("templates/index.html", """
<html>
<body>
    <!-- BUG: Missing user display -->
    <h1>Welcome</h1>
</body>
</html>
""")
        
        # Setup mock responses
        responses = {
            "fix user display": """Created decomposition:
1. Analyze the bug
2. Fix backend route
3. Update template
4. Test the fix""",
            
            "analyze": "The bug is that user data is not passed from backend to frontend",
            
            "fix backend": """Fixed app.py:
@app.route('/')
def index():
    user = {'name': 'John Doe'}
    return render_template('index.html', user=user)""",
            
            "update template": """Fixed index.html:
<h1>Welcome {{ user.name }}</h1>""",
            
            "test": "All tests passing",
            
            "integrate": "Successfully fixed the user display bug across backend and frontend"
        }
        
        mock_claude = MockClaudeResponse(responses)
        mock_run_prompt.side_effect = mock_claude.get_response
        
        # Mock file finding for decomposition
        def find_files_side_effect(work_dir, problem_name):
            if str(work_dir).endswith("root"):
                return [
                    "analyze_bug/problem.md",
                    "fix_backend/problem.md",
                    "update_template/problem.md",
                    "test_fix/problem.md"
                ]
            return []
        
        mock_find_files.side_effect = find_files_side_effect
        
        # Run the agent
        node = AgentNode("root", self.temp_dir / "workspace")
        
        # First decompose
        subtasks = node.decompose_to_markdown("Fix user display bug in web app")
        self.assertEqual(len(subtasks), 4)
        
        # Then solve each subtask
        solution1 = node.solve_simple("Analyze the bug")
        self.assertIn("not passed", solution1)
        
        solution2 = node.solve_simple("Fix backend route")
        self.assertIn("user =", solution2)
        
        solution3 = node.solve_simple("Update template")
        self.assertIn("{{ user.name }}", solution3)
        
        solution4 = node.solve_simple("Test the fix")
        self.assertIn("tests passing", solution4)
        
        # Integrate solutions
        final = node.integrate_solutions(
            "Fix user display bug",
            [
                ("Analyze", solution1),
                ("Fix backend", solution2),
                ("Update template", solution3),
                ("Test", solution4)
            ]
        )
        
        self.assertIn("Successfully fixed", final)
        self.assertIn("backend and frontend", final)


if __name__ == "__main__":
    unittest.main(verbosity=2)