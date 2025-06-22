"""
Context management for agent tree nodes
"""

from typing import List


class Context:
    """Context passed down the tree"""

    def __init__(
        self,
        root_problem: str,
        parent_task: str = "",
        parent_approach: str = "",
        sibling_tasks: List[str] = None,
    ):
        self.root_problem = root_problem
        self.parent_task = parent_task
        self.parent_approach = parent_approach
        self.sibling_tasks = sibling_tasks or []

    def to_prompt(self) -> str:
        """Convert to prompt text"""
        if not self.parent_task:
            return ""

        siblings = "\n".join(f"  - {task}" for task in self.sibling_tasks)
        return f"""=== CONTEXT FROM ANCESTORS ===
Root Goal: {self.root_problem}
Parent Task: {self.parent_task}
Parent's Approach: {self.parent_approach}
Sibling Tasks:
{siblings}
===========================

"""
