# Develop Inline Annotation Syntax

## Type
simple

## Problem
Design a lightweight inline syntax for expressing simple dependencies directly in markdown text without requiring separate metadata blocks. Should be intuitive, non-intrusive, and support common dependency patterns. Must not interfere with standard markdown rendering.

## Possible Solution
Use comment-style annotations like `<!-- depends-on: task1 -->` or inline markers like `[->task1,task2]` for sequential and `[||task1,task2]` for parallel. Could leverage existing markdown link syntax: `[Task Name](#task-id){.parallel}`. Support shorthand for common patterns. Make annotations invisible in rendered markdown.

## Notes
Balance between expressiveness and simplicity. Inline syntax should handle 80% of use cases with complex dependencies relegated to metadata blocks. Consider compatibility with popular markdown processors and IDEs. Should feel natural to write and read in raw markdown form.