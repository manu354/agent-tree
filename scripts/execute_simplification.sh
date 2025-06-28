#!/bin/bash

# Execute Agent Tree Simplification Tasks in Parallel
# This script spawns multiple Claude agents to work on different parts of the simplification

set -euo pipefail

echo "=== Agent Tree Simplification Execution Script ==="
echo "Working directory: $(pwd)"
echo ""

# Clean up any previous markers and logs
echo "Cleaning up previous run artifacts..."
rm -f task*_complete.marker
rm -f task*.log

# Prepare Task 1 Prompt (Entry Point)
TASK1_PROMPT="You are helping simplify the agent-tree system by implementing one focused subtask.

Current working directory: $(pwd)

Your task:
$(cat subtask_entry_point.md)

Please implement this task by modifying agent_tree.py as described.

IMPORTANT: When complete, create a file named 'task1_complete.marker' to signal completion."

# Prepare Task 2 Prompt (Decompose Module)
TASK2_PROMPT="You are helping simplify the agent-tree system by implementing one focused subtask.

Current working directory: $(pwd)

Your task:
$(cat subtask_decompose_module.md)

Module interface contracts:
$(cat module_contracts.md)

Please create decompose.py as described. You can look at src/agent_tree.py and src/claude_client.py for Claude CLI integration patterns.

IMPORTANT: When complete, create a file named 'task2_complete.marker' to signal completion."

# Prepare Task 3 Prompt (Solve Module)
TASK3_PROMPT="You are helping simplify the agent-tree system by implementing one focused subtask.

Current working directory: $(pwd)

Your task:
$(cat subtask_solve_module.md)

Module interface contracts:
$(cat module_contracts.md)

Please create solve.py as described. You can look at src/agent_tree.py and src/claude_client.py for Claude CLI integration patterns.

IMPORTANT: When complete, create a file named 'task3_complete.marker' to signal completion."

# Launch all three agents in parallel
echo "=== Launching Parallel Agents ==="
echo ""

echo "[$(date)] Launching Task 1: Entry Point Refactoring..."
claude -p "$TASK1_PROMPT" --dangerously-skip-permissions > task1.log 2>&1 &
PID1=$!
echo "  PID: $PID1"

echo "[$(date)] Launching Task 2: Decompose Module..."
claude -p "$TASK2_PROMPT" --dangerously-skip-permissions > task2.log 2>&1 &
PID2=$!
echo "  PID: $PID2"

echo "[$(date)] Launching Task 3: Solve Module..."
claude -p "$TASK3_PROMPT" --dangerously-skip-permissions > task3.log 2>&1 &
PID3=$!
echo "  PID: $PID3"

echo ""
echo "All agents launched. Waiting for completion..."
echo "You can monitor progress by tailing the log files in another terminal:"
echo "  tail -f task1.log"
echo "  tail -f task2.log"
echo "  tail -f task3.log"
echo ""

# Wait for all background processes to complete
wait $PID1 $PID2 $PID3

echo ""
echo "[$(date)] All agents have finished execution."
echo ""

# Check completion status
echo "=== Checking Completion Status ==="
FAILED=0

if [[ -f task1_complete.marker ]]; then
    echo "✓ Task 1 (Entry Point) completed successfully"
else
    echo "✗ Task 1 (Entry Point) FAILED - check task1.log"
    FAILED=1
fi

if [[ -f task2_complete.marker ]]; then
    echo "✓ Task 2 (Decompose Module) completed successfully"
else
    echo "✗ Task 2 (Decompose Module) FAILED - check task2.log"
    FAILED=1
fi

if [[ -f task3_complete.marker ]]; then
    echo "✓ Task 3 (Solve Module) completed successfully"
else
    echo "✗ Task 3 (Solve Module) FAILED - check task3.log"
    FAILED=1
fi

echo ""

if [[ $FAILED -eq 0 ]]; then
    echo "=== All tasks completed successfully! ==="
    echo ""
    echo "Ready for Task 4 (Integration Testing)."
    echo ""
    read -p "Would you like to launch Task 4 now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Prepare Task 4 Prompt
        TASK4_PROMPT="You are helping complete the agent-tree simplification by running integration tests.

Current working directory: $(pwd)

The following components have been implemented:
- agent_tree.py with decompose/solve subcommands (Task 1)
- decompose.py module (Task 2)  
- solve.py module (Task 3)

Your task:
$(cat subtask_integration.md)

Please test the integration and fix any issues found.

IMPORTANT: When complete, create a file named 'task4_complete.marker' to signal completion."

        echo "[$(date)] Launching Task 4: Integration Testing..."
        claude -p "$TASK4_PROMPT" --dangerously-skip-permissions > task4.log 2>&1
        
        if [[ -f task4_complete.marker ]]; then
            echo "✓ Task 4 (Integration) completed successfully"
            echo ""
            echo "=== SIMPLIFICATION COMPLETE! ==="
            echo "The agent-tree system has been successfully refactored."
        else
            echo "✗ Task 4 (Integration) FAILED - check task4.log"
        fi
    fi
else
    echo "=== Some tasks failed ==="
    echo "Please check the log files for errors before proceeding."
    echo ""
    echo "Log files:"
    ls -la task*.log
fi

echo ""
echo "Execution script complete."