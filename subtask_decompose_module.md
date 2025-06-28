# Subtask: Decompose Module Implementation

## Goal
Create `decompose.py` module that recursively decomposes complex tasks into subtasks using Claude

## Context
Reference the pseudocode from simplification_plan.md:
```python
# Global state for tracking
node_count = 0
seen_tasks = set()

def decompose(task_file):
    global node_count, seen_tasks
    
    if node_count >= 5:
        return  # Hit 5-node limit
    
    task_name = extract_name(task_file)
    children_dir = f"{task_name}_children"
    
    node_count += 1
    # Agent creates: plan file + children tasks in children_dir
    # Each child .md specifies if it's simple or complex
    agent(decompose_prompt(task_file))
    seen_tasks.add(task_file)
    
    for each .md file in children_dir not in seen_tasks:
        seen_tasks.add(file)
        if is_complex(file):  # Claude already marked it as 'complex'
            decompose(file)  # No file moving needed!
```

## Implementation Requirements

### 1. Core Functions

**extract_name(task_file)**
- Extract base name from file path (without .md extension)
- Example: "web_scraper.md" → "web_scraper"

**is_complex(file_path)**
- Read markdown file
- Look for `## Type` section
- Return True if contains "complex", False if "simple"

**decompose_prompt(task_file)**
- Create prompt for Claude that instructs it to:
  - Create a plan file: `{name}_plan.md`
  - Create a children folder: `{name}_children/`
  - Create subtask files in the children folder
  - Mark each subtask with `## Type` as either "simple" or "complex"
  - Include `### Dependents` section if needed

**agent(prompt)**
- Call Claude CLI using subprocess
- Pass the prompt and let Claude create the files
- Working directory should be the parent of the task file
- Let any errors crash with clear stack traces

### 2. File Structure Created

For input `web_scraper.md`, Claude should create:
```
web_scraper_plan.md          # Analysis and links to children
web_scraper_children/
├── fetch_urls.md           # With ## Type: simple
├── parse_html.md           # With ## Type: simple  
└── extract_data.md         # With ## Type: complex
```

### 3. Claude Prompt Template

```
You are helping decompose a complex task into subtasks.

Task file: {task_file}
Task content:
{task_content}

Please:
1. Create a file named `{name}_plan.md` with:
   - Analysis of how to break down this task
   - Links to the subtasks you'll create
   
2. Create a folder named `{name}_children/`

3. In that folder, create .md files for each subtask with:
   # [Subtask Title]
   ## Type
   [simple or complex - simple means it can be solved directly, complex needs further breakdown]
   ## Summary  
   [One line summary]
   ## Task
   [Detailed description]
   ### Dependents
   [List of markdown links to other tasks that depend on this, if any]

Keep subtask names short and descriptive (e.g., fetch_urls.md, parse_html.md).
```

### 4. Claude CLI Integration

```python
import subprocess
import os

def agent(prompt, working_dir):
    result = subprocess.run(
        ['claude', '-m', 'claude-3-5-sonnet-20241022'],
        input=prompt,
        text=True,
        capture_output=True,
        cwd=working_dir
    )
    if result.returncode != 0:
        print(result.stderr)
        raise Exception(f"Claude failed with code {result.returncode}")
```

## Testing Approach

1. Create a simple test task file
2. Run decompose on it
3. Verify the file structure is created correctly
4. Check that complex subtasks are detected
5. Verify recursion stops at 5 nodes

## Success Criteria
- [ ] Creates correct file structure via Claude
- [ ] Recursively decomposes complex tasks
- [ ] Respects 5-node limit
- [ ] Clear error messages on failures
- [ ] Follows the pseudocode closely

## Notes
- Let errors crash - no try/except blocks
- Keep the implementation simple and readable
- Trust Claude to create the right structure with a good prompt
- File paths are relative to the initial task file location