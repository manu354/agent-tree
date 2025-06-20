# Simplified Agent Tree Vision

## The New Way: Let Claude Do More

Instead of complex Python recursion, we let Claude create the entire problem structure as markdown files in one go.

## How It Works

```
1. User gives problem
   ↓
2. Claude creates markdown structure:
   workspace/
   ├── tasks/
   │   └── build_scraper.md
   └── build_scraper/
       └── subproblems/
           ├── 1_parse_html.md      [simple]
           ├── 2_handle_auth.md     [complex]
           └── 3_save_data.md       [simple]
   ↓
3. System pauses - "Review files, type 'continue' when ready"
   ↓
4. User can edit any markdown file
   ↓
5. User types 'continue'
   ↓
6. Execute from bottom up:
   - First: All [simple] tasks
   - Then: [complex] tasks using simple results
   - Finally: Integrate everything
```

## What Each Markdown File Contains

```markdown
# Parse HTML Content

## Type
simple

## Problem
Extract data from HTML pages using BeautifulSoup.
Need to handle various HTML structures and malformed content.
(max 100 words)

## Possible Solution  
Use BeautifulSoup with lxml parser. Create extraction functions
for different data types. Add error handling for malformed HTML.
(max 100 words)

## Notes
Consider using CSS selectors for flexibility. May need to handle
JavaScript-rendered content later.
(max 100 words)
```

## Key Simplifications

1. **No Python recursion** - Claude creates all files at once
2. **No fallback logic** - One way to do things
3. **No complex state** - Markdown files ARE the state
4. **No MCP/Zen modes** - Just Claude CLI
5. **Minimal Context** - Just root problem, parent task, current task

## Why This Is Better

- **Simpler code** - Probably 70% less code
- **User control** - Edit markdown files with any editor
- **Transparent** - See entire plan before execution
- **Reliable** - No complex recursion or state management
- **Focused** - Claude does what it's best at: understanding and planning

## Example Interaction

```bash
$ python agent_tree.py "Build a web scraper for news articles"

Creating problem structure...
✓ Created: workspace/tasks/build_web_scraper.md
✓ Created: workspace/build_web_scraper/subproblems/1_parse_articles.md [simple]
✓ Created: workspace/build_web_scraper/subproblems/2_handle_pagination.md [complex]
✓ Created: workspace/build_web_scraper/subproblems/3_extract_metadata.md [simple]
✓ Created: workspace/build_web_scraper/subproblems/4_save_to_database.md [simple]

Workspace: workspace/agent_tree_20240620_150000/
Review and modify markdown files as needed.

Type 'continue' to execute: continue

Executing tasks...
✓ Completed: parse_articles
✓ Completed: extract_metadata  
✓ Completed: save_to_database
✓ Completed: handle_pagination (using results from simple tasks)
✓ Final solution integrated

Solution saved to: workspace/final_solution.md
```

## The Magic: Better Claude Prompts

Instead of complex Python logic, we use a single powerful prompt that tells Claude to:
1. Analyze the problem
2. Create the directory structure
3. Write concise markdown files
4. Label each as simple/complex
5. Maintain word limits

This leverages Claude's strength in understanding and planning, rather than trying to control everything through code.