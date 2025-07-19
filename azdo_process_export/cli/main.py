"""
Azure DevOps Process Export CLI

Main command-line interface using Click for the azdo-process-export tool.
"""

import click
from rich.console import Console
from rich.logging import RichHandler
import logging
import sys
from pathlib import Path

console = Console()


def setup_logging(log_level: str) -> None:
    """Configure structured logging with Rich output."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["info", "debug", "trace"], case_sensitive=False),
    default="info",
    help="Set logging level"
)
@click.version_option(version="0.1.0", prog_name="azdo-process-export")
def cli(log_level: str) -> None:
    """Azure DevOps process export tool.
    
    Captures complete project configuration and activity trends in portable JSON format.
    """
    setup_logging(log_level)


@cli.command()
@click.argument("project_name")
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default="process.json",
    help="Output file path (default: ./process.json)"
)
@click.option(
    "--pat",
    envvar="AZDO_PAT",
    help="Personal Access Token (overrides DefaultAzureCredential)"
)
@click.option(
    "--skip-metrics",
    is_flag=True,
    help="Export configuration only, no Analytics queries"
)
@click.option(
    "--organization",
    envvar="AZDO_ORGANIZATION",
    help="Azure DevOps organization name or URL"
)
def process(
    project_name: str,
    out: Path,
    pat: str | None,
    skip_metrics: bool,
    organization: str | None
) -> None:
    """Export every process artifact and activity metric for PROJECT_NAME into a single JSON file.
    
    \b
    Examples:
        azdo-process-export process "My Project"
        azdo-process-export process "My Project" --out export.json
        azdo-process-export process "My Project" --pat $AZDO_PAT
        azdo-process-export process "My Project" --skip-metrics
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting export for project: [bold]{project_name}[/bold]", extra={"markup": True})

    if not organization:
        logger.error("Organization not specified. Use --organization or set AZDO_ORGANIZATION environment variable.")
        sys.exit(1)

    # Import authentication logic
    from azdo_process_export.infrastructure.auth import get_credentials, AuthenticationError
    try:
        auth_headers, credential_source = get_credentials(pat)
        
        logger.info("Authentication headers generated", extra={"credential_source": credential_source})
        
        # Simulate using the headers for an API call (actual export logic not yet implemented)
        logger.info(
            f"Would export project '{project_name}' from organization '{organization}' to {out}",
            extra={"credential_source": credential_source}
        )
        
        if skip_metrics:
            logger.info("Skipping Analytics metrics collection")
            
        console.print("Export would complete successfully!", style="green")
        sys.exit(0)
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}", extra={"event": "auth_failure", "error": str(e)})
        console.print(f"[red]Authentication failed: {e}[/red]")
        sys.exit(2)


if __name__ == "__main__":
    cli()