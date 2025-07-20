---
description: Project-wide convention for using `uv` to execute Python commands, scripts, and utilities
applyTo: '**'
---

# Python Command Execution: Use `uv` Exclusively

## Purpose

To ensure consistent, reliable, and isolated execution of all Python commands, scripts, and utilities, this project **requires** the use of [`uv`](https://astral.sh/uv/) for all Python-related operations.

## Rules

- **All Python scripts and CLI tools must be executed using `uv`** (preferably `uv run <script.py>` or `uvx <tool>`), not directly with `python`, `pip`, or other legacy methods.
- **Dependency management** must use `uv add`, `uv lock`, and `uv sync`.
- **Tool execution** (behave, ruff, etc.) should use `uv run <tool>` or `uvx <tool>`.
- **Python version selection** should be managed via `uv` options (e.g., `--python 3.11`).
- **Installation**: If `uv` is not installed, follow the official instructions:
  - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Or use `pipx install uv`
- **Documentation**: All README, developer guides, and instructions must reference `uv` for Python execution and management.

## Example Usage

- Run a script: `uv run script.py`
- Run a tool: `uvx behave` or `uv run behave`
- Add a dependency: `uv add requests`
- Sync dependencies: `uv sync`
- Specify Python version: `uv run --python 3.11 script.py`

## Rationale

Using `uv` ensures:

- Fast, isolated, and reproducible environments
- Consistent dependency management
- Simplified tool execution
- Modern Python workflow

## Enforcement

- PRs and commits that do not follow this convention may be rejected.
- All CI/CD pipelines and developer scripts must use `uv`.

---

For more details, see [uv documentation](https://docs.astral.sh/uv/).
