# Python CLI Todo App

A simple, yet powerful, command-line todo application built with Python and Typer.

This project was built and refactored with the assistance of the Gemini CLI. It serves as a demonstration of a well-structured CLI application with a clean separation of concerns.

## Features

*   **Add, List, Update, Delete Todos**: All the basic CRUD operations for managing your tasks.
*   **Interactive Mode**: Run the app without any commands (`todo`) to enter a user-friendly interactive menu.
*   **Toggle Task Status**: Easily mark tasks as "Done" or "Not Done".
*   **Search**: Find tasks with a specific query in the title or description.
*   **Filter**: Filter tasks by their status (done/not done) or priority (low/medium/high).
*   **Export and import todos to/from a CSV file.**
*   **Colorful Output**: Uses the `rich` library for a better user experience with colorful and well-formatted text.
*   **Configuration via `.env`**: The database file path is configured through a `.env` file for better security and flexibility.

## Requirements

- Python 3.7+

## Setup

1.  Clone the repository.
2.  Create a `.env` file in the root of the project with the following content:
    ```
    DB_PATH="todo_db.json"
    ```
3.  It is recommended to create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
4.  Install the project in editable mode, along with the development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## Usage

The most reliable way to run the application is by using Python's module flag `-m`. This avoids potential issues with your system's PATH environment variable.

### Interactive Mode

To run the application in interactive mode, simply run the module without any arguments:

```bash
python -m todo_cli_app.main
```

This will launch a menu-driven interface to manage your todos.

### Command-Line Interface

You can also use the app with commands and arguments directly from the command line.

**Add a new todo:**
```bash
python -m todo_cli_app.main add "My new task" --priority high
```

**List all todos:**
```bash
python -m todo_cli_app.main list
```

**Filter todos by status:**
```bash
python -m todo_cli_app.main list --status done
```

**Toggle a todo's status:**
```bash
python -m todo_cli_app.main toggle 1
```

**Search for a todo:**
```bash
python -m todo_cli_app.main search "My new task"
```

**Export todos to a CSV file:**
```bash
python -m todo_cli_app.main export my_tasks.csv
```

**Import todos from a CSV file:**
```bash
python -m todo_cli_app.main import my_tasks.csv
```

For more commands and options, you can use the `--help` flag:
```bash
python -m todo_cli_app.main --help
```

## Project Structure

The project is organized into several files, each with a specific responsibility:

*   `src/todo_cli_app/main.py`: This is the entry point for the CLI application. It uses `Typer` to define the commands and arguments. It is responsible for handling the command-line interaction.

*   `src/todo_cli_app/app.py`: This file contains the core application logic (the "business logic"). The `Todoer` class in this file has all the methods to manage the todos (add, delete, update, etc.). It doesn't know about the CLI or the database format.

*   `src/todo_cli_app/database.py`: This file handles the data persistence. It is responsible for reading from and writing to the JSON database file. It also loads the database path from the `.env` file.

*   `src/todo_cli_app/interactive.py`: This file contains the logic for the interactive mode. It's responsible for displaying the menu, prompting the user for input, and calling the appropriate functions from `app.py`.

*   `src/todo_cli_app/model.py`: This file defines the `Todo` data model using a `dataclass`.

## How Gemini CLI Was Used

Gemini CLI was used as a development assistant throughout the creation of this project. Its contributions include:

*   **Initial Scaffolding**: Setting up the initial project structure.
*   **Feature Implementation**: Adding new features like searching, filtering, and the interactive mode.
*   **Refactoring**: A major refactoring was performed to separate the concerns of the application into different files (`main.py`, `app.py`, `database.py`, `interactive.py`), which significantly improved the codebase's modularity and maintainability.
*   **Bug Fixing**: Identifying and fixing bugs, such as the `ModuleNotFoundError` for the `dotenv` package.
*   **Dependency Management**: Adding dependencies to `pyproject.toml` and ensuring the project is installed correctly.
*   **Documentation**: Generating and updating this `README.md` file.
