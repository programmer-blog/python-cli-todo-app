from dataclasses import dataclass
from typing import Optional

@dataclass
class Todo:
    title: str
    id: int
    completed: bool = False
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
