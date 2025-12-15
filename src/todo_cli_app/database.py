import json
from pathlib import Path
from typing import List
from dataclasses import asdict
from todo_cli_app.model import Todo as TodoDTO
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "todo_db.json")
DEFAULT_DB_FILE = Path(DB_PATH)

def get_todo_list(db_path: Path = DEFAULT_DB_FILE) -> List[TodoDTO]:
    """Reads the todo list from the database file."""
    if not db_path.exists():
        return []
    with db_path.open("r") as db:
        try:
            data = json.load(db)
            # Handle older data that might have 'description' instead of 'title'
            for item in data:
                if "title" not in item and "description" in item:
                    item["title"] = item.pop("description") # Move old description to title
            return [TodoDTO(**item) for item in data]
        except json.JSONDecodeError:
            return []

def save_todo_list(todo_list: List[TodoDTO], db_path: Path = DEFAULT_DB_FILE) -> None:
    """Saves the todo list to the database file."""
    with db_path.open("w") as db:
        json.dump([asdict(item) for item in todo_list], db, indent=4)