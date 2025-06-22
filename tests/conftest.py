"""
Pytest configuration and fixtures for agent-tree tests
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest


@pytest.fixture(autouse=True)
def cleanup_tmp_directories():
    """Automatically clean up any tmp directories created during tests"""
    # Get original working directory
    original_cwd = Path.cwd()

    # Create a temporary directory for the test
    test_dir = tempfile.mkdtemp()
    os.chdir(test_dir)

    yield

    # Change back to original directory
    os.chdir(original_cwd)

    # Clean up the test directory
    shutil.rmtree(test_dir, ignore_errors=True)

    # Clean up any tmp directories in the project root
    tmp_dir = original_cwd / "tmp"
    if tmp_dir.exists() and tmp_dir.is_dir():
        # Only remove agent_tree_* directories to avoid deleting other tmp files
        for agent_tree_dir in tmp_dir.glob("agent_tree_*"):
            if agent_tree_dir.is_dir():
                shutil.rmtree(agent_tree_dir, ignore_errors=True)

        # If tmp dir is now empty, remove it
        try:
            if not any(tmp_dir.iterdir()):
                tmp_dir.rmdir()
        except OSError:
            # Directory not empty or other error, ignore
            pass
