#!/bin/bash

# Helper script to monitor agent progress

echo "=== Agent Progress Monitor ==="
echo ""

while true; do
    clear
    echo "=== Agent Progress Monitor === $(date)"
    echo ""
    
    # Check for completion markers
    echo "Completion Status:"
    [[ -f task1_complete.marker ]] && echo "✓ Task 1: Entry Point" || echo "⏳ Task 1: Entry Point"
    [[ -f task2_complete.marker ]] && echo "✓ Task 2: Decompose Module" || echo "⏳ Task 2: Decompose Module"
    [[ -f task3_complete.marker ]] && echo "✓ Task 3: Solve Module" || echo "⏳ Task 3: Solve Module"
    [[ -f task4_complete.marker ]] && echo "✓ Task 4: Integration" || echo "⏳ Task 4: Integration"
    
    echo ""
    echo "Log Activity (last 5 lines):"
    echo ""
    
    if [[ -f task1.log ]]; then
        echo "--- Task 1 Log ---"
        tail -n 5 task1.log
        echo ""
    fi
    
    if [[ -f task2.log ]]; then
        echo "--- Task 2 Log ---"
        tail -n 5 task2.log
        echo ""
    fi
    
    if [[ -f task3.log ]]; then
        echo "--- Task 3 Log ---"
        tail -n 5 task3.log
        echo ""
    fi
    
    if [[ -f task4.log ]]; then
        echo "--- Task 4 Log ---"
        tail -n 5 task4.log
        echo ""
    fi
    
    echo ""
    echo "Press Ctrl+C to exit monitor"
    
    sleep 5
done