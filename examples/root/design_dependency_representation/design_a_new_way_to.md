# Design a New Way to Represent Task Dependencies

## Overview
Design a representation system that distinguishes between parallel (O->a,b,c) and sequential (a->b->c) execution patterns in the agent tree structure, without breaking existing functionality.

## Key Challenges
- Current system treats all children as implicitly parallel
- No explicit dependency representation between sibling tasks
- Need to maintain backward compatibility
- Must integrate with existing markdown decomposition approach

## Design Goals
- Clear distinction between parallel and sequential dependencies
- Minimal changes to existing codebase
- Human-readable representation in markdown files
- Support for mixed parallel/sequential patterns (e.g., (a,b)->c->d)

## Subproblems
1. Analyze dependency patterns
2. Design metadata format
3. Extend markdown structure
4. Update execution logic
5. Validate backward compatibility