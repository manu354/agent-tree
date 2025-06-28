#!/usr/bin/env python3
"""
Simple test for the decompose module
"""

import os
import tempfile
import shutil
from pathlib import Path
from decompose import decompose, extract_name, is_complex, node_count, seen_tasks


def test_extract_name():
    """Test extract_name function"""
    assert extract_name("web_scraper.md") == "web_scraper"
    assert extract_name("/path/to/task.md") == "task"
    assert extract_name("complex_task.md") == "complex_task"
    print("✓ extract_name tests passed")


def test_is_complex():
    """Test is_complex function"""
    # Create test files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Complex task file
        complex_file = Path(tmpdir) / "complex.md"
        complex_file.write_text("""# Complex Task
## Type
complex
## Summary
This needs decomposition
""")
        
        # Simple task file
        simple_file = Path(tmpdir) / "simple.md"
        simple_file.write_text("""# Simple Task
## Type
simple
## Summary
Can be solved directly
""")
        
        # No type file
        no_type_file = Path(tmpdir) / "no_type.md"
        no_type_file.write_text("""# Task
## Summary
No type specified
""")
        
        assert is_complex(str(complex_file)) == True
        assert is_complex(str(simple_file)) == False
        assert is_complex(str(no_type_file)) == False
        
    print("✓ is_complex tests passed")


def test_decompose():
    """Test decompose function with a simple example"""
    global node_count, seen_tasks
    
    # Reset global state
    node_count = 0
    seen_tasks.clear()
    
    # Create a test task file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_task = Path(tmpdir) / "build_web_app.md"
        test_task.write_text("""# Build a Simple Web Application

## Type
complex

## Summary
Create a web application with frontend and backend

## Task
Build a simple web application that:
1. Has a React frontend
2. Has a Node.js backend API
3. Connects to a database
4. Supports user authentication

This is a complex task that should be broken down into smaller components.
""")
        
        print(f"\nTest task created at: {test_task}")
        print("Running decompose (this will call Claude CLI)...")
        
        try:
            # Run decompose
            decompose(str(test_task))
            
            # Check results
            print(f"\nResults:")
            print(f"- Nodes created: {node_count}")
            print(f"- Tasks seen: {len(seen_tasks)}")
            
            # Check if plan file was created
            plan_file = Path(tmpdir) / "build_web_app_plan.md"
            if plan_file.exists():
                print(f"✓ Plan file created: {plan_file}")
            else:
                print(f"✗ Plan file not found")
            
            # Check if children directory was created
            children_dir = Path(tmpdir) / "build_web_app_children"
            if children_dir.exists():
                print(f"✓ Children directory created: {children_dir}")
                # List children
                children = list(children_dir.glob("*.md"))
                print(f"  Found {len(children)} subtasks:")
                for child in children:
                    print(f"    - {child.name}")
            else:
                print(f"✗ Children directory not found")
                
        except Exception as e:
            print(f"Error during decompose: {e}")
            print("Note: This test requires Claude CLI to be installed and configured")


if __name__ == "__main__":
    print("Testing decompose module...")
    
    # Test utility functions
    test_extract_name()
    test_is_complex()
    
    print("\nUtility function tests completed!")
    print("\nTo run the full decompose test (which calls Claude CLI), run:")
    print("  python -c \"from test_decompose import test_decompose; test_decompose()\"")