#!/usr/bin/env python3
"""
Demo: Direct MCP usage from within Claude

This script demonstrates how to use Zen MCP tools directly when running
inside Claude, avoiding the overhead of calling Claude CLI.
"""

import json
import re
from typing import Dict, Any, Tuple, List, Optional


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
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response_text}")
        return {"error": "Failed to parse JSON", "response": response_text}


async def call_gemini_via_mcp(prompt: str) -> str:
    """
    This function is meant to be called by Claude directly.
    Claude will use the mcp__zen__chat tool when it executes this.
    """
    # When Claude runs this, it should replace this comment with an actual
    # mcp__zen__chat tool call
    print("📞 Calling Gemini via MCP...")
    print(f"Prompt: {prompt[:100]}...")
    
    # CLAUDE: Please use mcp__zen__chat here with:
    # - model: "flash"
    # - prompt: the prompt variable
    # - temperature: 0.2
    # - thinking_mode: "low"
    # And return the response
    
    return "PLACEHOLDER - Claude should call mcp__zen__chat here"


def assess_complexity_with_mcp(problem: str, context: str = "") -> Tuple[str, Optional[List[str]], str]:
    """
    Assess complexity using direct MCP call (to be executed by Claude)
    """
    prompt = f"""{context}Assess if this problem requires breaking down into subtasks.

Problem: {problem}

A problem is SIMPLE if it's a single, focused task like "fix a bug in one file" or "write a single function".
A problem is COMPLEX if it requires multiple steps, affects multiple files, or needs coordination.

Respond with ONLY valid JSON:
If simple: {{"complexity": "simple", "approach": "direct solution approach"}}
If complex: {{"complexity": "complex", "approach": "high-level strategy", "subtasks": ["specific subtask 1", "specific subtask 2", ...]}}"""
    
    print("\n" + "="*80)
    print("🚀 DIRECT MCP COMPLEXITY ASSESSMENT")
    print("="*80)
    
    # This will be replaced by Claude with actual MCP call
    # For now, return a placeholder
    print("⚠️  This demo requires Claude to execute the MCP call")
    print("When run by Claude, it will call mcp__zen__chat directly")
    
    return "simple", None, "Direct solution (demo mode)"


if __name__ == "__main__":
    # Demo the complexity assessment
    test_problem = "Build a web application with user authentication, database, and REST API"
    
    print("Direct MCP Demo")
    print("="*80)
    print(f"Problem: {test_problem}")
    print("")
    
    complexity, subtasks, approach = assess_complexity_with_mcp(test_problem)
    
    print(f"\nResults (Demo Mode):")
    print(f"- Complexity: {complexity}")
    print(f"- Approach: {approach}")
    if subtasks:
        print(f"- Subtasks: {subtasks}")
    
    print("\n📌 Note: To see this working with real MCP calls, this script")
    print("    needs to be executed by Claude with Zen MCP tools available.")