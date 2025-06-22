# Validate Backward Compatibility

## Type
simple

## Problem
Ensure the new dependency system doesn't break existing agent trees. All current markdown files should work unchanged, defaulting to parallel execution. Test with existing examples.

## Possible Solution
Make dependency sections optional with sensible defaults. Files without dependencies treated as parallel siblings. Add compatibility tests. Document migration path for existing trees.

## Notes
Critical for adoption. Run existing test cases unchanged. Consider versioning strategy if needed. Ensure prompts still work for Claude without dependency knowledge.