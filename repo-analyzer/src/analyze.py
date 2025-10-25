#!/usr/bin/env python3
"""
Universal Repository Analyzer - Main Entry Point
Analyzes ANY GitHub/GitLab repository for SBOM, costs, and comprehensive metrics
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from analyzers.github import GitHubAnalyzer
from analyzers.gitlab import GitLabAnalyzer
from exporters.json_exporter import JSONExporter
from exporters.html_exporter import HTMLExporter
from exporters.pdf_exporter import PDFExporter
from exporters.cyclonedx_exporter import CycloneDXExporter
from utils.config import Config
from utils.logger import setup_logger
from utils.validators import validate_repo_url
from utils.output_manager import create_organized_output

# Load environment variables
load_dotenv()

console = Console()
logger = setup_logger()


def get_analyzer(repo_url: str, config: Config):
    """Factory method to get appropriate analyzer"""
    if 'github.com' in repo_url:
        return GitHubAnalyzer(
            repo_url=repo_url,
            config=config,
            token=config.get('github_token') or os.getenv('GITHUB_TOKEN')
        )
    elif 'gitlab' in repo_url:
        return GitLabAnalyzer(
            repo_url=repo_url,
            config=config,
            token=config.get('gitlab_token') or os.getenv('GITLAB_TOKEN')
        )
    else:
        raise ValueError(f"Unsupported platform for URL: {repo_url}")


@click.command()
@click.argument('repo_url')
@click.option('--output-dir', default='./output', help='Output directory for reports')
@click.option('--hourly-rate', type=float, default=100, help='Hourly rate for cost calculation')
@click.option('--github-token', envvar='GITHUB_TOKEN', help='GitHub Personal Access Token')
@click.option('--gitlab-token', envvar='GITLAB_TOKEN', help='GitLab Personal Access Token')
@click.option('--format', 'output_format', default='json,html,pdf,cyclonedx',
              help='Output formats (comma-separated): json,html,pdf,cyclonedx')
@click.option('--include-vuln', is_flag=True, help='Include vulnerability scanning')
@click.option('--config', 'config_file', type=click.Path(exists=True),
              help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(repo_url, output_dir, hourly_rate, github_token, gitlab_token,
         output_format, include_vuln, config_file, verbose):
    """
    Universal Repository Analyzer - SBOM & Cost Estimator
    
    Analyzes ANY GitHub/GitLab repository to generate:
    - Software Bill of Materials (SBOM) in CycloneDX format
    - Development cost estimates based on COCOMO II
    - Contributor analytics and language statistics
    - Comprehensive dependency analysis
    
    Works with: Python, Node.js, Java, Go, Rust, Unity, Ruby, PHP, and more!
    
    Example:
        python analyze.py https://github.com/owner/repo.git --verbose
    """
    try:
        # Display banner
        console.print(Panel.fit(
            "[bold cyan]Universal Repository Analyzer[/bold cyan]\n"
            "[dim]SBOM Generator & Cost Estimator for ANY Project Type[/dim]",
            border_style="cyan"
        ))
        
        # Validate URL
        if not validate_repo_url(repo_url):
            console.print("[bold red]Error:[/bold red] Invalid repository URL", style="bold red")
            sys.exit(1)
        
        # Load configuration
        config = Config(config_file) if config_file else Config()
        config.set('output_dir', output_dir)
        config.set('hourly_rate', hourly_rate)
        config.set('github_token', github_token)
        config.set('gitlab_token', gitlab_token)
        config.set('include_vuln', include_vuln)
        config.set('verbose', verbose)
        
        # Parse output formats
        formats = [f.strip().lower() for f in output_format.split(',')]
        config.set('output_formats', formats)
        
        # Determine platform from URL
        platform = 'github' if 'github.com' in repo_url else 'gitlab'
        
        # Extract repo name from URL for session creation
        repo_name_parts = repo_url.rstrip('.git').split('/')
        repo_name_temp = repo_name_parts[-1] if repo_name_parts else 'unknown'
        
        # Create organized output session
        session = create_organized_output(
            repo_name=repo_name_temp,
            repo_url=repo_url,
            platform=platform,
            base_dir=output_dir
        )
        
        # Update output path to use session directory
        output_path = Path(session['base_dir'])
        reports_path = Path(session['reports_dir'])
        sbom_path = Path(session['sbom_dir'])
        raw_data_path = Path(session['raw_data_dir'])
        logs_path = Path(session['logs_dir'])
        
        console.print(f"\n[bold]Repository:[/bold] {repo_url}")
        console.print(f"[bold]Session ID:[/bold] {session['session_id']}")
        console.print(f"[bold]Output Directory:[/bold] {session['base_dir']}")
        console.print(f"[bold]Output Formats:[/bold] {', '.join(formats)}")
        console.print(f"[bold]Hourly Rate:[/bold] ${hourly_rate}\n")
        
        # Get appropriate analyzer
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Initialize analyzer
            task1 = progress.add_task("[cyan]Initializing analyzer...", total=None)
            analyzer = get_analyzer(repo_url, config)
            progress.update(task1, completed=True)
            
            # Fetch repository info
            task2 = progress.add_task("[cyan]Fetching repository information...", total=None)
            analyzer.get_repo_info()
            progress.update(task2, completed=True)
            
            # Scan dependencies
            task3 = progress.add_task("[cyan]Scanning dependencies (SBOM)...", total=None)
            analyzer.scan_dependencies()
            progress.update(task3, completed=True)
            
            # Analyze costs (THIS IS WHERE THE BUG WAS - commits showing 0)
            task4 = progress.add_task("[cyan]Analyzing development costs...", total=None)
            analyzer.analyze_costs(hourly_rate)
            progress.update(task4, completed=True)
            
            # Get results
            results = analyzer.get_results()
        
        # Export results
        console.print("\n[bold cyan]Generating Reports...[/bold cyan]\n")
        
        repo_name = analyzer.repo_name
        
        # Create exporters with organized paths
        exporters = {
            'json': JSONExporter(reports_path, repo_name),
            'html': HTMLExporter(reports_path, repo_name),
            'pdf': PDFExporter(reports_path, repo_name),
            'cyclonedx': CycloneDXExporter(sbom_path, repo_name)
        }
        
        generated_files = []
        for format_name in formats:
            if format_name in exporters:
                exporter = exporters[format_name]
                file_path = exporter.export(results)
                generated_files.append((format_name.upper(), file_path))
                console.print(f"  ✓ {format_name.upper()}: {file_path}", style="green")
        
        # Save session metadata
        import json
        metadata_file = Path(session['metadata_file'])
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Update metadata with analysis results
        metadata['analysis_results'] = {
            'total_dependencies': results['sbom'].get('total_dependencies', 0),
            'total_commits': results['cost_analysis'].get('total_commits', 0),
            'total_contributors': results['cost_analysis'].get('total_contributors', 0),
            'estimated_cost': results['cost_analysis'].get('estimated_cost', 0),
            'estimated_hours': results['cost_analysis'].get('estimated_hours', 0),
            'generated_files': [str(f[1]) for f in generated_files]
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        console.print(f"\n  ✓ Metadata: {metadata_file}", style="green")
        
        # Display comprehensive summary
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            f"[bold green]✅ Analysis Complete![/bold green]\n\n"
            f"[bold]Repository:[/bold] {repo_url}\n"
            f"[bold]Session:[/bold] {session['session_id']}\n"
            f"[bold]Project Type:[/bold] {results['sbom'].get('project_type', 'Multi-language')}\n"
            f"[bold]Total Dependencies:[/bold] {results['sbom'].get('total_dependencies', 0)}\n"
            f"[bold]Package Managers:[/bold] {len(results['sbom'].get('package_managers', []))}\n"
            f"[bold]Total Commits:[/bold] {results['cost_analysis'].get('total_commits', 0):,}\n"
            f"[bold]Contributors:[/bold] {results['cost_analysis'].get('total_contributors', 0)}\n"
            f"[bold]Estimated Cost:[/bold] ${results['cost_analysis'].get('estimated_cost', 0):,.2f}\n"
            f"[bold]Estimated Hours:[/bold] {results['cost_analysis'].get('estimated_hours', 0):,}\n\n"
            f"[dim]Dependencies:Commits Ratio = {results['sbom'].get('total_dependencies', 0)}:{results['cost_analysis'].get('total_commits', 0)}[/dim]",
            title="[bold]Summary[/bold]",
            border_style="green"
        ))
        
        console.print(f"\n[bold]📁 Analysis Session:[/bold] {output_path.absolute()}\n")
        console.print(f"[bold]🔗 Latest Symlink:[/bold] {Path(output_dir) / 'latest'}\n")
        
        # Show file listing
        console.print("[bold]Generated Files:[/bold]")
        for format_name, file_path in generated_files:
            console.print(f"  • {format_name}: [link=file://{file_path}]{file_path}[/link]")
        
        console.print("\n[bold]Session Structure:[/bold]")
        console.print(f"  • Reports:  {reports_path}")
        console.print(f"  • SBOM:     {sbom_path}")
        console.print(f"  • Raw Data: {raw_data_path}")
        console.print(f"  • Logs:     {logs_path}")
        console.print(f"  • Metadata: {metadata_file}")
        
        console.print("\n" + "="*70 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Analysis interrupted by user[/bold yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}", style="bold red")
        if verbose:
            console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())
