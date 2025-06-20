# Agent Tree SWE-Benchmark Tests

This benchmark suite tests the Agent Tree system's ability to handle complex, hierarchical software engineering tasks inspired by the SWE-bench dataset.

## Overview

The benchmark includes two types of tests:

1. **Synthetic Benchmark**: A controlled test with a mini web application that has a multi-file bug
2. **Complex Refactoring Test**: Inspired by real SWE-bench problems requiring architectural changes

## Test Structure

### Synthetic Web App Bug (`test_synthetic_web_app_bug_fix`)

This test simulates a common software engineering scenario:
- A web application with Controller, Service, and Data layers
- A feature flag (`use_new_format`) that's incompletely implemented
- The bug requires coordinated changes across all three layers
- Tests the agent tree's ability to:
  - Decompose the problem hierarchically
  - Execute subtasks in the correct order
  - Coordinate changes across multiple files

**Files involved:**
- `controller.py`: User-facing API layer
- `service.py`: Business logic layer  
- `datastore.py`: Data access layer
- `test_user.py`: Test suite

**The Bug:**
When `use_new_format=True`, the system should return a `full_name` field, but:
- Datastore computes it but doesn't return it
- Service doesn't process the field
- Controller doesn't include it in the response

### Complex Refactoring Test (`test_complex_refactoring_task`)

This test simulates a larger architectural refactoring:
- A monolithic `Calculator` class violating SOLID principles
- Requires extracting operations into separate classes
- Needs to separate concerns (operations vs history)
- Tests the agent tree's ability to handle:
  - Complex multi-step refactoring
  - Creating new file structures
  - Maintaining backward compatibility

## Mock LLM System

The benchmark uses a `MockLLM` class that provides deterministic responses:
- Maps prompt keywords to pre-programmed responses
- Simulates task decomposition and planning
- Tracks call history for verification
- Ensures reproducible test results

## Running the Benchmark

```bash
python -m pytest test_swe_benchmark.py -v
```

## Extending the Benchmark

To add new test cases:

1. Create a new test method in `TestSWEBenchmark`
2. Set up the initial buggy/problematic code
3. Create appropriate mock LLM responses
4. Define the expected task decomposition
5. Verify the agent tree executes correctly

## Why These Tests Matter

1. **Hierarchical Decomposition**: Real software bugs often require understanding multiple layers
2. **Parallel Execution**: Some subtasks can be done independently (e.g., updating different files)
3. **Context Management**: The agent must maintain context across subtasks
4. **Real-World Complexity**: Inspired by actual SWE-bench problems that challenge current AI systems

## Future Improvements

- Add more SWE-bench inspired scenarios
- Test error handling and recovery
- Benchmark performance metrics
- Add tests for parallel subtask execution
- Include tests with actual file I/O operations