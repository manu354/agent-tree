"""
Module for recursively decomposing complex tasks into subtasks using Claude
"""

import os
import subprocess
from pathlib import Path

# Global state for tracking
node_count = 0
seen_tasks = set()


def extract_name(task_file: str) -> str:
    """Extract base name from file path without .md extension
    
    Args:
        task_file: Path to the .md task file
        
    Returns:
        Base name without extension
    """
    return Path(task_file).stem


def is_complex(file_path: str) -> bool:
    """Check if a task file is marked as complex
    
    Args:
        file_path: Path to the .md file
        
    Returns:
        True if the file contains '## Type' section with 'complex'
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Look for ## Type section
        lines = content.split('\n')
        in_type_section = False
        
        for line in lines:
            if line.strip() == '## Type':
                in_type_section = True
                continue
            if in_type_section:
                if line.strip().startswith('#'):
                    # Reached next section
                    break
                if 'complex' in line.lower():
                    return True
                if 'simple' in line.lower():
                    return False
        
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def decompose_prompt(task_file: str) -> str:
    """Create a prompt for Claude to decompose a task
    
    Args:
        task_file: Path to the .md task file
        
    Returns:
        The prompt string for Claude
    """
    # Read task content
    with open(task_file, 'r') as f:
        task_content = f.read()
    
    name = extract_name(task_file)
    
    prompt = f"""You are helping decompose a complex task into subtasks.

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
"""
    
    return prompt


def agent(prompt: str, working_dir: str = None):
    """Call Claude CLI with the given prompt
    
    Args:
        prompt: The prompt to send to Claude
        working_dir: Working directory for Claude (defaults to current directory)
    """
    if working_dir is None:
        working_dir = os.getcwd()
    
    cmd = ["claude", "--dangerously-skip-permissions", "-p", prompt]
    
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        cwd=working_dir
    )
    
    if result.returncode != 0:
        print(result.stderr)
        raise Exception(f"Claude failed with code {result.returncode}")
    
    print(result.stdout)


def decompose(task_file: str) -> None:
    """
    Decomposes a task file into subtasks.
    
    Args:
        task_file: Path to the .md task file
        
    Side effects:
        - Creates {name}_plan.md
        - Creates {name}_children/ folder with subtask .md files
        - Recursively decomposes complex subtasks
    """
    global node_count, seen_tasks
    
    if node_count >= 5:
        print(f"Hit 5-node limit, skipping {task_file}")
        return
    
    task_name = extract_name(task_file)
    children_dir = f"{task_name}_children"
    
    # Get the directory containing the task file
    task_dir = os.path.dirname(task_file) or '.'
    
    node_count += 1
    print(f"\nNode {node_count}/5: Decomposing {task_file}")
    
    # Agent creates: plan file + children tasks in children_dir
    prompt = decompose_prompt(task_file)
    agent(prompt, working_dir=task_dir)
    seen_tasks.add(task_file)
    
    # Check if children directory was created
    children_path = os.path.join(task_dir, children_dir)
    if not os.path.exists(children_path):
        print(f"No children directory created for {task_file}, treating as simple task")
        return
    
    # Process each .md file in children_dir
    for filename in os.listdir(children_path):
        if filename.endswith('.md'):
            child_file = os.path.join(children_path, filename)
            
            if child_file not in seen_tasks:
                seen_tasks.add(child_file)
                
                if is_complex(child_file):
                    print(f"Found complex subtask: {child_file}")
                    decompose(child_file)
                else:
                    print(f"Found simple subtask: {child_file}")