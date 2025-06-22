# Examine Markdown Structure

## Type
simple

## Problem
Analyze how the markdown file structure created during decomposition represents task relationships. Determine if the file system hierarchy and markdown format can be extended to capture dependency information.

## Possible Solution
Review markdown format in prompts.py, file creation in decompose_to_markdown(), and directory structure. Evaluate if Type field or new sections could encode dependencies while maintaining backward compatibility.

## Notes
Current format uses Type: simple/complex only. Consider how dependency information could be added to markdown files without breaking existing parsing.