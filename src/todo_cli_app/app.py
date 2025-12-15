from pathlib import Path
from typing import List, Optional
from todo_cli_app.database import get_todo_list, save_todo_list, DEFAULT_DB_FILE
from todo_cli_app.model import Todo as TodoDTO

class Todoer:
    def __init__(self):
        self._db_path = DEFAULT_DB_FILE

    def add(self, title: str, description: Optional[str] = None, priority: Optional[str] = None, due_date: Optional[str] = None) -> TodoDTO:
        """Adds a new todo to the database."""
        todo_list = get_todo_list(self._db_path)
        new_id = self._get_next_id(todo_list)
        new_todo_dto = TodoDTO(id=new_id, title=title, description=description, priority=priority, due_date=due_date)
        todo_list.append(new_todo_dto)
        save_todo_list(todo_list, self._db_path)
        return new_todo_dto

    def list_all(self) -> List[TodoDTO]:
        """Lists all todos from the database."""
        return get_todo_list(self._db_path)

    def toggle_completion(self, todo_id: int) -> Optional[TodoDTO]:
        """Toggles the completion status of a todo."""
        todo_list = get_todo_list(self._db_path)
        for todo_dto in todo_list:
            if todo_dto.id == todo_id:
                todo_dto.completed = not todo_dto.completed # Flip the status
                save_todo_list(todo_list, self._db_path)
                return todo_dto
        return None # Todo not found

    def update_todo(self, todo_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, due_date: Optional[str] = None, completed: Optional[bool] = None) -> Optional[TodoDTO]:
        """Updates the title or description of a todo."""
        todo_list = get_todo_list(self._db_path)
        for todo_dto in todo_list:
            if todo_dto.id == todo_id:
                if title is not None:
                    todo_dto.title = title
                if description is not None:
                    todo_dto.description = description
                if priority is not None:
                    todo_dto.priority = priority
                if due_date is not None:
                    todo_dto.due_date = due_date
                if completed is not None:
                    todo_dto.completed = completed
                save_todo_list(todo_list, self._db_path)
                return todo_dto
        return None # Todo not found

    def delete_todo(self, todo_id: int) -> Optional[TodoDTO]:
        """Deletes a todo from the database."""
        todo_list = get_todo_list(self._db_path)
        initial_len = len(todo_list)
        todo_list = [todo_dto for todo_dto in todo_list if todo_dto.id != todo_id]
        if len(todo_list) < initial_len:
            save_todo_list(todo_list, self._db_path)
            return TodoDTO(id=todo_id, title="deleted", completed=False) # Placeholder for deleted todo
        return None # Todo not found

    def search_todos(self, query: str, by_title: bool = True, by_description: bool = False) -> List[TodoDTO]:
        """Searches for todos matching a query in title and/or description."""
        todos = self.list_all() # Get all and filter in memory for now
        query_lower = query.lower()
        results = []
        for todo_dto in todos:
            match = False
            if by_title and todo_dto.title and query_lower in todo_dto.title.lower():
                match = True
            if not match and by_description and todo_dto.description and query_lower in todo_dto.description.lower():
                match = True
            if match:
                results.append(todo_dto)
        return results

    def filter_todos(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[TodoDTO]:
        """Filters todos by status and/or priority."""
        todos = self.list_all() # Get all and filter in memory for now
        filtered_todos = []
        for todo_dto in todos:
            status_match = True
            if status is not None:
                expected_status = True if status.lower() == "done" else False
                status_match = (todo_dto.completed == expected_status)
            
            priority_match = True
            if priority is not None:
                priority_match = (todo_dto.priority and todo_dto.priority.lower() == priority.lower())
            
            if status_match and priority_match:
                filtered_todos.append(todo_dto)
        return filtered_todos

    def sort_todos(self, todos: List[TodoDTO], sort_by: str = "id", reverse: bool = False) -> List[TodoDTO]:
        """Sorts a list of todos based on specified criteria."""
        if not todos:
            return []

        # Define a key function based on the sort_by field
        def get_sort_key(todo: TodoDTO):
            field = getattr(todo, sort_by, None)
            if field is None:
                return float('inf') # Send None values to the end for consistent sorting
            if isinstance(field, str):
                return field.lower() # Case-insensitive sort for strings
            return field

        return sorted(todos, key=get_sort_key, reverse=reverse)

    def _get_next_id(self, todo_list: List[TodoDTO]) -> int:
        """Returns the next available ID."""
        if not todo_list:
            return 1
        return max(todo_dto.id for todo_dto in todo_list) + 1

    def export_to_csv(self, filename: str) -> None:
        """Exports the todo list to a CSV file."""
        import csv
        todos = self.list_all()
        if not todos:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["id", "title", "description", "priority", "due_date", "completed"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for todo in todos:
                writer.writerow({
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "priority": todo.priority,
                    "due_date": todo.due_date,
                    "completed": todo.completed,
                })

    def import_from_csv(self, filename: str) -> None:
        """Imports the todo list from a CSV file."""
        import csv
        
        todo_list = get_todo_list(self._db_path)
        max_id = self._get_next_id(todo_list) -1

        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Ensure the imported todo has a unique id
                max_id += 1
                new_todo = TodoDTO(
                    id=max_id,
                    title=row["title"],
                    description=row["description"],
                    priority=row["priority"],
                    due_date=row["due_date"],
                    completed=row["completed"].lower() == "true",
                )
                todo_list.append(new_todo)
        
        save_todo_list(todo_list, self._db_path)