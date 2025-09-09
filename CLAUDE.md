# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

This project uses **Task** (not Make) for build automation. All commands are defined in `Taskfile.yaml`:

- `task check` - Run all quality checks (lint, format, type-check, test)
- `task lint` - Run ruff linting 
- `task format` - Auto-format code with ruff
- `task type-check` - Run mypy type checking
- `task test` - Run pytest unit tests
- `task test:integration` - Run integration tests (requires CMEM instance)
- `task build` - Build wheel package with poetry
- `task install` - Install package in development mode
- `task pre-commit` - Install pre-commit hooks

## Architecture Overview

### Core Components

**cmem_plugin_loopwf/task.py** - Main plugin implementation:
- `StartWorkflow` class extends `WorkflowPlugin` from cmem-plugin-base
- Takes input entities and starts sub-workflow for each entity
- `WorkflowExecution` dataclass manages individual workflow execution status
- `WorkflowExecutionList` handles queue-based execution with configurable parallelism
- Implements polling-based workflow status monitoring with async execution
- Supports both entity metadata and file content processing

**cmem_plugin_loopwf/workflow_type.py** - Workflow type definitions and utilities:
- Custom parameter types for workflow selection
- Dynamic value fetching and autocomplete integration

**cmem_plugin_loopwf/exceptions.py** - Custom exception classes:
- Plugin-specific error handling and exception types

### Key Patterns

- **Dataclass Configuration**: Uses `@dataclass` for parameter models with type hints
- **Decorator-Based Registration**: Plugins use `@Plugin` decorator from cmem-plugin-base
- **Autocomplete Integration**: Custom parameter types with dynamic value fetching
- **Async Workflow Execution**: Non-blocking workflow starts with status polling

### Project Structure

```
cmem_plugin_loopwf/
├── task.py           # Main plugin logic
├── workflow_type.py  # Workflow type definitions and utilities
├── exceptions.py     # Custom exception classes
├── loopwf.svg       # Plugin icon
└── __init__.py      # Plugin registration
tests/               # Unit and integration tests
├── conftest.py      # Test configuration
├── test_task.py     # Task plugin tests
├── test_discovery.py        # Plugin discovery tests
├── test_workflow_type.py    # Workflow type tests
├── test_workflow_execution_list.py  # Execution list tests
└── utils.py         # Test utilities
```

## Development Workflow

### Dependencies
- **Poetry** for package management (not pip/requirements.txt)
- **Ruff** for linting and formatting (replaces black/isort/flake8)
- **MyPy** for type checking
- **Pre-commit** hooks for quality gates

### Testing
- Unit tests in `tests/` directory using pytest
- Integration tests require running CMEM instance
- Test configuration in `pyproject.toml` under `[tool.pytest.ini_options]`

### Plugin Development
- Extend `WorkflowPlugin` base class from cmem-plugin-base
- Use type hints extensively - this is a strongly typed codebase
- Follow the existing parameter model pattern with dataclasses
- All plugins must be registered in `__init__.py`

### CMEM Integration
- Plugin outputs must be compatible with CMEM's RDF/entity model
- Uses `cmempy` library for CMEM API interactions (config, get_json, execute_workflow_io, get_workflows_io)
- Authentication handled through user context propagation via `setup_cmempy_user_access`
- All operations are project-scoped within CMEM instance
- Supports async workflow execution via `/api/workflow/executeAsync` endpoint
- Entity conversion to JSON for workflow input via replaceable datasets
- File processing support with configurable MIME types for file-to-workflow scenarios