"""
Claude CLI client for running prompts
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Handles interaction with Claude CLI"""
    
    def __init__(self, work_dir: Path, node_name: str = "unknown", depth: int = 0):
        self.work_dir = work_dir
        self.node_name = node_name
        self.depth = depth
    
    def run_prompt(self, prompt: str, mode: str = "ephemeral") -> str:
        """Run claude CLI and return output"""
        
        # Use headless mode for programmatic integration
        cmd = ["claude", "--dangerously-skip-permissions", "-p", prompt]
        
        # Show full visibility of what's happening
        print(f"\n{'='*80}")
        print(f"🌳 CLAUDE CALL - Node: {self.node_name} (Depth: {self.depth})")
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