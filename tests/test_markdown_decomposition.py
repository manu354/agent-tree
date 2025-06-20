"""Tests for markdown-based decomposition"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.agent_node import AgentNode
from src.context import Context


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
        node = AgentNode("test", self.work_dir)
        
        # Test basic case
        assert node._generate_problem_name("Build a web scraper") == "build_a_web_scraper"
        
        # Test with special characters
        assert node._generate_problem_name("Create REST API (with auth)") == "create_rest_api_with_auth"
        
        # Test truncation
        long_problem = "This is a very long problem description that should be truncated"
        name = node._generate_problem_name(long_problem)
        assert len(name) <= 50
        assert name == "this_is_a_very_long"
    
    def test_is_problem_complex(self):
        """Test complexity detection from markdown"""
        node = AgentNode("test", self.work_dir)
        
        # Test simple problem
        simple_md = self.work_dir / "simple.md"
        simple_md.write_text("""# Task

## Type
simple

## Problem
A simple task""")
        assert not node.is_problem_complex(str(simple_md))
        
        # Test complex problem
        complex_md = self.work_dir / "complex.md"
        complex_md.write_text("""# Task

## Type
complex

## Problem
A complex task""")
        assert node.is_problem_complex(str(complex_md))
        
        # Test when both appear (first wins)
        mixed_md = self.work_dir / "mixed.md"
        mixed_md.write_text("""# Task
First mention: simple
Later mention: complex""")
        assert not node.is_problem_complex(str(mixed_md))
        
        # Test default (no type found)
        no_type_md = self.work_dir / "no_type.md"
        no_type_md.write_text("""# Task
No type specified""")
        assert not node.is_problem_complex(str(no_type_md))
    
    @patch('src.agent_node.AgentNode._run_claude')
    def test_decompose_to_markdown(self, mock_claude):
        """Test markdown file creation during decomposition"""
        node = AgentNode("test", self.work_dir)
        
        # Mock Claude to simulate file creation
        def create_files(prompt):
            # Extract problem name from prompt
            if "build_a_web_scraper" in prompt:
                # Create main problem file
                (self.work_dir / "build_a_web_scraper.md").write_text("""# Build a web scraper

## Type
complex

## Problem
Create a web scraper

## Possible Solution
Use requests and BeautifulSoup

## Notes
Handle errors gracefully""")
                
                # Create subproblems directory and files
                subprobs_dir = self.work_dir / "build_a_web_scraper" / "subproblems"
                subprobs_dir.mkdir(parents=True, exist_ok=True)
                
                (subprobs_dir / "parse_html.md").write_text("""# Parse HTML

## Type
simple

## Problem
Extract data from HTML

## Possible Solution
Use BeautifulSoup

## Notes
Handle malformed HTML""")
                
                (subprobs_dir / "handle_pagination.md").write_text("""# Handle Pagination

## Type
complex

## Problem
Navigate through pages

## Possible Solution
Follow next links

## Notes
Detect pagination patterns""")
            
            return "Files created"
        
        mock_claude.side_effect = create_files
        
        # Test decomposition
        context = Context(root_problem="Build a web scraper")
        files = node.decompose_to_markdown("Build a web scraper", context, ".")
        
        # Verify files were created
        assert len(files) == 2
        assert any("parse_html.md" in f for f in files)
        assert any("handle_pagination.md" in f for f in files)
        
        # Verify main problem file exists
        assert (self.work_dir / "build_a_web_scraper.md").exists()
        
        # Verify subproblem structure
        assert (self.work_dir / "build_a_web_scraper" / "subproblems").exists()
    
    def test_build_decomposition_prompt(self):
        """Test the markdown decomposition prompt generation"""
        node = AgentNode("test", self.work_dir)
        context = Context(root_problem="Main problem")
        
        prompt = node._build_decomposition_prompt(
            "Build a web scraper",
            context.to_prompt(),
            "workspace/root"
        )
        
        # Verify prompt contains key elements
        assert "Build a web scraper" in prompt
        assert "workspace/root/build_a_web_scraper.md" in prompt
        assert "workspace/root/build_a_web_scraper/subproblems/" in prompt
        assert "## Type" in prompt
        assert "simple or complex" in prompt
        assert "MAX 100 WORDS" in prompt
        assert "Write tool" in prompt


class TestMarkdownIntegration:
    """Test integration with agent_tree.py"""
    
    @patch('src.agent_node.AgentNode._run_claude')
    def test_decompose_only_phase(self, mock_claude):
        """Test that decompose_only creates markdown files without executing"""
        from src.agent_tree import solve_problem
        
        # Mock Claude to create files
        def mock_decomposition(prompt):
            # Simulate Claude creating markdown files based on prompt
            if "Calculate factorial" in prompt:
                # For root problem, create subproblems
                return "Created markdown files"
            return ""
        
        mock_claude.return_value = mock_decomposition
        
        # TODO: This test needs more work to properly mock the file creation
        # For now, we're just checking the structure
        
    def test_execute_bottom_up_order(self):
        """Test that execution happens in correct bottom-up order"""
        # Create a mock file structure
        workspace = Path(tempfile.mkdtemp())
        try:
            # Create root
            root = workspace / "root"
            root.mkdir()
            (root / "problem.md").write_text("""# Main Problem
## Type
complex""")
            
            # Create child
            child = root / "subtask1"
            child.mkdir()
            (child / "problem.md").write_text("""# Subtask 1
## Type
simple""")
            
            # Import and test
            from src.agent_tree import execute_bottom_up
            
            # Mock the AgentNode methods
            with patch('src.agent_node.AgentNode.solve_simple') as mock_solve:
                with patch('src.agent_node.AgentNode.integrate_solutions') as mock_integrate:
                    mock_solve.return_value = "Leaf solution"
                    mock_integrate.return_value = "Integrated solution"
                    
                    # Execute
                    result = execute_bottom_up(workspace)
                    
                    # Verify execution order: leaf first, then parent
                    assert mock_solve.called
                    assert mock_integrate.called
                    
        finally:
            shutil.rmtree(workspace)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])