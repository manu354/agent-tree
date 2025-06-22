# Code Style and Conventions

## General Style
- Python 3.x with type hints where appropriate
- Black formatter for consistent code style
- Flake8 for linting
- MyPy for type checking

## Key Design Principles
1. **NEVER have multiple solutions for the same problem** - evolve incrementally
2. **No fallback logic** - single clear path
3. **Minimize complexity** when adding features
4. **High-quality unit tests** that withstand mutation testing

## Testing Conventions
- Tests organized into `tests/unit/` and `tests/live_system/`
- Unit tests mock external dependencies
- Live system tests use real Claude CLI
- Test files follow `test_*.py` pattern
- Use pytest markers: @pytest.mark.unit, @pytest.mark.live_system, @pytest.mark.slow

## Code Organization
- Core logic in `src/` directory
- Clear separation of concerns between modules
- Context flows unidirectionally (parent → children)
- Each module has a single responsibility

## Documentation
- Only create documentation when explicitly requested
- Prefer editing existing files over creating new ones
- Keep comments minimal unless requested
- Use clear, descriptive variable and function names