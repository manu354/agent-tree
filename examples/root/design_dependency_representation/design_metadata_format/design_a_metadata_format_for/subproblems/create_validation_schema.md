# Create Validation Schema

## Type
simple

## Problem
Define validation rules and constraints for dependency metadata to ensure valid task graphs. Must detect circular dependencies, validate task references, enforce dependency type rules, and provide clear error messages. Schema should be implementable in common validation frameworks.

## Possible Solution
Create JSON Schema or similar validation specification defining required fields, valid dependency types, and graph constraints. Include rules like: no circular dependencies, all referenced tasks must exist, sequential chains must be acyclic. Provide validation levels (strict/permissive) and clear error reporting with suggested fixes.

## Notes
Validation is crucial for preventing runtime errors in agent-tree execution. Consider both static validation (at markdown parse time) and dynamic validation (at execution time). Schema should be extensible for future dependency types while maintaining backward compatibility.