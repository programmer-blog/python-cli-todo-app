import typer
from rich.console import Console
from typing import Optional
from todo_cli_app.app import Todoer
from todo_cli_app.interactive import interactive_mode

app = typer.Typer()
todoer = Todoer()
console = Console()

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the todo item."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Short description of the todo item."),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Priority of the todo item (Low, Medium, High).", rich_help_panel="Customization and Utils"),
    due_date: Optional[str] = typer.Option(None, "--due-date", "-D", help="Due date of the todo item (YYYY-MM-DD).", rich_help_panel="Customization and Utils"),
):
    """Adds a new todo item."""
    todo = todoer.add(title=title, description=description, priority=priority, due_date=due_date)
    console.print(f"[green]Added todo: '{todo.title}' (ID: {todo.id})[/green]")

@app.command(name="list")
def list_todos(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (done/not done).", rich_help_panel="Filtering and Sorting"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Filter by priority (low/medium/high).", rich_help_panel="Filtering and Sorting"),
):
    """Lists all todo items, with optional filtering."""
    todos = todoer.filter_todos(status=status, priority=priority)

    if not todos:
        console.print("[yellow]No todo items found matching your criteria yet.[/yellow]")
        return

    for todo in todos:
        status_text = "Done" if todo.completed else "Not Done"
        console.print(f"[{todo.id}] {todo.title} [{status_text}]")

@app.command()
def toggle(
    todo_id: int = typer.Argument(..., help="ID of the todo item to toggle."),
):
    """Toggles the completion status of a todo item."""
    todo = todoer.toggle_completion(todo_id)
    if todo:
        status_text = "Done" if todo.completed else "Not Done"
        console.print(f"[green]Todo '{todo.title}' (ID: {todo.id}) marked as {status_text}.[/green]")
    else:
        console.print(f"[red]Error: Todo with ID {todo_id} not found.[/red]")

@app.command()
def update(
    todo_id: int = typer.Argument(..., help="ID of the todo item to update."),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title for the todo item."),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description for the todo item."),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="New priority for the todo item (Low, Medium, High).", rich_help_panel="Customization and Actuals"),
    due_date: Optional[str] = typer.Option(None, "--due-date", "-D", help="New due date for the todo item (YYYY-MM-DD).", rich_help_panel="Customization and Actuals"),
    completed: Optional[bool] = typer.Option(None, "--completed/--no-completed", help="Set completion status (true/false).", rich_help_panel="Customization and Actuals"),
):
    """Updates an existing todo item."""
    updated_todo = todoer.update_todo(
        todo_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        completed=completed
    )
    if updated_todo:
        console.print(f"[green]Todo ID {todo_id} updated.[/green]")
    else:
        console.print(f"[red]Error: Failed to update todo with ID {todo_id}.[/red]")

@app.command()
def delete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to delete."),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation."),
):
    """Deletes a todo item."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete todo with ID {todo_id}?")
        if not confirm:
            typer.echo("[yellow]Deletion aborted.[/yellow]")
            raise typer.Exit()
    
    todo = todoer.delete_todo(todo_id)
    if todo:
        console.print(f"[green]Todo ID {todo_id} deleted.[/green]")
    else:
        console.print(f"[red]Error: Todo with ID {todo_id} not found.[/red]")

@app.command()
def search(
    query: str = typer.Argument(..., help="The search query."),
    title: bool = typer.Option(False, "--title", "-t", help="Search by title."),
    description: bool = typer.Option(False, "--description", "-d", help="Search by description."),
):
    """Searches for todo items by title and/or description."""
    if not title and not description:
        title = True

    results = todoer.search_todos(query, by_title=title, by_description=description)

    if not results:
        console.print(f"[yellow]No todo items found matching '{query}'.[/yellow]")
        return

    console.print(f"[green]Found {len(results)} todo item(s) matching '{query}':[/green]")
    for todo in results:
        status = "Done" if todo.completed else "Not Done"
        console.print(f"[{todo.id}] {todo.title} [{status}]")

@app.command(name="import")
def import_csv(
    filename: str = typer.Argument(..., help="The name of the CSV file to import from."),
):
    """Imports the todo list from a CSV file."""
    count = todoer.import_from_csv(filename)
    typer.echo(f"Successfully imported {count} todo(s) from {filename}", nl=False)

@app.command()
def export(
    filename: str = typer.Argument(..., help="The name of the CSV file to export to."),
):
    """Exports the todo list to a CSV file."""
    count = todoer.export_to_csv(filename)
    if count == 0:
        typer.echo("No tasks to export.", nl=False)
    else:
        typer.echo(f"Successfully exported {count} todo(s) to {filename}", nl=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        try:
            interactive_mode()
        except typer.Exit:
            pass
    else:
        app()
