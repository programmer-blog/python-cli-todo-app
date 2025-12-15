import pytest
import json
from typer.testing import CliRunner
from todo_cli_app.main import app, todoer
from todo_cli_app.database import DEFAULT_DB_FILE # Import the default JSON DB file path

runner = CliRunner()

@pytest.fixture
def temp_db(tmp_path):
    """Fixture to create a temporary JSON database file for testing."""
    test_db_path = tmp_path / DEFAULT_DB_FILE.name # Use the default name but in tmp_path
    todoer._db_path = test_db_path # Override the db_path in the todoer instance

    # Ensure the file exists (empty list) for get_todo_list to not fail
    with test_db_path.open("w") as f:
        json.dump([], f)

    yield test_db_path # Yield the path to the temporary JSON file
    
    # Teardown: delete the temporary file
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Restore original db_path to avoid interference with other potential tests
    todoer._db_path = DEFAULT_DB_FILE


def test_add(temp_db):
    """Tests the 'add' command with title and optional fields."""
    # Test adding with only title
    result = runner.invoke(app, ["add", "Test title 1"])
    assert result.exit_code == 0
    assert "Added todo: 'Test title 1' (ID: 1)" in result.stdout

    # Verify in the database
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert len(data) == 1
        assert data[0]["title"] == "Test title 1"
        assert data[0]["description"] is None
        assert data[0]["priority"] is None
        assert data[0]["due_date"] is None
        assert data[0]["completed"] is False
        assert data[0]["id"] == 1
    
    # Test adding with all optional fields
    result = runner.invoke(app, ["add", "Test title 2", "--description", "A detailed description", "--priority", "High", "--due-date", "2025-12-31"])
    assert result.exit_code == 0
    assert "Added todo: 'Test title 2' (ID: 2)" in result.stdout

    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert len(data) == 2
        assert data[1]["title"] == "Test title 2"
        assert data[1]["description"] == "A detailed description"
        assert data[1]["priority"] == "High"
        assert data[1]["due_date"] == "2025-12-31"
        assert data[1]["completed"] is False
        assert data[1]["id"] == 2


def test_list(temp_db):
    """Tests the 'list' command with filtering."""
    # Add some todos first
    runner.invoke(app, ["add", "Task A", "--priority", "high"])
    runner.invoke(app, ["add", "Task B", "--priority", "medium"])
    runner.invoke(app, ["add", "Task C", "--priority", "low"])
    runner.invoke(app, ["add", "Task D", "--priority", "high"])
    runner.invoke(app, ["toggle", "1"])

    # List all
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "[1] Task A [Done]" in result.stdout
    assert "[2] Task B [Not Done]" in result.stdout
    assert "[3] Task C [Not Done]" in result.stdout
    assert "[4] Task D [Not Done]" in result.stdout

    # Filter by status: Done
    result = runner.invoke(app, ["list", "--status", "done"])
    assert result.exit_code == 0
    assert "[1] Task A [Done]" in result.stdout
    assert "Task B" not in result.stdout

    # Filter by status: Not Done
    result = runner.invoke(app, ["list", "--status", "not done"])
    assert result.exit_code == 0
    assert "Task A" not in result.stdout
    assert "[2] Task B [Not Done]" in result.stdout
    assert "[3] Task C [Not Done]" in result.stdout
    assert "[4] Task D [Not Done]" in result.stdout

    # Filter by priority: High
    result = runner.invoke(app, ["list", "--priority", "high"])
    assert result.exit_code == 0
    assert "[1] Task A [Done]" in result.stdout
    assert "[4] Task D [Not Done]" in result.stdout
    assert "Task B" not in result.stdout

    # Filter by status and priority
    result = runner.invoke(app, ["list", "--status", "not done", "--priority", "medium"])
    assert result.exit_code == 0
    assert "Task A" not in result.stdout
    assert "[2] Task B [Not Done]" in result.stdout
    assert "Task C" not in result.stdout
    assert "Task D" not in result.stdout

    # No items found
    result = runner.invoke(app, ["list", "--status", "done", "--priority", "low"])
    assert result.exit_code == 0
    assert "No todo items found matching your criteria yet." in result.stdout


def test_toggle_completion_status(temp_db):
    """Tests the 'toggle' command."""
    # Add a todo, initially Not Done
    runner.invoke(app, ["add", "Task to toggle"])

    # Toggle to Done
    result = runner.invoke(app, ["toggle", "1"])
    assert result.exit_code == 0
    assert "Todo 'Task to toggle' (ID: 1) marked as Done." in result.stdout
    
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert data[0]["completed"] is True

    # Toggle back to Not Done
    result = runner.invoke(app, ["toggle", "1"])
    assert result.exit_code == 0
    assert "Todo 'Task to toggle' (ID: 1) marked as Not Done." in result.stdout
    
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert data[0]["completed"] is False

    # Test toggling a non-existent todo
    result = runner.invoke(app, ["toggle", "99"])
    assert result.exit_code == 0
    assert "Error: Todo with ID 99 not found." in result.stdout


def test_update(temp_db):
    """Tests the 'update' command."""
    # Add a todo first
    runner.invoke(app, ["add", "Initial Title", "--description", "Initial Description", "--priority", "low", "--due-date", "2024-01-01"])

    # Scenario 1: Update title, description, priority, due_date, completed
    result = runner.invoke(app, ["update", "1", "--title", "New Title", "--description", "New Desc", "--priority", "high", "--due-date", "2025-12-31", "--completed"])
    assert result.exit_code == 0
    assert "Todo ID 1 updated." in result.stdout
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert data[0]["title"] == "New Title"
        assert data[0]["description"] == "New Desc"
        assert data[0]["priority"] == "high"
        assert data[0]["due_date"] == "2025-12-31"
        assert data[0]["completed"] is True

    # Scenario 2: Update only title
    result = runner.invoke(app, ["update", "1", "--title", "Title Only Update"])
    assert result.exit_code == 0
    assert "Todo ID 1 updated." in result.stdout
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert data[0]["title"] == "Title Only Update"
        assert data[0]["description"] == "New Desc" # Should remain unchanged
        assert data[0]["priority"] == "high" # Should remain unchanged
        assert data[0]["due_date"] == "2025-12-31" # Should remain unchanged
        assert data[0]["completed"] is True # Should remain unchanged

    # Scenario 3: Update only completion status
    result = runner.invoke(app, ["update", "1", "--no-completed"])
    assert result.exit_code == 0
    assert "Todo ID 1 updated." in result.stdout
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert data[0]["completed"] is False # Should be false now

    # Test updating a non-existent todo
    result = runner.invoke(app, ["update", "99", "--title", "Non Existent"])
    assert result.exit_code == 0
    assert "Error: Failed to update todo with ID 99." in result.stdout


def test_delete(temp_db):
    """Tests the 'delete' command."""
    # Add a few todos
    runner.invoke(app, ["add", "Task 1 Title"])
    runner.invoke(app, ["add", "Task 2 Title"])
    runner.invoke(app, ["add", "Task 3 Title"])

    # Delete Task 2 using --force flag
    result = runner.invoke(app, ["delete", "2", "--force"])
    assert result.exit_code == 0
    assert "Todo ID 2 deleted." in result.stdout

    # Verify in the database
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 3
        assert not any(todo["id"] == 2 for todo in data)

    # Test deleting a non-existent todo
    result = runner.invoke(app, ["delete", "99", "--force"]) # Also use --force here
    assert result.exit_code == 0
    assert "Error: Todo with ID 99 not found." in result.stdout

def test_search(temp_db):
    """Tests the 'search' command."""
    # Add some todos
    runner.invoke(app, ["add", "Buy groceries", "--description", "Milk, Eggs, Bread"])
    runner.invoke(app, ["add", "Clean apartment", "--description", "Vacuum, Dusting"])
    runner.invoke(app, ["add", "Read book about Python"])

    # Search by title (default)
    result = runner.invoke(app, ["search", "buy"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'buy':" in result.stdout
    assert "[1] Buy groceries [Not Done]" in result.stdout
    assert "Clean apartment" not in result.stdout

    # Search by description
    result = runner.invoke(app, ["search", "dusting", "--description"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'dusting':" in result.stdout
    assert "[2] Clean apartment [Not Done]" in result.stdout
    assert "Buy groceries" not in result.stdout # Ensure it's not searching title here

    # Search by both title and description
    result = runner.invoke(app, ["search", "python", "--title", "--description"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'python':" in result.stdout
    assert "[3] Read book about Python [Not Done]" in result.stdout

    # Search with no results
    result = runner.invoke(app, ["search", "nonexistent"])
    assert result.exit_code == 0
    assert "No todo items found matching 'nonexistent'." in result.stdout

    # Search for a term that appears in both title and description for a single todo
    runner.invoke(app, ["add", "Project X docs", "--description", "Review Project X requirements"])
    result = runner.invoke(app, ["search", "Project X", "--title", "--description"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'Project X':" in result.stdout
    assert "[4] Project X docs [Not Done]" in result.stdout
    
    # Search only by title when description also matches (and only description specified)
    result = runner.invoke(app, ["search", "Project X", "--title"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'Project X':" in result.stdout
    assert "[4] Project X docs [Not Done]" in result.stdout
    
    # Search only by description when title also matches (and only description specified)
    result = runner.invoke(app, ["search", "Project X", "--description"])
    assert result.exit_code == 0
    assert "Found 1 todo item(s) matching 'Project X':" in result.stdout
    assert "[4] Project X docs [Not Done]" in result.stdout

def test_export(temp_db, tmp_path):
    """Tests the 'export' command."""
    # Test exporting with no todos
    export_file = tmp_path / "export.csv"
    result = runner.invoke(app, ["export", str(export_file)])
    assert result.exit_code == 0
    assert "No tasks to export." == result.stdout

    # Add a todo first
    runner.invoke(app, ["add", "Test Export", "--description", "Test Description", "--priority", "high", "--due-date", "2025-01-01"])
    runner.invoke(app, ["toggle", "1"]) # Mark as completed

    # Export to a temporary file
    result = runner.invoke(app, ["export", str(export_file)])
    assert result.exit_code == 0
    assert f"Successfully exported 1 todo(s) to {export_file}" == result.stdout

    # Verify the content of the CSV file
    with open(export_file, "r") as f:
        content = f.read()
        assert "id,title,description,priority,due_date,completed" in content
        assert "1,Test Export,Test Description,high,2025-01-01,True" in content

def test_import(temp_db, tmp_path):
    """Tests the 'import' command."""
    # Create a temporary CSV file with some todos
    import_file = tmp_path / "import.csv"
    with open(import_file, "w") as f:
        f.write("id,title,description,priority,due_date,completed\n")
        f.write("10,Imported Task,Imported Description,medium,2025-12-31,False\n")
        f.write("11,Another Imported Task,,low,2026-01-01,True\n")

    # Import from the temporary file
    result = runner.invoke(app, ["import", str(import_file)])
    assert result.exit_code == 0
    assert f"Successfully imported 2 todo(s) from {import_file}" == result.stdout

    # Verify the content of the database
    with temp_db.open("r") as db_file:
        data = json.load(db_file)
        assert len(data) == 2
        assert data[0]["title"] == "Imported Task"
        assert data[0]["id"] == 1 # Check that the id is re-assigned
        assert data[1]["title"] == "Another Imported Task"
        assert data[1]["id"] == 2 # Check that the id is re-assigned
        assert data[1]["completed"] is True
