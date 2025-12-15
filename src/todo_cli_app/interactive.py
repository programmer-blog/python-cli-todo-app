from rich.console import Console
from rich.prompt import Prompt, Confirm
import typer
from todo_cli_app.app import Todoer

console = Console()
todoer = Todoer()

def _interactive_add():
    console.print("\n[bold cyan]--- Add New Todo ---[/bold cyan]")
    title = Prompt.ask("[yellow]Enter task title[/yellow]")
    if not title:
        console.print("[red]Title cannot be empty. Aborting add operation.[/red]")
        return
    
    description = Prompt.ask("[yellow]Enter short description (optional)[/yellow]", default="")
    priority = Prompt.ask("[yellow]Enter priority (Low/Medium/High, optional)[/yellow]", choices=["low", "medium", "high", ""], default="").lower()
    due_date = Prompt.ask("[yellow]Enter due date (YYYY-MM-DD, optional)[/yellow]", default="")

    todo = todoer.add(
        title=title,
        description=description if description else None,
        priority=priority if priority else None,
        due_date=due_date if due_date else None
    )
    console.print(f"[green]Added todo: '{todo.title}' (ID: {todo.id})[/green]")

def _interactive_list():
    console.print("\n[bold cyan]--- List Todos ---[/bold cyan]")
    filter_status = Prompt.ask("[yellow]Filter by status (Done/Not Done, leave blank for all)[/yellow]", choices=["done", "not done", ""], default="").lower()
    filter_priority = Prompt.ask("[yellow]Filter by priority (Low/Medium/High, leave blank for all)[/yellow]", choices=["low", "medium", "high", ""], default="").lower()

    todos = todoer.filter_todos(
        status=filter_status if filter_status else None,
        priority=filter_priority if filter_priority else None
    )

    if not todos:
        console.print("[yellow]No todo items found matching your criteria.[/yellow]")
        return

    for todo in todos:
        status_text = "Done" if todo.completed else "Not Done"
        console.print(f"[{todo.id}] {todo.title} [{status_text}]")

def _interactive_toggle():
    console.print("\n[bold cyan]--- Toggle Todo Status ---[/bold cyan]")
    todo_id_str = Prompt.ask("[yellow]Enter ID of todo to toggle[/yellow]")
    try:
        todo_id = int(todo_id_str)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return
    
    todo = todoer.toggle_completion(todo_id)
    if todo:
        status_text = "Done" if todo.completed else "Not Done"
        console.print(f"[green]Todo '{todo.title}' (ID: {todo.id}) marked as {status_text}.[/green]")
    else:
        console.print(f"[red]Error: Todo with ID {todo_id} not found.[/red]")

def _interactive_update():
    console.print("\n[bold cyan]--- Update Todo ---[/bold cyan]")
    todo_id_str = Prompt.ask("[yellow]Enter ID of todo to update[/yellow]")
    try:
        todo_id = int(todo_id_str)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return
    
    todo_to_update = next((t for t in todoer.list_all() if t.id == todo_id), None)

    if not todo_to_update:
        console.print(f"[red]Error: Todo with ID {todo_id} not found.[/red]")
        return

    console.print(f"Current Title: [cyan]{todo_to_update.title}[/cyan]")
    new_title = Prompt.ask("Enter new title (leave blank to keep current)")
    
    console.print(f"Current Description: [cyan]{todo_to_update.description or '[None]'}[/cyan]")
    new_description = Prompt.ask("Enter new description (leave blank to keep current)")

    console.print(f"Current Priority: [cyan]{todo_to_update.priority or '[None]'}[/cyan]")
    new_priority = Prompt.ask("Enter new priority (leave blank to keep current)", choices=["low", "medium", "high", ""])

    console.print(f"Current Due Date: [cyan]{todo_to_update.due_date or '[None]'}[/cyan]")
    new_due_date = Prompt.ask("Enter new due date (YYYY-MM-DD, leave blank to keep current)")

    current_status = "Done" if todo_to_update.completed else "Not Done"
    console.print(f"Current Status: [cyan]{current_status}[/cyan]")
    new_completed_str = Prompt.ask("Mark as completed? (y/n, leave blank to keep current)", choices=["y", "n", ""])
    new_completed = None
    if new_completed_str == 'y':
        new_completed = True
    elif new_completed_str == 'n':
        new_completed = False


    updated_todo = todoer.update_todo(
        todo_id,
        title=new_title if new_title else None,
        description=new_description if new_description else None,
        priority=new_priority if new_priority else None,
        due_date=new_due_date if new_due_date else None,
        completed=new_completed
    )

    if updated_todo:
        console.print(f"[green]Todo ID {todo_id} updated.[/green]")
    else:
        console.print(f"[red]Error: Failed to update todo with ID {todo_id}.[/red]")

def _interactive_delete():
    console.print("\n[bold cyan]--- Delete Todo ---[/bold cyan]")
    todo_id_str = Prompt.ask("[yellow]Enter ID of todo to delete[/yellow]")
    try:
        todo_id = int(todo_id_str)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a number.[/red]")
        return
    
    confirm = Confirm.ask(f"[red]Are you sure you want to delete todo with ID {todo_id}?[/red]", default=False)
    if not confirm:
        console.print("[yellow]Deletion aborted.[/yellow]")
        return

    todo = todoer.delete_todo(todo_id)
    if todo:
        console.print(f"[green]Todo ID {todo_id} deleted.[/green]")
    else:
        console.print(f"[red]Error: Todo with ID {todo_id} not found.[/red]")

def _interactive_search():
    console.print("\n[bold cyan]--- Search Todos ---[/bold cyan]")
    query = Prompt.ask("[yellow]Enter search query[/yellow]")
    if not query:
        console.print("[red]Search query cannot be empty. Aborting search.[/red]")
        return
    
    search_by_title_str = Prompt.ask("[yellow]Search by title? (y/n)[/yellow]", choices=["y", "n"], default="y").lower()
    search_by_title = True if search_by_title_str == "y" else False
    
    search_by_description_str = Prompt.ask("[yellow]Search by description? (y/n)[/yellow]", choices=["y", "n"], default="n").lower()
    search_by_description = True if search_by_description_str == "y" else False

    if not search_by_title and not search_by_description:
        console.print("[red]You must select at least one field to search by. Defaulting to title search.[/red]")
        search_by_title = True
    
    results = todoer.search_todos(query, by_title=search_by_title, by_description=search_by_description)

    if not results:
        console.print(f"[yellow]No todo items found matching '{query}'.[/yellow]")
        return

    console.print(f"[green]Found {len(results)} todo item(s) matching '{query}':[/green]")
    for todo in results:
        status = "Done" if todo.completed else "Not Done"
        console.print(f"[{todo.id}] {todo.title} [{status}]")

def interactive_mode():
    console.print("\n[bold green]Welcome to the Interactive Todo CLI![/bold green]")
    while True:
        console.print("\n[bold yellow]Available Commands:[/bold yellow]")
        console.print("  1. [cyan]Add[/cyan] new todo")
        console.print("  2. [cyan]List[/cyan] all todos (with filter options)")
        console.print("  3. [cyan]Toggle[/cyan] todo status (Done/Not Done)")
        console.print("  4. [cyan]Update[/cyan] todo")
        console.print("  5. [cyan]Delete[/cyan] todo")
        console.print("  6. [cyan]Search[/cyan] todos")
        console.print("  7. [red]Exit[/red]")

        choice = Prompt.ask("[blue]Choose an option[/blue]", choices=["1", "2", "3", "4", "5", "6", "7"])

        if choice == "1":
            _interactive_add()
        elif choice == "2":
            _interactive_list()
        elif choice == "3":
            _interactive_toggle()
        elif choice == "4":
            _interactive_update()
        elif choice == "5":
            _interactive_delete()
        elif choice == "6":
            _interactive_search()
        elif choice == "7":
            console.print("[bold green]Exiting Todo CLI. Goodbye![/bold green]")
            raise typer.Exit()
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
