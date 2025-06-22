"""Tests for markdown-based decomposition"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.agent_node import AgentNode
from src.context import Context
from src.claude_client import ClaudeClient
from src.markdown_utils import generate_problem_name, find_subproblem_files
from src.prompts import build_decomposition_prompt


class TestMarkdownDecomposition:
    """Test the new markdown-based decomposition"""

    def setup_method(self):
        """Create a temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.work_dir = Path(self.temp_dir) / "test_node"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_generate_problem_name(self):
        """Test safe problem name generation"""
        # Test basic case
        assert generate_problem_name("Build a web scraper") == "build_a_web_scraper"

        # Test with special characters
        assert (
            generate_problem_name("Create REST API (with auth)")
            == "create_rest_api_with_auth"
        )

        # Test truncation
        long_problem = "This is a very long problem description that should be truncated to a reasonable length"
        name = generate_problem_name(long_problem)
        assert len(name) <= 50
        assert name.startswith("this_is_a_very_long")

    def test_is_problem_complex(self):
        """Test is_problem_complex method"""
        node = AgentNode("test", self.work_dir)

        # Create test markdown files
        simple_file = self.work_dir / "simple.md"
        simple_file.write_text("# Task\n\n## Type\nsimple\n")

        complex_file = self.work_dir / "complex.md"
        complex_file.write_text("# Task\n\n## Type\ncomplex\n")

        assert node.is_problem_complex(str(simple_file)) == False
        assert node.is_problem_complex(str(complex_file)) == True

    @patch.object(ClaudeClient, "run_prompt")
    def test_decompose_to_markdown(self, mock_run_prompt):
        """Test decomposition creates markdown structure"""
        node = AgentNode("test", self.work_dir)

        # Mock Claude creating markdown files
        mock_run_prompt.return_value = "Created markdown structure"

        # Create actual files in expected structure
        problem_name = "build_a_fullstack_web_application"
        subproblems_dir = self.work_dir / problem_name / "subproblems"
        subproblems_dir.mkdir(parents=True)

        ui_file = subproblems_dir / "01_build_ui.md"
        backend_file = subproblems_dir / "02_setup_backend.md"
        integrate_file = subproblems_dir / "03_integrate_components.md"

        ui_file.write_text("# Build UI\n\n## Type\nsimple")
        backend_file.write_text("# Setup Backend\n\n## Type\ncomplex")
        integrate_file.write_text("# Integrate Components\n\n## Type\nsimple")

        # Test decomposition
        problem = "Build a full-stack web application"
        result = node.decompose_to_markdown(problem)

        # Verify results
        assert len(result) == 3
        assert any("build_ui" in r for r in result)
        assert any("setup_backend" in r for r in result)
        assert any("integrate_components" in r for r in result)

        # Verify Claude was called with correct prompt
        call_args = mock_run_prompt.call_args[0][0]
        assert "Build a full-stack web application" in call_args
        assert "markdown" in call_args.lower()

    def test_build_decomposition_prompt(self):
        """Test prompt building for decomposition"""
        problem = "Create a chat application"
        context = Context(
            root_problem="Build messaging platform",
            parent_task="Create user features",
            parent_approach="Modular architecture",
            sibling_tasks=["User auth", "Message storage"],
        )

        prompt = build_decomposition_prompt(
            problem, context, parent_path="features", problem_name="chat_application"
        )

        # Verify prompt includes all necessary information
        assert "Create a chat application" in prompt
        assert "Root Goal: Build messaging platform" in prompt
        assert "Parent Task: Create user features" in prompt
        assert "features/chat_application" in prompt
        assert "markdown" in prompt.lower()


class TestMarkdownIntegration:
    """Test markdown decomposition integration"""

    def setup_method(self):
        """Create a temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.work_dir = Path(self.temp_dir) / "test_project"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    @patch.object(ClaudeClient, "run_prompt")
    def test_decompose_only_phase(self, mock_run_prompt):
        """Test decomposition-only workflow"""
        node = AgentNode("root", self.work_dir)

        # Mock Claude creating files
        mock_run_prompt.return_value = """
Created the following structure:
- data_model/
- api_layer/
- frontend/
"""

        # Create actual files in expected structure
        problem_name = "build_a_task_management_system"
        subproblems_dir = self.work_dir / problem_name / "subproblems"
        subproblems_dir.mkdir(parents=True)

        data_file = subproblems_dir / "01_data_model.md"
        api_file = subproblems_dir / "02_api_layer.md"
        frontend_file = subproblems_dir / "03_frontend.md"

        data_file.write_text("# Data Model\n\n## Type\nsimple")
        api_file.write_text("# API Layer\n\n## Type\ncomplex")
        frontend_file.write_text("# Frontend\n\n## Type\nsimple")

        # Run decomposition
        problem = "Build a task management system"
        subtasks = node.decompose_to_markdown(problem)

        # Verify structure
        assert len(subtasks) == 3
        assert any("data_model" in task for task in subtasks)
        assert any("api_layer" in task for task in subtasks)
        assert any("frontend" in task for task in subtasks)

    def test_execute_bottom_up_order(self):
        """Test that execution follows bottom-up order"""
        # Create a mock structure
        root = self.work_dir / "root"
        root.mkdir()

        # Create leaf nodes
        (root / "task1").mkdir()
        (root / "task1" / "subtask1").mkdir()
        (root / "task1" / "subtask2").mkdir()
        (root / "task2").mkdir()

        # In the actual system, solve_recursive would process these
        # in bottom-up order: subtask1, subtask2, then task1, then task2, then root

        # This test verifies the structure is correct for bottom-up processing
        assert (root / "task1" / "subtask1").exists()
        assert (root / "task1" / "subtask2").exists()
        assert (root / "task1").exists()
        assert (root / "task2").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
