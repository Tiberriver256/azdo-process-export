---
description: Testing practices and guidelines for this project - BDD testing only, no unit testing
applyTo: '**'
alwaysApply: true
---

# Testing Practices

## Overview

This project uses **Behavior-Driven Development (BDD) testing exclusively** with [Behave](https://behave.readthedocs.io/). **Unit testing is not used in this project.**

## Testing Philosophy

- **BDD Only**: All testing is done through Behave feature scenarios that describe behavior from the user's perspective
- **No Unit Tests**: This project deliberately does not use unit testing frameworks like pytest, unittest, or similar
- **End-to-End Focus**: Tests validate complete user workflows and integration scenarios
- **Real Environment**: Tests use actual Azure DevOps demo environments for authentic validation

## Testing Guidelines

### **Writing Tests**

- **Create Gherkin scenarios** in `features/` directory using `.feature` files
- **Implement step definitions** in `features/steps/` directory
- **Focus on user behavior** rather than implementation details
- **Test complete workflows** from CLI invocation to final output

### **Test Categories**

1. **CLI Basic Tests** (`features/cli_basic.feature`)
   - Command line argument validation
   - Help and version information
   - Error handling and exit codes

2. **Authentication Tests** (`features/authentication.feature`)
   - Azure credential chain validation
   - PAT token handling
   - Error scenarios

3. **Logging Tests** (`features/logging.feature`)
   - Structured logging validation
   - Log level handling
   - Sensitive data protection

4. **HTTP Client Tests** (`features/http_client.feature`)
   - API integration scenarios
   - Error handling and retries

### **Running Tests**

```bash
# Run all BDD tests
uv run behave

# Run tests with verbose output
uv run behave --verbose

# Run specific feature
uv run behave features/cli_basic.feature

# Dry run to validate syntax
uv run behave --dry-run
```

### **Test Environment Setup**

- Tests use `features/environment.py` for setup and teardown
- Environment variables are managed per test scenario
- Temporary files and directories are cleaned up automatically

## What NOT to Do

- **Do not add unit testing frameworks** (pytest, unittest, etc.)
- **Do not create test/ or tests/ directories** - use features/ only
- **Do not write implementation-focused tests** - focus on user behavior
- **Do not test internal functions** - test complete workflows

## Adding New Tests

1. **Identify the user scenario** you want to validate
2. **Write a Gherkin feature** describing the expected behavior
3. **Implement step definitions** to execute the scenario
4. **Run the test** to ensure it passes
5. **Update this documentation** if new patterns emerge

## Example Test Structure

```gherkin
Feature: Authentication validation
  As a user of azdo-process-export
  I want authentication to work reliably
  So that I can export process data

  Scenario: Default Azure credential success
    Given I have access to the azdo-process-export CLI
    And the environment variable "AZDO_ORGANIZATION" is set to "demo-org"
    When I run "azdo-process-export process 'Test Project'"
    Then the exit code should be 0
    And the output should contain export completion message
```

## Contribution Guidelines

- **All new features** must include corresponding BDD scenarios
- **All bug fixes** should include regression tests via BDD
- **Test coverage** is measured by scenario coverage, not code coverage
- **CI/CD integration** runs `uv run behave` for validation

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/)
- Project BDD scenarios: `features/` directory