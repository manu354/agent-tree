#!/usr/bin/env python3
"""
Direct MCP Client wrapper for calling Zen MCP server

This module provides a simple wrapper that uses the mcp__zen__chat tool
directly when available, avoiding the overhead of calling through Claude CLI.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """Extract JSON from a response that might contain markdown or other text"""
    try:
        # First try to extract from markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if code_block_match:
            return json.loads(code_block_match.group(1))
        
        # Fallback to finding raw JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # If no JSON found, return the text as-is
        return {"response": response_text}
    except json.JSONDecodeError:
        return {"response": response_text}


def call_gemini_direct(prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Call Gemini Flash directly if MCP tools are available
    
    This function is meant to be called from within Claude when Zen MCP
    tools are available. It returns a dict for compatibility.
    """
    # This function will be called from agent_tree_simple.py
    # The actual MCP call will happen there using the mcp__zen__chat tool
    return {
        "prompt": prompt,
        "model": "flash",
        "temperature": temperature,
        "thinking_mode": "low"
    }


def decompose_problem_sync(problem: str, context_prompt: str = "", is_leaf: bool = False) -> Optional[List[Tuple[str, bool]]]:
    """
    Decompose problem into subtasks with complexity labels
    
    This is a placeholder that returns the prompt structure.
    The actual MCP call should be made by the caller.
    
    Returns:
        None if problem should be solved directly
        List of (subtask_description, is_simple) tuples if decomposition needed
    """
    if is_leaf:
        return None
        
    prompt = f"""{context_prompt}STEPS to PLAN & EXECUTE CHILDREN:

Analyze this problem and identify how it can break into sub-problems, in what order they need to run, what context they need from the parent & ancestor hierarchy, any knowledge of sibling tasks or dependencies, etc. - all context that would be useful for child claude process without bloating the context with any irrelevant information.

Problem: {problem}

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
    
    # Return the prompt for the caller to use
    return prompt


# For testing outside of Claude
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py 'Your prompt here'")
        print("")
        print("Note: This module is designed to be used from within Claude")
        print("with Zen MCP tools available. When run standalone, it only")
        print("shows the prompt structure.")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    print("MCP Client Test Mode")
    print("=" * 80)
    print("Prompt structure for Gemini Flash:")
    print(json.dumps(call_gemini_direct(prompt), indent=2))
    print("")
    print("To actually call Gemini, this needs to be run from within")
    print("Claude with Zen MCP server connected.")