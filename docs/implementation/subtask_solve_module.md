# Subtask: Solve Module Implementation

## Goal
Create `solve.py` module that solves a decomposed task tree by working bottom-up with dependency resolution

## Context
Reference the pseudocode from simplification_plan.md:
```python
# Tree search, postorder traversal (leaves first)
solve(task):
    if has_child_or_dependency:
        dependent = get_dependent(task)  # Look for links in ### Dependents
        solve(dependent)
    
    # Generate tree with one-line summaries
    tree_context = generate_tree_with_summaries(workspace_root)
    agent(solve_prompt(task, tree_context))
    # Agent updates plan file with progress and results
```

## Implementation Requirements

### 1. Core Functions

**get_dependent(task_file)**
- Read the markdown file
- Find `### Dependents` section
- Extract markdown links like `[Task Name](path/to/task.md)`
- Return list of dependent file paths
- Return empty list if no dependents section

**has_child_or_dependency(task_file)**
- Check if `{name}_children/` folder exists
- Or check if task has dependents
- Return True if either exists

**generate_tree_with_summaries(root_path, current_task)**
- Walk the file system starting from root
- Build a tree structure showing all .md files (skip _plan.md files)
- Extract first line from each .md file as summary
- Mark current task with `[YOU ARE HERE]`
- Return as formatted string

Example output:
```
workspace/
├── web_scraper.md - "Build a web scraper for news sites"
└── web_scraper_children/
    ├── fetch_urls.md - "Download HTML from URLs"
    ├── parse_html.md - "Parse HTML into structured data" [YOU ARE HERE]
    └── extract_data.md - "Extract article content"
        └── extract_data_children/
            ├── find_selectors.md - "Find CSS selectors"
            └── handle_pagination.md - "Handle multi-page articles"
```

**solve_prompt(task_file, tree_context)**
- Create prompt that includes:
  - The task content
  - The tree context showing where this task fits
  - Instructions to read other files if needed
  - Instructions to update the plan file with progress

**agent(prompt, working_dir)**
- Same as in decompose module
- Call Claude CLI with the prompt
- Let Claude update files and write code

### 2. Traversal Logic

```python
def solve(task_file):
    # Process dependencies first
    for dependent in get_dependent(task_file):
        if dependent not in solved_tasks:
            solve(dependent)
    
    # Process children (if any)
    children_dir = f"{extract_name(task_file)}_children"
    if os.path.exists(children_dir):
        for child in os.listdir(children_dir):
            if child.endswith('.md') and not child.endswith('_plan.md'):
                child_path = os.path.join(children_dir, child)
                if child_path not in solved_tasks:
                    solve(child_path)
    
    # Now solve this task
    tree_context = generate_tree_with_summaries(workspace_root, task_file)
    agent(solve_prompt(task_file, tree_context), os.path.dirname(task_file))
    solved_tasks.add(task_file)
```

### 3. Solve Prompt Template

```
You are solving a specific task within a larger system.

Here's where your task fits in the overall structure:
{tree_context}

Current task file: {task_file}
Task content:
{task_content}

Related plan file: {plan_file}

Instructions:
1. Read the task carefully
2. You can read other task files if you need context about dependencies or integration
3. Implement the solution by creating/editing necessary code files
4. Update the plan file with:
   - Progress notes
   - Any decisions made
   - Summary of what was implemented
   
Focus on solving just this specific task. Other tasks in the tree will be handled separately.
```

### 4. Global State

```python
# Track which tasks have been solved
solved_tasks = set()

# Remember the workspace root for tree generation
workspace_root = None
```

## Testing Approach

1. Create a simple task tree structure manually
2. Test individual functions (get_dependent, tree generation)
3. Test full solve on a simple tree
4. Verify correct traversal order
5. Check that plan files are updated

## Success Criteria
- [ ] Correctly identifies and processes dependencies
- [ ] Traverses tree in postorder (leaves first)
- [ ] Generates helpful tree context
- [ ] Updates plan files with progress
- [ ] Handles both simple and complex tasks
- [ ] Clear error messages on failures

## Notes
- Dependencies are different from parent-child relationships
- A task might depend on a sibling or cousin task
- Let errors crash for clear debugging
- The tree context is key for helping Claude understand scope
- Plan files serve as both documentation and progress tracking