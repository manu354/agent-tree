#!/usr/bin/env python3
"""
Main entry point for agent tree system

Single atomic command to prove correctness: python -m pytest tests/ -v
"""

import sys
import argparse
import logging

from src import solve_problem


def main():
    """Command-line interface for agent tree
    
    Follows bible principle: minimize complexity by hiding multiple steps 
    behind a single atomic action the LLM can run.
    """
    parser = argparse.ArgumentParser(
        description="Solve complex problems using hierarchical agent decomposition",
        epilog="Test system correctness: python -m pytest tests/ -v"
    )
    
    # Core required argument
    parser.add_argument(
        "problem",
        help="Problem description to solve"
    )
    
    # Optional complexity controls (minimal set)
    parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum recursion depth (default: 3)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system tests to verify correctness"
    )
    
    args = parser.parse_args()
    
    # Bible Rule 2 & 3: Single atomic command to prove correctness
    if args.test:
        import subprocess
        print("Running system correctness tests...")
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        sys.exit(result.returncode)
    
    # Configure logging (simplified)
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Solve the problem (hide complexity behind simple interface)
    try:
        result = solve_problem(args.problem, max_depth=args.max_depth)
        
        print(f"\n{'='*80}")
        print("FINAL SOLUTION:")
        print("="*80)
        print(result)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()