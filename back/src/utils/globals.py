from typing import Dict, Any

class GlobalState:
    def __init__(self):
        self.active_tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_id: str):
        self.active_tasks[task_id] = {'uids': set()}

globals = GlobalState()
