# Agent Tree Simplification - Handoff Document

## Overview
This document guides the next engineer or agent through understanding and continuing the agent-tree simplification project. The project transforms a complex monolithic system into a clean two-phase architecture.

## Step 0: Familiarize Yourself with the Vision and System

### Read in this order:
1. **human_simplification_vision.txt** - The original vision (5 min read)
   - Understand the "why" - simplicity over complexity
   - Two-phase approach: decompose → human review → solve
   - Key principle: let errors crash during development

2. **simplification_plan.md** - The master plan (15 min read)
   - See the target architecture and pseudocode
   - Review progress checkboxes (most are ✅)
   - Focus on sections: "Target Pseudocode", "Current Status", "Next Steps"

3. **CLAUDE.md** - Project-specific instructions (3 min read)
   - Understand the system's purpose
   - Review key commands and architecture overview

## Step 1: Understand Current Implementation Status

### Check the implemented modules:
```bash
# See the new clean implementation
cat agent_tree.py      # Entry point with subcommands
cat decompose.py       # Recursive decomposition logic  
cat solve.py           # Bottom-up solving with dependencies
```

### Current state:
- ✅ Core modules implemented and working
- ✅ Entry point supports `decompose` and `solve` subcommands
- ✅ File structure follows the plan (_plan.md, _children/ folders)
- ❌ Integration tests failing due to interface mismatches
- ❌ Mock Claude needs updates to match actual behavior

## Step 2: Review Module Contracts and Interfaces

Read **docs/implementation/module_contracts.md** to understand:
- Function signatures: `decompose(task_file)`, `solve(task_file)`
- File structure contract
- Task markdown format

This is critical for fixing the test failures.

## Step 3: Understand the Test Failures

### Run tests to see current state:
```bash
# Run integration tests
python -m pytest tests/integration/test_integration.py -v

# Key failures to fix:
# 1. Mock claude prompt matching ("solving a specific task" vs "solve this task")
# 2. File creation expectations (plan files vs solution files)
# 3. Decompose file structure creation
```

### Files to examine for fixes:
1. **tests/integration/mock_claude.py** - Needs updates to:
   - Match actual prompt patterns
   - Create correct file structure
   - Update plan files instead of creating solution.md

2. **tests/integration/test_integration.py** - Needs updates to:
   - Look for correct prompt text
   - Check for plan file updates instead of solution.md
   - Match actual system behavior

## Step 4: Fix Integration Tests

### Priority fixes:

1. **Update mock_claude.py line 18**:
   ```python
   elif "solving a specific task" in prompt:  # Was "solve this task"
   ```

2. **Update file creation in mock_claude.py**:
   - Ensure decompose creates: `{name}_plan.md` and `{name}_children/`
   - Ensure solve updates plan files, not creates solution.md

3. **Update test assertions**:
   - Change assertions looking for "solution.md" to check plan file updates
   - Fix dependency test to match actual prompt text

## Step 5: Test the Full Workflow

After fixing tests, verify the complete system:

```bash
# Create a test task
echo "# Test Web Scraper

Build a web scraper that extracts articles from a news site." > test_scraper.md

# Phase 1: Decompose
python agent_tree.py decompose test_scraper.md

# Review created files
ls -la test_scraper_children/
cat test_scraper_plan.md

# Phase 2: Human review (optional edits)

# Phase 3: Solve
python agent_tree.py solve test_scraper.md

# Check results in plan files
```

## Step 6: Clean Up and Finalize

1. **Remove development artifacts**:
   ```bash
   rm -rf development_artifacts/
   rm -rf tmp/
   ```

2. **Consider old code removal**:
   - Decide if `src/` directory should be removed
   - Keep for reference or remove for clarity

3. **Update documentation**:
   - Update README with new usage examples
   - Add example workflow to docs/

## Key Files Reference

### Planning Documents (read first):
- `human_simplification_vision.txt` - Original vision
- `simplification_plan.md` - Master plan with progress
- `docs/implementation/module_contracts.md` - Interface definitions

### Implementation Files (understand the code):
- `agent_tree.py` - Entry point
- `decompose.py` - Decomposition logic
- `solve.py` - Solving logic

### Test Files (fix these):
- `tests/integration/mock_claude.py` - Mock implementation
- `tests/integration/test_integration.py` - Integration tests

### Meta Documentation:
- `AGENT_WORKFLOW_GUIDE.md` - How to orchestrate sub-agents
- `CLAUDE.md` - Project-specific Claude instructions

## Common Pitfalls to Avoid

1. **Don't add complexity** - The whole point is simplification
2. **Let errors crash** - Don't add try/except during development
3. **Follow the pseudocode** - simplification_plan.md has the target
4. **Test with real Claude** - After fixing mocks, test actual CLI

## Quick Command Reference

```bash
# Run all tests
python -m pytest -v

# Run specific test
python -m pytest tests/integration/test_integration.py::TestAgentTreeIntegration::test_simple_task_workflow -v

# Test with real Claude (slow but accurate)
python -m pytest tests/live_system/ -v -m live_system

# Format code
black agent_tree.py decompose.py solve.py
```

## Next Steps Summary

1. Fix mock_claude.py to match actual prompts and file creation
2. Update test assertions to match system behavior  
3. Run full test suite
4. Test with real example end-to-end
5. Clean up artifacts
6. Update user documentation

The system is 90% complete - just needs test fixes and cleanup!