# azdo-process-export

[![Release](https://img.shields.io/github/v/release/Tiberriver256/azdo-process-export)](https://img.shields.io/github/v/release/Tiberriver256/azdo-process-export)
[![Build status](https://img.shields.io/github/actions/workflow/status/Tiberriver256/azdo-process-export/main.yml?branch=main)](https://github.com/Tiberriver256/azdo-process-export/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/Tiberriver256/azdo-process-export)](https://img.shields.io/github/license/Tiberriver256/azdo-process-export)

Azure DevOps process export tool - captures complete project configuration and activity trends in portable JSON format.

A single-command Python CLI that dumps every process-relevant facet of an Azure DevOps project into one comprehensive, portable JSON file. It enables delivery leads, process coaches, and analysts to obtain a point-in-time snapshot of configuration and activity trends.

- **GitHub repository**: <https://github.com/Tiberriver256/azdo-process-export/>
- **Documentation**: <https://github.com/Tiberriver256/azdo-process-export/>

## Quick Start


### Quick Start (uv Only)

Run directly with PEP 723 inline dependencies:

```bash
uv run __main__.py process --project "My Project" --out process.json
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

### Credential Precedence

The tool supports two authentication methods with clear precedence:

1. **Personal Access Token (PAT)** - If `--pat` is provided, it takes precedence and is used for Basic Auth. No fallback occurs if PAT fails.
2. **DefaultAzureCredential** - Used automatically when no PAT is provided. Supports managed identity, Azure CLI (`az login`), Visual Studio, etc.

```bash
# Using DefaultAzureCredential (recommended in Azure environments)
export AZDO_ORGANIZATION="your-org"
uv run __main__.py process "My Project" --out process.json

# Using PAT for local development or CI/CD
export AZDO_ORGANIZATION="your-org"
uv run __main__.py process "My Project" --pat $AZDO_PAT --out process.json
```

### Troubleshooting

**Authentication failures (exit code 2):**
- Ensure `AZDO_ORGANIZATION` environment variable is set
- For DefaultAzureCredential: Run `az login` or configure managed identity
- For PAT: Verify token has required scopes (Work Items: Read, Analytics: Read)
- Check structured logs for detailed error information

**Missing organization (exit code 1):**
- Set `AZDO_ORGANIZATION` environment variable or use `--organization` flag

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

## TDD Workflow for CLI Development

This project uses **Test-Driven Development (TDD)** for CLI features, with full coverage via Behave BDD scenarios and step definitions.

### Workflow Steps
1. **Write Behave feature scenarios** in `tests/features/cli_basic.feature` for each CLI requirement (help, version, argument validation, error handling, etc).
2. **Implement failing step definitions** in `tests/steps/cli_steps.py` to drive CLI invocation and output checks.
3. **Develop CLI code** in `azdo_process_export/cli/main.py` to pass the scenarios, using Click for argument parsing and Rich for output/logging.
4. **Run tests** with `uv run behave` to verify all scenarios pass. Fix code and tests until green.
5. **Iterate**: Add new scenarios for each feature or bug fix, and repeat the cycle.

#### Example Scenario
```feature
Scenario: Require organization configuration
  When I run "azdo-process-export process 'Test Project'"
  Then the exit code should be 1
  And the output should contain "Organization not specified"
```

#### Example Step Definition
```python
@when('I run "{command}"')
def step_run_command(context, command):
    # Uses shlex.split to preserve quoted arguments
    ...
```

#### Example CLI Implementation
```python
@click.command()
@click.argument("project_name")
@click.option("--organization", ...)
def process(...):
    if not organization:
        logger.error("Organization not specified.")
        sys.exit(1)
```
See `tests/features/cli_basic.feature` and `tests/steps/cli_steps.py` for full coverage examples.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Repository created with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).