# Subtask: Entry Point Refactoring

## Goal
Modify `agent_tree.py` to support two subcommands: `decompose` and `solve`

## Current State
The current `agent_tree.py` takes a problem description as a direct argument and runs both decomposition and solving in one go.

## Target State
```bash
python agent_tree.py decompose task_file.md
python agent_tree.py solve task_file.md
```

## Implementation Requirements

1. **Add Subcommands**
   - Use argparse subparsers
   - `decompose` subcommand: Takes a task file path
   - `solve` subcommand: Takes a task file path
   - Both should have --help support

2. **Entry Point Structure**
   ```python
   def main():
       parser = argparse.ArgumentParser(description="Agent Tree - Hierarchical Problem Solver")
       subparsers = parser.add_subparsers(dest='command', help='Commands')
       
       # Decompose command
       decompose_parser = subparsers.add_parser('decompose', help='Decompose a task into subtasks')
       decompose_parser.add_argument('task_file', help='Path to task markdown file')
       
       # Solve command
       solve_parser = subparsers.add_parser('solve', help='Solve a decomposed task tree')
       solve_parser.add_argument('task_file', help='Path to root task markdown file')
       
       args = parser.parse_args()
       
       if args.command == 'decompose':
           from decompose import decompose
           decompose(args.task_file)
       elif args.command == 'solve':
           from solve import solve
           solve(args.task_file)
       else:
           parser.print_help()
   ```

3. **Remove Old Logic**
   - Remove the old single-command flow
   - Keep any useful utility functions that might be needed

4. **Error Handling**
   - Let import errors crash (modules might not exist yet)
   - Let file not found errors crash
   - Simple and clear during development

## Testing
```bash
# Should show help with both subcommands
python agent_tree.py --help

# Should show decompose-specific help
python agent_tree.py decompose --help

# Should show solve-specific help  
python agent_tree.py solve --help

# Should attempt to import and run decompose
python agent_tree.py decompose test.md

# Should attempt to import and run solve
python agent_tree.py solve test.md
```

## Success Criteria
- [ ] Subcommands are properly registered
- [ ] Help text is clear and useful
- [ ] Attempts to import and call appropriate modules
- [ ] Clean, simple implementation

## Notes
- This is the foundation that enables the other modules
- Keep it minimal - just argument parsing and dispatch
- Don't worry about the decompose/solve module implementations yet