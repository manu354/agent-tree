# Suggested Commands for Agent Tree Simple

## Running the System
```bash
# Main usage
python agent_tree_simple.py "Your complex problem description"
```

## Testing
```bash
# Run unit tests only (default)
python -m pytest -v

# Run specific unit test file
python -m pytest tests/unit/test_agent_tree_simple.py -v

# Run ALL tests including live system tests
python -m pytest -c pytest-all.ini -v

# Run only live system tests
python -m pytest tests/live_system/ -v -m live_system

# Skip slow tests
python -m pytest -v -m "not slow"
```

## Code Quality
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## System Commands (Darwin/macOS)
- `ls -la`: List files with details
- `find . -name "*.py"`: Find Python files
- `grep -r "pattern" .`: Search for pattern recursively
- `git status`: Check git status
- `git diff`: View unstaged changes
- `git log --oneline -10`: View recent commits