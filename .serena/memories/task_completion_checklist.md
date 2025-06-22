# Task Completion Checklist

When completing any coding task, always run these commands:

## 1. Code Formatting
```bash
black src/ tests/
```

## 2. Linting
```bash
flake8 src/ tests/
```

## 3. Type Checking
```bash
mypy src/
```

## 4. Run Tests
```bash
# For changes affecting unit tests
python -m pytest -v

# For system-wide changes or if uncertain
python -m pytest -c pytest-all.ini -v
```

## Important Notes
- NEVER commit changes unless explicitly asked by user
- All tests must pass before considering task complete
- If lint/typecheck commands are missing, ask user and suggest adding to CLAUDE.md
- Fix any errors found during these checks
- Being too proactive with commits will upset the user