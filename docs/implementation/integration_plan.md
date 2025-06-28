# Integration Plan for Agent Tree Simplification

## Overview
This document describes how we decompose the simplification plan into focused subtasks for individual agents, then integrate their solutions.

## Decomposition Strategy

We break the simplification into 4 focused subtasks, each with minimal but sufficient context:

### Task 1: Entry Point Refactoring (Simple)
**File**: `subtask_entry_point.md`
**Goal**: Add subcommand support to agent_tree.py
**Dependencies**: None
**Context Needed**: Just the command interface design

### Task 2: Decompose Module (Complex)
**File**: `subtask_decompose_module.md`
**Goal**: Create decompose.py with recursive decomposition logic
**Dependencies**: Task 1 (needs entry point)
**Context Needed**: Pseudocode, file structure, Claude integration

### Task 3: Solve Module (Complex)
**File**: `subtask_solve_module.md`
**Goal**: Create solve.py with dependency resolution and execution
**Dependencies**: Task 1 (needs entry point)
**Context Needed**: Pseudocode, tree generation, Claude integration

### Task 4: Integration & Testing (Simple)
**File**: `subtask_integration.md`
**Goal**: Ensure all components work together
**Dependencies**: Tasks 1, 2, 3
**Context Needed**: Full system flow, example usage

## Integration Sequence

### Parallel Execution (Recommended)

All three tasks can run **completely in parallel**:

1. **Task 1**: Entry Point (Independent)
   - Just needs function signatures from contract
   
2. **Task 2**: Decompose Module (Independent)
   - Can create own test harness
   - Tests with mock entry point
   
3. **Task 3**: Solve Module (Independent)
   - Can create test file structures
   - Tests with mock entry point

4. **Task 4**: Integration (Depends on 1,2,3)
   - Runs after all others complete
   - Tests the real integration

### Why This Works

- **Defined contracts**: See `module_contracts.md`
- **No shared state**: Modules communicate only through files
- **Clear interfaces**: Just two function signatures
- **Independent testing**: Each module can verify itself

## Integration Points

### Between Entry Point and Modules
```python
# agent_tree.py will call:
from decompose import decompose
from solve import solve

# Based on subcommand:
if args.command == 'decompose':
    decompose(args.task_file)
elif args.command == 'solve':
    solve(args.task_file)
```

### File System Contract
- Decompose creates: `{name}_plan.md`, `{name}_children/`
- Solve reads: Same structure, updates plan files
- No shared state except file system

### Error Handling
- Let errors bubble up (development phase)
- Each module fails independently
- Clear stack traces for debugging

## Success Criteria

1. Task 1 complete → Can run `python agent_tree.py decompose --help`
2. Task 2 complete → Can decompose a task into file structure
3. Task 3 complete → Can solve a task tree with dependencies
4. Task 4 complete → Full workflow works end-to-end

## Tips for Agents

- **Stay focused**: Only implement what's in your subtask
- **Don't over-engineer**: Keep it simple, let errors crash
- **Follow the pseudocode**: It's your north star
- **Ask if unclear**: Better to clarify than assume

## Final Integration

Once all subtasks complete:
1. Merge code changes
2. Run integration test from Task 4
3. Update documentation
4. Remove old monolithic code