"""
Behave environment configuration for Azure DevOps process export tests.

Sets up test environment, fixtures, and cleanup for BDD scenarios.
"""

import os
import tempfile
from pathlib import Path


def before_all(context):
    """Set up test environment before all scenarios."""
    # Create temporary directory for test outputs
    context.temp_dir = Path(tempfile.mkdtemp(prefix="azdo_export_test_"))
    
    # Set default test organization and project
    context.test_organization = os.environ.get("AZDO_TEST_ORGANIZATION", "demo-org")
    context.test_project = os.environ.get("AZDO_TEST_PROJECT", "Demo Project")
    context.test_pat = os.environ.get("AZDO_TEST_PAT")
    
    # Initialize result tracking
    context.export_results = {}
    context.cli_exit_code = None
    context.cli_output = ""


def after_all(context):
    """Clean up test environment after all scenarios."""
    # Clean up temporary files
    import shutil
    if context.temp_dir.exists():
        shutil.rmtree(context.temp_dir)


def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Reset scenario-specific state
    context.export_file = None
    context.cli_exit_code = None
    context.cli_output = ""
    context.cli_error = ""


def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Clean up any created files
    if hasattr(context, 'export_file') and context.export_file:
        export_path = Path(context.export_file)
        if export_path.exists():
            export_path.unlink()
