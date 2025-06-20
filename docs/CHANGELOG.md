# Changelog

All notable changes to Agent Tree Simple will be documented in this file.

## [0.1.0] - 2024-06-17

### Added
- Initial implementation of agent tree system
- Recursive problem decomposition
- Context propagation between nodes
- Claude CLI integration
- Organized workspace output

### Changed
- Refactored decomposition system
  - Replaced `assess_complexity` with `decompose_problem`
  - Parent nodes now decide subtask complexity
  - Added explicit leaf node support
  - Unified approach for all node types

### Improved
- Modular code structure
  - Split monolithic file into focused modules
  - Organized into standard Python package layout
  - Clear separation of concerns

## Decomposition Changes Detail

### Before
```python
# Two-step process
complexity, subtasks, approach = node.assess_complexity(problem)
if complexity == "complex":
    # All subtasks treated the same
    for subtask in subtasks:
        solve_recursive(subtask)
```

### After
```python
# Single decomposition step with complexity labels
subtasks = node.decompose_problem(problem)  # Returns None or [(task, is_simple), ...]
for task, is_simple in subtasks:
    solve_recursive(task, is_leaf=is_simple)  # Leaf nodes can't recurse
```

### Benefits
- Cleaner architecture
- Better recursion control per branch
- Eliminates special cases
- More intuitive JSON format