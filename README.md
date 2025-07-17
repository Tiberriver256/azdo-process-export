# azdo-process-export

[![Release](https://img.shields.io/github/v/release/Tiberriver256/azdo-process-export)](https://img.shields.io/github/v/release/Tiberriver256/azdo-process-export)
[![Build status](https://img.shields.io/github/actions/workflow/status/Tiberriver256/azdo-process-export/main.yml?branch=main)](https://github.com/Tiberriver256/azdo-process-export/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/Tiberriver256/azdo-process-export)](https://img.shields.io/github/license/Tiberriver256/azdo-process-export)

Azure DevOps process export tool - captures complete project configuration and activity trends in portable JSON format.

A single-command Python CLI that dumps every process-relevant facet of an Azure DevOps project into one comprehensive, portable JSON file. It enables delivery leads, process coaches, and analysts to obtain a point-in-time snapshot of configuration and activity trends.

- **GitHub repository**: <https://github.com/Tiberriver256/azdo-process-export/>
- **Documentation**: <https://github.com/Tiberriver256/azdo-process-export/>

## Quick Start

### Using uv (Recommended)

Run directly with PEP 723 inline dependencies:

```bash
uv run __main__.py process --project "My Project" --out process.json
```

### Using pip

```bash
pip install azdo-process-export
azdo-process-export process --project "My Project" --out process.json
```

## Features

- **Zero-configuration auth** for Azure environments via DefaultAzureCredential
- **Comprehensive export** includes:
  - Work item types, fields, and behaviors
  - Team settings and backlog hierarchy
  - Usage metrics via OData Analytics
  - User enrichment from Microsoft Graph
- **Fast performance** with asyncio (≤5 min for 50k work items)
- **Portable JSON output** (≤50 MB in 95% of projects)
- **Resilient** with exponential backoff for transient failures

## Authentication

The tool attempts authentication in this order:
1. **DefaultAzureCredential** (managed identity, Azure CLI, etc.)
2. **Personal Access Token** via `--pat` flag

```bash
# Using DefaultAzureCredential (recommended in Azure)
uv run __main__.py process --project "My Project" --out process.json

# Using PAT for local development
uv run __main__.py process --project "My Project" --pat $AZDO_PAT --out process.json
```

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/Tiberriver256/azdo-process-export.git
cd azdo-process-export
uv sync --dev
```

### 2. Run Pre-commit Hooks

```bash
uv run pre-commit run -a
```

### 3. Run Tests

```bash
# BDD tests with Behave
uv run behave

# Unit tests with pytest
uv run pytest
```

## Project Structure (Screaming Architecture)

```
azdo_process_export/
├── domain/          # Business logic (Process, Metrics)
├── infrastructure/  # Azure DevOps APIs, Analytics
├── cli/            # Click command interface
├── tests/          # Behave BDD scenarios
└── scripts/        # Sample notebooks
```

## Output Format

The tool generates a comprehensive JSON file containing:

```json
{
  "exportedAt": "2025-07-17T15:04:05Z",
  "project": { "id": "...", "name": "My Project" },
  "workItemTypes": [{ "name": "User Story", "usageLast12M": 1234 }],
  "fields": [{ "refName": "System.Title", "type": "string" }],
  "behaviors": [{ "name": "EpicsKanban", "inherits": "Kanban" }],
  "teams": [{
    "id": "...", "name": "Backend",
    "settings": { "bugsBehavior": "asTasks" },
    "members": [{ "displayName": "Alice", "roleHint": "PR-heavy" }]
  }],
  "metrics": {
    "workItemsClosedPerMonth": { "2025-06": 42 },
    "prsMergedPerMonth": { "2025-06": 18 }
  }
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Repository created with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).