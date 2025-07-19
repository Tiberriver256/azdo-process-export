"""
Azure DevOps Process Export CLI

Main command-line interface using Click for the azdo-process-export tool.
"""

import sys
from pathlib import Path

import click
from rich.console import Console

from azdo_process_export.infrastructure.logging import setup_logging, get_logger

console = Console()


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["info", "debug", "trace"], case_sensitive=False),
    default="info",
    help="Set logging level",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    help="Optional log file path for structured JSON logs",
)
@click.version_option(version="0.1.0", prog_name="azdo-process-export")
def cli(log_level: str, log_file: Path | None) -> None:
    """Azure DevOps process export tool.

    Captures complete project configuration and activity trends in portable JSON format.

    \b
    Authentication Methods:
        The tool uses credential precedence for secure authentication:

        1. Personal Access Token (--pat flag or AZDO_PAT env var)
           - Takes precedence when provided
           - Uses Basic Auth, no fallback if PAT fails

        2. DefaultAzureCredential (automatic fallback)
           - Azure CLI (az login), managed identity, Visual Studio
           - Uses Bearer Auth with appropriate Azure DevOps scopes

    \b
    Required Configuration:
        AZDO_ORGANIZATION environment variable or --organization flag
    """
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_trace=(log_level.lower() == "trace")
    )


@cli.command()
@click.argument("project_name")
@click.option(
    "--out", type=click.Path(path_type=Path), default="process.json", help="Output file path (default: ./process.json)"
)
@click.option("--pat", envvar="AZDO_PAT", help="Personal Access Token (overrides DefaultAzureCredential)")
@click.option("--skip-metrics", is_flag=True, help="Export configuration only, no Analytics queries")
@click.option("--organization", envvar="AZDO_ORGANIZATION", help="Azure DevOps organization name or URL")
def process(project_name: str, out: Path, pat: str | None, skip_metrics: bool, organization: str | None) -> None:
    """Export every process artifact and activity metric for PROJECT_NAME into a single JSON file.

    \b
    Examples:
        azdo-process-export process "My Project"
        azdo-process-export process "My Project" --out export.json
        azdo-process-export process "My Project" --pat $AZDO_PAT
        azdo-process-export process "My Project" --skip-metrics

    \b
    Authentication Troubleshooting:
        Authentication failures result in exit code 2. Common solutions:

        • Ensure AZDO_ORGANIZATION is set or use --organization flag
        • For DefaultAzureCredential: Run 'az login' or configure managed identity
        • For PAT: Verify token has required scopes (Work Items: Read, Analytics: Read)
        • Check structured logs for detailed error information
    """
    logger = get_logger(__name__)
    logger.info("Starting export for project", project=project_name)

    if not organization:
        logger.error("Organization not specified", error="missing_organization")
        console.print("[red]Organization not specified. Use --organization or set AZDO_ORGANIZATION environment variable.[/red]")
        sys.exit(1)

    # Import authentication logic
    from azdo_process_export.infrastructure.auth import AuthenticationError, get_credentials

    try:
        auth_headers, credential_source = get_credentials(pat)

        logger.info("Authentication headers generated", credential_source=credential_source)

        # Simulate using the headers for an API call (actual export logic not yet implemented)
        logger.info(
            "Export operation started",
            project=project_name,
            organization=organization,
            output_file=str(out),
            credential_source=credential_source,
            skip_metrics=skip_metrics
        )

        if skip_metrics:
            logger.info("Skipping Analytics metrics collection", skip_metrics=True)

        console.print("Export would complete successfully!", style="green")
        sys.exit(0)

    except AuthenticationError as e:
        logger.error("Authentication failed", error=str(e), event="auth_failure")
        console.print(f"[red]Authentication failed: {e}[/red]")
        sys.exit(2)


if __name__ == "__main__":
    cli()
