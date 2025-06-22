# Extend Markdown Structure

## Type
simple

## Problem
Extend the current markdown file structure to include dependency information without breaking existing parsers. Determine where dependency data should live and how to maintain backward compatibility.

## Possible Solution
Add optional "## Dependencies" or "## Execution" section after "## Notes". Use structured text that degrades gracefully. Existing files without this section default to parallel execution.

## Notes
Must work with existing markdown_utils.py functions. Consider how find_subproblem_files and is_problem_complex will handle new sections. Ensure Claude can reliably generate valid dependency specifications.