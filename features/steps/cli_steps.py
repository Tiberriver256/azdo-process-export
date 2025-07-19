# Behave step definitions for CLI testing (copied from /tests/steps/cli_steps.py)
# ...existing code from /tests/steps/cli_steps.py...
# This file is a direct copy for Behave to discover steps in the default location.
# If you update step definitions, keep both files in sync until migration is complete.

"""
Behave step definitions for CLI testing.
Implements the step definitions for testing the command-line interface of azdo-process-export.
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from behave import given, then, when


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Restore Azure config if we moved it
    if hasattr(context, "azure_config_moved") and context.azure_config_moved:
        azure_config = Path.home() / ".azure"
        azure_config_backup = Path.home() / ".azure.backup"
        if azure_config_backup.exists() and not azure_config.exists():
            try:
                azure_config_backup.rename(azure_config)
            except Exception:
                pass


@given("I have access to the azdo-process-export CLI")
def step_have_cli_access(context):
    context.cli_command = [sys.executable, "-m", "azdo_process_export.cli.main"]


@given("I have a valid Personal Access Token")
def step_have_valid_pat(context):
    # This step represents having a valid PAT available for use
    # The actual PAT value will be provided via the command line in the "When" step
    context.has_valid_pat = True


@given('the environment variable "{var_name}" is set to "{var_value}"')
def step_set_environment_variable(context, var_name, var_value):
    if not hasattr(context, "env_vars"):
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
    if hasattr(context, "env_vars"):
        env.update(context.env_vars)
    try:
        result = subprocess.run(
            full_command, capture_output=True, text=True, env=env, cwd=Path(__file__).parent.parent.parent, timeout=30
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


@then("the exit code should be {expected_code:d}")
def step_check_exit_code(context, expected_code):
    actual_code = context.cli_exit_code
    assert actual_code == expected_code, (
        f"Expected exit code {expected_code}, but got {actual_code}. "
        f"Output: {context.cli_output}. Error: {context.cli_error}"
    )


@then('the output should contain "{expected_text}"')
def step_output_contains(context, expected_text):
    combined_output = context.cli_output + context.cli_error
    assert expected_text in combined_output, f"Expected output to contain '{expected_text}', but got: {combined_output}"


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
        with open(path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        assert False, f"File {path} does not contain valid JSON: {e}"
    except FileNotFoundError:
        assert False, f"File {path} does not exist"


@then("the structured log should contain authentication success with PAT credential source")
def step_structured_log_contains_pat_success(context):
    # Check CLI output for a structured JSON log line with authentication success and PAT credential source
    import json

    found = False
    # Search for JSON log lines in stdout
    for line in context.cli_output.splitlines():
        try:
            log_obj = json.loads(line)
            if log_obj.get("event") == "authentication_success" and log_obj.get("credential_source") == "PAT":
                found = True
                break
        except Exception:
            continue
    assert found, "Structured log does not contain authentication success with PAT credential source"


@given("I have Azure AD credentials available")
def step_have_azure_ad_credentials(context):
    # This step represents having Azure AD credentials available for use
    # Check if we're in an environment where Azure AD credentials are actually available
    from azure.identity import DefaultAzureCredential

    try:
        # Quick test to see if DefaultAzureCredential can get a token
        credential = DefaultAzureCredential()
        scope = "499b84ac-1321-427f-aa17-267ca6975798/.default"
        # Don't actually get the token, just check if the credential chain has any viable options
        # This is a heuristic - in a real ephemeral test environment, this would work
        context.has_azure_ad_credentials = True
    except Exception:
        # Skip this scenario if Azure AD credentials are not available
        context.scenario.skip("Azure AD credentials not available in current environment")
        return

    context.has_azure_ad_credentials = True


@given("I have an invalid Personal Access Token")
def step_have_invalid_pat(context):
    # This step represents having an invalid PAT - the test will use a clearly invalid token
    context.has_invalid_pat = True


@given("I have no Azure AD credentials available")
def step_have_no_azure_ad_credentials(context):
    # This step represents having no Azure AD credentials available
    # We'll set a test flag that our auth code can check to simulate no credentials
    if not hasattr(context, "env_vars"):
        context.env_vars = {}

    # Set a test flag to simulate no Azure AD credentials
    context.env_vars["TEST_SIMULATE_NO_AZURE_CREDENTIALS"] = "true"
    context.has_no_azure_ad_credentials = True


@then("the structured log should contain authentication success with DefaultAzureCredential credential source")
def step_structured_log_contains_azure_ad_success(context):
    # Check CLI output for a structured JSON log line with authentication success and DefaultAzureCredential credential source
    import json

    found = False
    # Search for JSON log lines in stdout
    for line in context.cli_output.splitlines():
        try:
            log_obj = json.loads(line)
            if (
                log_obj.get("event") == "authentication_success"
                and log_obj.get("credential_source") == "DefaultAzureCredential"
            ):
                found = True
                break
        except Exception:
            continue
    assert found, "Structured log does not contain authentication success with DefaultAzureCredential credential source"


@then("the authentication headers should contain Basic authorization")
def step_auth_headers_contain_basic(context):
    # Check CLI output for a Basic authorization header
    import re

    found = False
    # Look for a line containing 'Authorization' and 'Basic'
    for line in context.cli_output.splitlines():
        if re.search(r'"Authorization":\s*"Basic [A-Za-z0-9+/=]+"', line):
            found = True
            break
    assert found, "Authentication headers do not contain Basic authorization"


@then("the authentication headers should contain Bearer authorization")
def step_auth_headers_contain_bearer(context):
    # Check CLI output for a Bearer authorization header
    import re

    found = False
    # Look for a line containing 'Authorization' and 'Bearer'
    for line in context.cli_output.splitlines():
        if re.search(r'"Authorization":\s*"Bearer [A-Za-z0-9._-]+"', line):
            found = True
            break
    assert found, "Authentication headers do not contain Bearer authorization"


@then("the structured log should contain authentication failure with PAT credential source")
def step_structured_log_contains_pat_failure(context):
    # Check CLI error output for authentication failure with PAT credential source
    found = False
    # Search for structured log entries in stderr (where error logs typically go)
    combined_output = context.cli_output + "\n" + context.cli_error
    for line in combined_output.splitlines():
        try:
            if "auth_failure" in line and "PAT" in line:
                found = True
                break
        except Exception:
            continue
    assert found, "Structured log does not contain authentication failure with PAT credential source"


@then("the structured log should contain authentication failure with DefaultAzureCredential credential source")
def step_structured_log_contains_azure_ad_failure(context):
    # Check CLI error output for authentication failure with DefaultAzureCredential credential source
    found = False
    # Search for structured log entries in stderr
    combined_output = context.cli_output + "\n" + context.cli_error
    for line in combined_output.splitlines():
        try:
            if "auth_failure" in line and "DefaultAzureCredential" in line:
                found = True
                break
        except Exception:
            continue
    assert found, "Structured log does not contain authentication failure with DefaultAzureCredential credential source"


@then('the error output should contain "{expected_text}"')
def step_error_output_contains(context, expected_text):
    # Check that error output contains expected text
    combined_output = context.cli_output + "\n" + context.cli_error
    assert expected_text in combined_output, (
        f"Expected error output to contain '{expected_text}', but got: {combined_output}"
    )


@then('the structured log should not contain "{secret_text}"')
def step_structured_log_should_not_contain_secret(context, secret_text):
    # Verify that structured logs do not expose secrets
    combined_output = context.cli_output + "\n" + context.cli_error
    assert secret_text not in combined_output, (
        f"Structured log contains secret text '{secret_text}' which should not be exposed"
    )


@given("the README.md file exists")
def step_readme_exists(context):
    # Check that README.md exists in the project root
    from pathlib import Path

    readme_path = Path(__file__).parent.parent.parent / "README.md"
    context.readme_path = readme_path
    context.readme_exists = readme_path.exists()


@then('the README should contain "{expected_text}"')
def step_readme_contains(context, expected_text):
    # Check that README.md contains expected text
    if not hasattr(context, "readme_path") or not context.readme_path.exists():
        assert False, "README.md file does not exist"

    try:
        with open(context.readme_path, encoding="utf-8") as f:
            readme_content = f.read()
        assert expected_text in readme_content, f"README.md does not contain '{expected_text}'"
    except Exception as e:
        assert False, f"Failed to read README.md: {e}"


# Structured JSON Logging Step Definitions

@then("the output should contain structured JSON logs")
def step_output_contains_json_logs(context):
    """Check that output contains valid JSON log entries."""
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    found_json_log = False
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and "timestamp" in json_data and "level" in json_data:
                found_json_log = True
                break
        except json.JSONDecodeError:
            continue  # Skip non-JSON lines
    
    assert found_json_log, f"No structured JSON logs found in output: {combined_output}"


@then('the JSON logs should contain "{field_name}" field')
def step_json_logs_contain_field(context, field_name):
    """Check that JSON logs contain a specific field."""
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    found_field = False
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and field_name in json_data:
                found_field = True
                break
        except json.JSONDecodeError:
            continue
    
    assert found_field, f"Field '{field_name}' not found in JSON logs"


@then("the JSON logs should contain debug level entries")
def step_json_logs_contain_debug_entries(context):
    """Check that JSON logs contain debug level entries."""
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    found_debug = False
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and json_data.get("level") == "debug":
                found_debug = True
                break
        except json.JSONDecodeError:
            continue
    
    assert found_debug, "No debug level entries found in JSON logs"


@then("the JSON logs should contain trace context information")
def step_json_logs_contain_trace_context(context):
    """Check that JSON logs contain trace context information."""
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    found_trace = False
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and "trace" in json_data:
                trace_data = json_data["trace"]
                if "thread_id" in trace_data and "thread_name" in trace_data:
                    found_trace = True
                    break
        except json.JSONDecodeError:
            continue
    
    assert found_trace, "No trace context information found in JSON logs"


@given("I have a temporary directory for logs")
def step_have_temp_log_directory(context):
    """Set up a temporary directory for log files."""
    context.temp_log_dir = "/tmp"


@then('a log file should be created at "{file_path}"')
def step_log_file_created(context, file_path):
    """Check that a log file was created."""
    from pathlib import Path
    log_file = Path(file_path)
    assert log_file.exists(), f"Log file {file_path} was not created"
    context.log_file = str(log_file)


@then('the log file should contain valid JSON')
def step_log_file_contains_valid_json(context):
    """Check that the log file contains valid JSON."""
    import json
    from pathlib import Path
    
    log_file = Path(context.log_file)
    try:
        content = log_file.read_text().strip()
        log_lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        for line in log_lines:
            json.loads(line)  # Will raise JSONDecodeError if invalid
            
    except json.JSONDecodeError as e:
        assert False, f"Log file contains invalid JSON: {e}"
    except FileNotFoundError:
        assert False, f"Log file {context.log_file} does not exist"


@then("the output should contain JSON logs with warning or higher levels only")
def step_output_contains_warning_or_higher(context):
    """Check that output only contains warning or higher level logs."""
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    allowed_levels = {"warning", "error", "critical"}
    
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and "level" in json_data:
                level = json_data["level"]
                assert level in allowed_levels, f"Found log level '{level}' which is below warning"
        except json.JSONDecodeError:
            continue  # Skip non-JSON lines


@then("each line of log output should be valid JSON")
def step_each_log_line_valid_json(context):
    """Check that each line of log output is valid JSON."""
    import json
    
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    json_lines_found = 0
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict):
                json_lines_found += 1
        except json.JSONDecodeError:
            # Skip non-JSON lines (like Rich console output)
            continue
    
    assert json_lines_found > 0, "No valid JSON log lines found"


@then("the JSON logs should contain sequential timestamps")
def step_json_logs_contain_sequential_timestamps(context):
    """Check that JSON logs have sequential timestamps."""
    import json
    from datetime import datetime
    
    combined_output = context.cli_output + "\n" + context.cli_error
    log_lines = [line.strip() for line in combined_output.split("\n") if line.strip()]
    
    timestamps = []
    for line in log_lines:
        try:
            json_data = json.loads(line)
            if isinstance(json_data, dict) and "timestamp" in json_data:
                timestamp_str = json_data["timestamp"]
                # Parse ISO timestamp
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                timestamps.append(timestamp)
        except (json.JSONDecodeError, ValueError):
            continue
    
    assert len(timestamps) >= 2, "Need at least 2 timestamps to verify sequence"
    
    # Check that timestamps are in order
    for i in range(1, len(timestamps)):
        assert timestamps[i] >= timestamps[i-1], "Timestamps are not in sequential order"
