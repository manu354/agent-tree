# Parse Dependency Metadata

## Type
simple

## Problem
Extract dependency information from task node metadata. Parse the dependency format that distinguishes between parallel (O->a,b,c) and sequential (a->b->c) patterns. Handle missing or malformed dependency specifications gracefully.

## Possible Solution
Create a parser function that reads node metadata and returns a structured representation of dependencies. Use regex or simple string parsing to extract dependency patterns. Return a dictionary with nodes as keys and their dependencies as values.

## Notes
This is the foundation for dependency-aware execution. The parser must be robust and handle various edge cases like circular dependencies or incomplete specifications. Should integrate with existing node structure without breaking backward compatibility.