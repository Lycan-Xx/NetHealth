"""Command-line interface for NetHealth."""
import logging
import sys
from typing import Optional

import click
from rich.logging import RichHandler

from nethealth.core.analyzer import NetworkAnalyzer
from nethealth.adapters.console_reporter import ConsoleReporter
from nethealth.core.history_manager import JSONHistoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("nethealth")

@click.group()
@click.version_option()
def cli():
    """NetHealth - Network Analysis Tool"""
    pass

@cli.command()
@click.option("--save/--no-save", default=True, help="Save results to history")
@click.option("--plugins", help="Comma-separated list of plugins to enable")
def analyze(save: bool, plugins: Optional[str]):
    """Run network analysis"""
    try:
        analyzer = NetworkAnalyzer()
        reporter = ConsoleReporter()
        history = JSONHistoryManager()
        
        # Run analysis
        report = analyzer.analyze()
        
        # Display results
        reporter.report(report)
        
        # Save to history
        if save:
            history.save(report)
            click.echo("Results saved to history")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option("--limit", default=5, help="Number of records to show")
def history(limit: int):
    """View analysis history"""
    try:
        history = JSONHistoryManager()
        reporter = ConsoleReporter()
        
        reports = history.get_latest(limit)
        for report in reports:
            reporter.report(report)
            click.echo("\n" + "-" * 80 + "\n")
            
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        sys.exit(1)

def main():
    """Entry point for the CLI"""
    cli()