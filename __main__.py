#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "azure-devops>=7.0.0",
#     "azure-identity>=1.16.0",
#     "msgraph-core>=1.0.0",
#     "click>=8.1.0",
#     "orjson>=3.9.0",
#     "rich>=13.0.0",
#     "httpx>=0.24.0",
# ]
# ///
"""
Azure DevOps Process Export Tool

A single-command Python CLI that captures every process-relevant facet of an
Azure DevOps project into one comprehensive, portable JSON file.

Usage:
    uv run __main__.py process --project "My Project" --out process.json
"""

import sys
from pathlib import Path

# Add the package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from azdo_process_export.cli.main import cli

if __name__ == "__main__":
    cli()
