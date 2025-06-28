#!/usr/bin/env python3
"""
Main entry point for agent tree system
"""

import sys
import argparse


def main():
    """Command-line interface for agent tree with decompose and solve subcommands"""
    parser = argparse.ArgumentParser(
        description="Agent Tree - Hierarchical Problem Solver"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Decompose command
    decompose_parser = subparsers.add_parser(
        'decompose',
        help='Decompose a task into subtasks'
    )
    decompose_parser.add_argument(
        'task_file',
        help='Path to task markdown file'
    )
    
    # Solve command
    solve_parser = subparsers.add_parser(
        'solve',
        help='Solve a decomposed task tree'
    )
    solve_parser.add_argument(
        'task_file',
        help='Path to root task markdown file'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute appropriate command
    if args.command == 'decompose':
        from decompose import decompose
        decompose(args.task_file)
    elif args.command == 'solve':
        from solve import solve
        solve(args.task_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()