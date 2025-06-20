#!/usr/bin/env python3
"""
Simple benchmark runner wrapper
"""

import subprocess
import sys
from pathlib import Path

def main():
    benchmark_script = Path(__file__).parent / "benchmarks" / "run_real_benchmark.py"
    
    print("Running Agent Tree Benchmarks...")
    print("=" * 60)
    
    result = subprocess.run([sys.executable, str(benchmark_script)])
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())