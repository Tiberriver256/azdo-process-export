# Behave step definitions for CLI testing (copied from /tests/steps/cli_steps.py)
# ...existing code from /tests/steps/cli_steps.py...
# This file is a direct copy for Behave to discover steps in the default location.
# If you update step definitions, keep both files in sync until migration is complete.

"""
Behave step definitions for CLI testing.
Implements the step definitions for testing the command-line interface of azdo-process-export.
"""
import subprocess
import sys
import os
from pathlib import Path
import shlex
from behave import given, when, then

@given('I have access to the azdo-process-export CLI')
def step_have_cli_access(context):
    context.cli_command = [sys.executable, "-m", "azdo_process_export.cli.main"]

@given('I have a valid Personal Access Token')
def step_have_valid_pat(context):
    # This step represents having a valid PAT available for use
    # The actual PAT value will be provided via the command line in the "When" step
    context.has_valid_pat = True

@given('the environment variable "{var_name}" is set to "{var_value}"')
def step_set_environment_variable(context, var_name, var_value):
    if not hasattr(context, 'env_vars'):
        context.env_vars = {}
    context.env_vars[var_name] = var_value

@when('I run "{command}"')
def step_run_command(context, command):
    if command.startswith("azdo-process-export"):
        args = shlex.split(command)[1:]
        full_command = context.cli_command + args
    else:
        full_command = shlex.split(command)
    env = os.environ.copy()
    if hasattr(context, 'env_vars'):
        env.update(context.env_vars)
    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent.parent,
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
    actual_code = context.cli_exit_code
    assert actual_code == expected_code, (
        f"Expected exit code {expected_code}, but got {actual_code}. "
        f"Output: {context.cli_output}. Error: {context.cli_error}"
    )

@then('the output should contain "{expected_text}"')
def step_output_contains(context, expected_text):
    combined_output = context.cli_output + context.cli_error
    assert expected_text in combined_output, (
        f"Expected output to contain '{expected_text}', but got: {combined_output}"
    )

@then('the output should not contain "{unexpected_text}"')
def step_output_not_contains(context, unexpected_text):
    combined_output = context.cli_output + context.cli_error
    assert unexpected_text not in combined_output, (
        f"Expected output to NOT contain '{unexpected_text}', but it was found in: {combined_output}"
    )

@then('a file should be created at "{file_path}"')
def step_file_created(context, file_path):
    path = Path(file_path)
    if not path.is_absolute():
        path = context.temp_dir / file_path
    assert path.exists(), f"Expected file {path} to exist, but it doesn't"
    context.export_file = str(path)

@then('the file "{file_path}" should contain valid JSON')
def step_file_contains_valid_json(context, file_path):
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

@then('the structured log should contain authentication success with PAT credential source')
def step_structured_log_contains_pat_success(context):
    assert False, "Structured log does not contain authentication success with PAT credential source (not implemented)"

@then('the authentication headers should contain Basic authorization')
def step_auth_headers_contain_basic(context):
    assert False, "Authentication headers do not contain Basic authorization (not implemented)"
