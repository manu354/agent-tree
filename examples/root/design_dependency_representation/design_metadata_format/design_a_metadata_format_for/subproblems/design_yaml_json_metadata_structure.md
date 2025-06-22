# Design YAML/JSON Metadata Structure

## Type
simple

## Problem
Create a structured format using YAML or JSON to express task dependencies in markdown files. Must support nested dependencies, multiple dependency types, and be easily parsed by both humans and machines. Should integrate cleanly with existing markdown content without disrupting readability.

## Possible Solution
Use YAML front matter or embedded blocks with fields like `dependencies: {parallel: [task1, task2], sequential: [task3, task4], depends_on: {task5: [task1, task2]}}`. Support both inline and block formats. Include metadata for execution hints, timeouts, and failure handling. Consider using standardized schema like JSON-LD for extensibility.

## Notes
YAML is more human-readable while JSON is more universally parseable. Consider supporting both with YAML as primary format. Must handle complex dependency graphs without becoming verbose. Integration with markdown should feel natural - perhaps using code blocks with special language tags like ```dependencies-yaml```.