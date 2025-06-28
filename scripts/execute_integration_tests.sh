#!/bin/bash
# Execute integration tests for agent-tree system

echo "========================================="
echo "Agent Tree Integration Tests"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test file
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "${YELLOW}Running ${test_name}...${NC}"
    
    if python "$test_file" -v 2>&1; then
        echo -e "${GREEN}✓ ${test_name} passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ ${test_name} failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    echo ""
}

# Check if mock_claude.py exists
if [ ! -f "tests/integration/mock_claude.py" ]; then
    echo -e "${RED}Error: tests/integration/mock_claude.py not found!${NC}"
    exit 1
fi

# Make sure mock_claude.py is executable
chmod +x tests/integration/mock_claude.py

echo "Starting test execution..."
echo ""

# Run unit tests
echo "=== Unit Tests ==="
run_test "tests/unit/new_system/test_decompose.py" "Decompose Module Tests"
run_test "tests/unit/new_system/test_solve.py" "Solve Module Tests"

# Run integration tests
echo "=== Integration Tests ==="
run_test "tests/integration/test_integration.py" "Full Workflow Integration Tests"

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo -e "Total Tests Run: ${TOTAL_TESTS}"
echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi