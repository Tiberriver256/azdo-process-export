"""
Behave step definitions for CLI testing.

Implements the step definitions for testing the command-line interface
of azdo-process-export.
"""

import subprocess
import sys
import os
from pathlib import Path
import shlex
from behave import given, when, then


@given('I have access to the azdo-process-export CLI')
def step_have_cli_access(context):
    """Verify that the CLI is accessible."""
    # The CLI should be accessible via the main module
    context.cli_command = [sys.executable, "-m", "azdo_process_export.cli.main"]


@given('the environment variable "{var_name}" is set to "{var_value}"')
def step_set_environment_variable(context, var_name, var_value):
    """Set an environment variable for the test."""
    if not hasattr(context, 'env_vars'):
        context.env_vars = {}
    context.env_vars[var_name] = var_value


@when('I run "{command}"')
def step_run_command(context, command):
    """Execute a CLI command and capture the result."""
    # Parse the command
    if command.startswith("azdo-process-export"):
        # Replace the command prefix with our Python module call
        args = shlex.split(command)[1:]  # Remove "azdo-process-export", preserve quoted args
        full_command = context.cli_command + args
    else:
        full_command = shlex.split(command)
    
    # Prepare environment
    env = os.environ.copy()
    if hasattr(context, 'env_vars'):
        env.update(context.env_vars)
    
    # Run the command
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent.parent,  # Project root
            timeout=30
        )
        context.cli_exit_code = result.returncode
        context.cli_output = result.stdout
        context.cli_error = result.stderr
    except subprocess.TimeoutExpired:
        context.cli_exit_code = -1
        context.cli_output = ""
        context.cli_error = "Command timed out"
    except Exception as e:
        context.cli_exit_code = -1
        context.cli_output = ""
        context.cli_error = str(e)


@then('the exit code should be {expected_code:d}')
def step_check_exit_code(context, expected_code):
    """Verify the command exit code."""
    actual_code = context.cli_exit_code
    assert actual_code == expected_code, (
        f"Expected exit code {expected_code}, but got {actual_code}. "
        f"Output: {context.cli_output}. Error: {context.cli_error}"
    )


@then('the output should contain "{expected_text}"')
def step_output_contains(context, expected_text):
    """Verify that the output contains specific text."""
    combined_output = context.cli_output + context.cli_error
    assert expected_text in combined_output, (
        f"Expected output to contain '{expected_text}', but got: {combined_output}"
    )


@then('the output should not contain "{unexpected_text}"')
def step_output_not_contains(context, unexpected_text):
    """Verify that the output does not contain specific text."""
    combined_output = context.cli_output + context.cli_error
    assert unexpected_text not in combined_output, (
        f"Expected output to NOT contain '{unexpected_text}', but it was found in: {combined_output}"
    )


@then('a file should be created at "{file_path}"')
def step_file_created(context, file_path):
    """Verify that a file was created."""
    path = Path(file_path)
    if not path.is_absolute():
        path = context.temp_dir / file_path
    
    assert path.exists(), f"Expected file {path} to exist, but it doesn't"
    context.export_file = str(path)


@then('the file "{file_path}" should contain valid JSON')
def step_file_contains_valid_json(context, file_path):
    """Verify that a file contains valid JSON."""
    import json
    
    path = Path(file_path)
    if not path.is_absolute():
        path = context.temp_dir / file_path
    
    try:
        with open(path, 'r') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        assert False, f"File {path} does not contain valid JSON: {e}"
    except FileNotFoundError:
        assert False, f"File {path} does not exist"