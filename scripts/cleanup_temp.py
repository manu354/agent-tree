#!/usr/bin/env python3
"""
Clean up temporary benchmark and agent_tree directories
"""

import os
import shutil
from pathlib import Path
import json

def cleanup_temp_directories():
    """Remove temporary benchmark and agent_tree directories"""
    current_dir = Path(".")
    
    # Patterns to match temporary directories
    temp_patterns = [
        "benchmark_synthetic_web_app_*",
        "agent_tree_*",
    ]
    
    removed_count = 0
    
    print("🧹 Cleaning up temporary directories...")
    
    for pattern in temp_patterns:
        for path in current_dir.glob(pattern):
            if path.is_dir():
                print(f"  Removing: {path}")
                shutil.rmtree(path)
                removed_count += 1
    
    # Also clean up old benchmark result files (keep only the latest)
    result_files = sorted(current_dir.glob("benchmark_results_*.json"))
    if len(result_files) > 1:
        print("\n📄 Cleaning up old benchmark result files (keeping latest)...")
        for result_file in result_files[:-1]:  # Keep the last one
            print(f"  Removing: {result_file}")
            result_file.unlink()
            removed_count += 1
    
    print(f"\n✅ Cleaned up {removed_count} items")
    
    # Create organized directory structure
    print("\n📁 Creating organized directory structure...")
    
    # Create directories if they don't exist
    dirs_to_create = [
        "tmp",  # For temporary test runs
        "results",  # For benchmark results
        "docs",  # For documentation
    ]
    
    for dir_name in dirs_to_create:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"  Created: {dir_name}/")
    
    # Move documentation files
    doc_files = ["README.md", "BENCHMARK_README.md", "SWE_BENCHMARK_SUMMARY.md"]
    for doc_file in doc_files:
        if Path(doc_file).exists() and not (Path("docs") / doc_file).exists():
            shutil.move(doc_file, Path("docs") / doc_file)
            print(f"  Moved {doc_file} to docs/")
    
    # Move the latest benchmark result if it exists
    if result_files:
        latest_result = result_files[-1]
        if not (Path("results") / latest_result.name).exists():
            shutil.move(str(latest_result), Path("results") / latest_result.name)
            print(f"  Moved {latest_result.name} to results/")
    
    print("\n✅ Directory structure organized!")
    print("\nNew structure:")
    print("  tmp/      - Temporary test runs (auto-cleaned)")
    print("  results/  - Benchmark results")
    print("  docs/     - Documentation")

if __name__ == "__main__":
    cleanup_temp_directories()