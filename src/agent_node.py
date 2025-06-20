"""
Agent node implementation for hierarchical problem solving
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .context import Context

# Try to import the direct MCP client
try:
    import os
    if os.environ.get('DISABLE_MCP_CLIENT', '').lower() in ('1', 'true', 'yes'):
        HAS_MCP_CLIENT = False
    else:
        from .mcp_client import decompose_problem_sync
        HAS_MCP_CLIENT = True
except ImportError:
    HAS_MCP_CLIENT = False

logger = logging.getLogger(__name__)


class AgentNode:
    """Minimal agent node using claude CLI"""
    
    def __init__(self, name: str, work_dir: Path, depth: int = 0):
        self.name = name
        self.work_dir = work_dir
        self.depth = depth
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
    def decompose_problem(self, problem: str, context: Optional[Context] = None, 
                         is_leaf: bool = False) -> Optional[List[Tuple[str, bool]]]:
        """Decompose a problem into subtasks with complexity labels
        
        Returns:
            None if problem should be solved directly
            List of (subtask_description, is_simple) tuples if decomposition needed
        """
        
        # Leaf nodes cannot decompose further
        if is_leaf:
            return None
            
        context_prompt = context.to_prompt() if context else ""
        
        # Build the decomposition prompt
        prompt = None
        
        # Use direct MCP client if available
        if HAS_MCP_CLIENT:
            print(f"\n{'='*80}")
            print(f"🚀 DIRECT MCP CALL - Node: {self.name} (Depth: {self.depth})")
            print(f"📍 Working Directory: {self.work_dir}")
            print(f"{'='*80}")
            print("Using direct MCP connection to Zen server...")
            
            try:
                # Get the prompt from the MCP client
                prompt_or_result = decompose_problem_sync(problem, context_prompt, is_leaf)
                
                # If it's a string, it's the prompt to use with Claude CLI
                if isinstance(prompt_or_result, str):
                    prompt = prompt_or_result
                else:
                    # Direct result from MCP (future implementation)
                    return prompt_or_result
            except Exception as e:
                logger.warning(f"Direct MCP call failed: {e}, falling back to Claude CLI")
        
        # If we don't have a prompt yet, build it
        if prompt is None:
            prompt = self._build_decomposition_prompt(problem, context_prompt)
        
        # Try Gemini Flash first for decomposition via CLI
        result = self._call_gemini_for_decomposition(prompt)

    
    def solve_simple(self, problem: str, context: Optional[Context] = None) -> str:
        """Use claude to solve a simple problem"""
        
        context_prompt = context.to_prompt() if context else ""
        
        prompt = f"""{context_prompt}Solve this problem:
{problem}

IMPORTANT: First, create a planning.md file in the current directory that documents this task:

The planning.md file should contain:
1. A # heading with the task/problem
2. A ## Solution Summary section
3. A brief description of your approach

Example planning.md content:
```
# Implement User Login Endpoint

## Solution Summary
Creating a REST endpoint that validates user credentials against the database and returns a JWT token for authenticated sessions.
```

After creating planning.md, provide a concrete solution with implementation details."""

        return self._run_claude(prompt)
    
    def integrate_solutions(self, problem: str, solutions: List[Tuple[str, str]], 
                          context: Optional[Context] = None) -> str:
        """Use claude to integrate sub-solutions"""
        
        context_prompt = context.to_prompt() if context else ""
        
        solutions_text = "\n\n".join([
            f"### {task}\nSolution: {solution}"
            for task, solution in solutions
        ])
        
        prompt = f"""{context_prompt}Original problem: {problem}

Sub-solutions:
{solutions_text}

IMPORTANT: First, update the planning.md file in the current directory:
1. Read the existing planning.md file
2. For each subtask in the decomposition plan, add a 1-3 sentence summary after the link
3. Add a ## Integration Summary section at the bottom with the overall solution approach

Example updated planning.md:
```
# Build User Authentication System

## Decomposition Plan
- [[sub1/planning|Design authentication schema and user model]] - Created User model with email/password fields and defined JWT token structure for stateless auth.
- [[sub2/planning|Implement login/logout endpoints]] - Built POST /login and POST /logout endpoints with proper validation and token management.
- [[sub3/planning|Add password reset functionality]] - Implemented secure password reset flow using temporary tokens sent via email.

## Integration Summary
The authentication system is now complete with user management, secure login/logout, and password recovery capabilities. All endpoints follow REST conventions and use JWT for session management.
```

After updating planning.md, integrate these sub-solutions into a complete solution."""

        return self._run_claude(prompt)
    
    def _build_decomposition_prompt(self, problem: str, context_prompt: str) -> str:
        """Build the decomposition prompt following the vision requirements"""
        return f"""{context_prompt}STEPS to PLAN & EXECUTE CHILDREN:

Analyze this problem and identify how it can break into sub-problems, in what order they need to run, what context they need from the parent & ancestor hierarchy, any knowledge of sibling tasks or dependencies, etc. - all context that would be useful for child claude process without bloating the context with any irrelevant information.

Problem: {problem}

IMPORTANT: Before responding with JSON, you MUST create a planning.md file in the current directory that documents your decomposition plan using Obsidian-style links.

The planning.md file should contain:
1. A # heading with the main task/problem
2. A ## Decomposition Plan section
3. For each subtask, create a line like: - [[sub1/planning|Description of subtask 1]]
   (where sub1, sub2, etc. match the subtask order in your JSON response)

Example planning.md content:
```
# Build User Authentication System

## Decomposition Plan
- [[sub1/planning|Design authentication schema and user model]]
- [[sub2/planning|Implement login/logout endpoints]]
- [[sub3/planning|Add password reset functionality]]
```

After creating planning.md, respond with JSON:

If this problem is simple enough to solve directly (single focused task, one file, etc.), respond with:
{{"decompose": false}}

If this problem needs breaking down, respond with subtasks and specify whether each subtask will be simple or complex:
{{"decompose": true, "approach": "high-level strategy", "subtasks": [
    {{"task": "specific subtask 1", "simple": true}},
    {{"task": "specific subtask 2", "simple": false}},
    ...
]}}

IMPORTANT: 
- If a subtask is "simple": true, the child process will be a LEAF NODE which cannot recurse further
- If a subtask is "simple": false, the child process can decompose further if needed
- Consider dependencies and execution order when defining subtasks
- Each subtask should have clear, focused scope

Respond with ONLY valid JSON."""
    
    def _call_gemini_for_decomposition(self, prompt: str) -> Optional[List[Tuple[str, bool]]]:
        """Call Gemini via Claude CLI for decomposition"""
        print(f"\n{'='*80}")
        print(f"🤖 GEMINI CALL (via Claude/Zen MCP) - Node: {self.name} (Depth: {self.depth})")
        print(f"📍 Working Directory: {self.work_dir}")
        print(f"{'='*80}")
        print("📝 DECOMPOSITION PROMPT:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        
        try:
            # Call the Zen MCP server using Claude CLI
            zen_prompt = f"""Use the mcp__zen__chat tool to ask Gemini 2.5 this question and return ONLY the raw JSON response from Gemini:

{prompt}

Use these parameters:
- model: "flash"
- temperature: 0.2
- thinking_mode: "low"

Return ONLY the JSON from Gemini's response, nothing else."""

            cmd = ["claude", "--dangerously-skip-permissions", "-p", zen_prompt]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.work_dir)
            )
            
            if process.returncode != 0:
                raise Exception(f"Claude CLI failed: {process.stderr}")
            
            result = process.stdout.strip()
            print("\n✅ Gemini Response (via Claude/Zen MCP):")
            print("-" * 40)
            print(result)
            print("-" * 40)
            print(f"{'='*80}\n")
            
            # Extract JSON from response
            data = self._extract_json(result)
            
            if not data.get("decompose", False):
                return None
            
            # Extract subtasks with their complexity labels
            subtasks = []
            for subtask in data.get("subtasks", []):
                task_desc = subtask["task"]
                is_simple = subtask.get("simple", True)
                subtasks.append((task_desc, is_simple))
            
            return subtasks
                
        except Exception as e:
            logger.warning(f"Failed to parse decomposition: {e}, solving directly")
            print(f"\n❌ GEMINI ERROR: {str(e)}")
            print(f"{'='*80}\n")
            return None
    
    def _call_claude_for_decomposition(self, prompt: str) -> Optional[List[Tuple[str, bool]]]:
        # TODO, REMOVE, WE SHOULD NEVER HAVE FALLBACKS ORM ULTIPLE VERSIONS
        """Fall back to Claude for decomposition when Gemini is not available"""
        logger.info("Using Claude for decomposition")
        
        # Modify prompt to ensure Claude returns valid JSON
        claude_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no other text or explanation."
        
        try:
            response = self._run_claude(claude_prompt)
            
            # Extract JSON from response
            data = self._extract_json(response)
            
            if not data.get("decompose", False):
                return None
            
            # Extract subtasks with their complexity labels
            subtasks = []
            for subtask in data.get("subtasks", []):
                task_desc = subtask["task"]
                is_simple = subtask.get("simple", True)
                subtasks.append((task_desc, is_simple))
            
            return subtasks
            
        except Exception as e:
            logger.warning(f"Failed to parse Claude decomposition: {e}")
            return None
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text that might contain markdown or other formatting"""
        # First try to extract from markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Fallback to finding raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                raise ValueError("No JSON found in response")
        
        return json.loads(json_str)
    
    def _run_claude(self, prompt: str, mode: str = "ephemeral") -> str:
        """Run claude CLI and return output"""
        
        # Use headless mode for programmatic integration
        cmd = ["claude", "--dangerously-skip-permissions", "-p", prompt]
        
        # Show full visibility of what's happening
        print(f"\n{'='*80}")
        print(f"🌳 CLAUDE CALL - Node: {self.name} (Depth: {self.depth})")
        print(f"📍 Working Directory: {self.work_dir}")
        print(f"{'='*80}")
        print("📝 INPUT PROMPT:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        
        logger.info(f"Running Claude in {self.work_dir}")
        
        print("\n🚀 Executing Claude...")
        print("⏳ Live output stream:")
        print("-" * 40)
        
        try:
            # Use Popen for streaming output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.work_dir)
            )
            
            output_lines = []
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"  {line.rstrip()}")
                    output_lines.append(line)
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode != 0:
                error_output = process.stderr.read()
                logger.error(f"Claude failed: {error_output}")
                print(f"\n❌ CLAUDE ERROR: {error_output}")
                return f"Error: {error_output}"
            
            output = ''.join(output_lines).strip()
            print("-" * 40)
            print(f"✅ Claude completed successfully")
            print(f"{'='*80}\n")
            
            return output
            
        except Exception as e:
            logger.error(f"Claude error: {e}")
            print(f"\n❌ CLAUDE EXCEPTION: {str(e)}")
            print(f"{'='*80}\n")
            
            # Try to terminate the process if it's still running
            if 'process' in locals():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            
            return f"Error: {str(e)}"