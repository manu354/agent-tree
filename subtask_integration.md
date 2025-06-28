# Subtask: Integration and Testing

## Goal
Ensure all components work together seamlessly and test the full workflow

## Prerequisites
- Task 1: Entry point with subcommands complete
- Task 2: Decompose module complete  
- Task 3: Solve module complete

## Integration Requirements

### 1. Verify Module Connections

**Entry Point → Decompose**
```bash
python agent_tree.py decompose test_task.md
```
Should:
- Import decompose module successfully
- Call decompose() with the file path
- Create the expected file structure

**Entry Point → Solve**
```bash
python agent_tree.py solve test_task.md
```
Should:
- Import solve module successfully
- Call solve() with the file path
- Process the task tree correctly

### 2. End-to-End Test Case

Create a test task file `calculator.md`:
```markdown
# Build a Calculator CLI

Create a command-line calculator that supports basic operations (add, subtract, multiply, divide) and can handle multiple numbers in one expression.
```

**Step 1: Decompose**
```bash
python agent_tree.py decompose calculator.md
```

Expected output structure:
```
calculator_plan.md
calculator_children/
├── parse_expression.md    # Complex
├── handle_operations.md   # Simple
└── display_result.md      # Simple
```

**Step 2: Human Review**
- Check the generated files
- Optionally modify task descriptions or dependencies

**Step 3: Solve**
```bash
python agent_tree.py solve calculator.md
```

Should:
1. Process parse_expression first (since it's complex, recurse)
2. Then handle_operations and display_result
3. Finally solve the root calculator task
4. Update all plan files with progress

### 3. Integration Checks

**File System Consistency**
- [ ] All paths are relative to initial task file
- [ ] No hardcoded paths
- [ ] Works from any directory

**State Management**
- [ ] Decompose resets globals between runs
- [ ] Solve tracks solved tasks correctly
- [ ] No state leakage between phases

**Error Propagation**
- [ ] Claude errors show clear messages
- [ ] File not found errors are descriptive
- [ ] Stack traces point to actual issues

### 4. Common Integration Issues to Check

1. **Import Paths**
   - Ensure decompose.py and solve.py are importable
   - Check Python path if needed

2. **Working Directory**
   - Claude should run in the correct directory
   - File creation should be relative to task location

3. **File Name Extraction**
   - Consistent handling of paths with/without .md
   - Handle paths with directories correctly

4. **Tree Generation**
   - Skip _plan.md files in tree display
   - Handle empty directories gracefully

## Testing Script

Create `test_integration.py`:
```python
import subprocess
import os
import shutil

def test_full_workflow():
    # Clean up any previous test
    if os.path.exists('calculator_plan.md'):
        os.remove('calculator_plan.md')
    if os.path.exists('calculator_children'):
        shutil.rmtree('calculator_children')
    
    # Create test task
    with open('calculator.md', 'w') as f:
        f.write('# Build a Calculator CLI\n\n...')
    
    # Test decompose
    result = subprocess.run(['python', 'agent_tree.py', 'decompose', 'calculator.md'])
    assert result.returncode == 0
    assert os.path.exists('calculator_plan.md')
    assert os.path.exists('calculator_children')
    
    # Test solve
    result = subprocess.run(['python', 'agent_tree.py', 'solve', 'calculator.md'])
    assert result.returncode == 0
    
    print("Integration test passed!")

if __name__ == '__main__':
    test_full_workflow()
```

## Success Criteria
- [ ] Full workflow runs without errors
- [ ] File structure matches expectations
- [ ] Dependencies are resolved correctly
- [ ] Plan files show progress updates
- [ ] Can run from any directory
- [ ] Clear error messages when things fail

## Final Cleanup
Once integration is verified:
1. Remove old monolithic code from src/
2. Update README with new usage
3. Update any existing tests
4. Consider adding the integration test to the test suite

## Notes
- This task is about making sure everything works together
- Don't add new features - just verify and fix integration
- Document any gotchas discovered during integration
- Keep the test case simple but representative