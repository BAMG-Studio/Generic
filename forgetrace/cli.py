#!/usr/bin/env python3
"""CLI for ForgeTrace - Author: Peter"""
import argparse
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path
import yaml
from .audit import AuditEngine
from .classifiers import MLIPClassifier


def cmd_audit(args, config):
    """Run audit command"""
    engine = AuditEngine(args.repo_path, args.out, config)
    findings = engine.run()
    
    # Print output paths
    out_dir = Path(args.out).resolve()
    print(f"\n{'='*60}")
    print(f"✓ Audit complete!")
    print(f"{'='*60}\n")
    print("📁 Output Files:")
    
    files_to_check = [
        ("audit.json", "Complete findings (JSON)"),
        ("ip_contribution_table.md", "IP contribution table"),
        ("report.html", "Interactive HTML report"),
        ("executive_summary.html", "Executive summary (HTML)"),
        ("executive_summary.pdf", "Executive summary (PDF)"),
    ]
    
    for filename, description in files_to_check:
        filepath = out_dir / filename
        if filepath.exists():
            print(f"  ✓ {filename:<30} - {description}")
            print(f"    file://{filepath}")
        else:
            print(f"  ✗ {filename:<30} - Not generated")
    
    print(f"\n💡 View reports:")
    print(f"   forgetrace preview {args.out}")
    print(f"   (or open files manually with your browser)\n")
    return findings


def cmd_export_training(args, config):
    """Run audit and export training data for the ML classifier."""
    findings = cmd_audit(args, config)
    ml_classifier = MLIPClassifier(findings, config)
    ml_classifier.export_training_data(args.training_output)


def cmd_preview(args):
    """Launch HTTP server to preview reports"""
    output_dir = Path(args.output_dir).resolve()
    
    if not output_dir.exists():
        print(f"Error: Directory not found: {output_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find HTML report
    report_html = output_dir / "report.html"
    exec_html = output_dir / "executive_summary.html"
    
    html_file = report_html if report_html.exists() else exec_html if exec_html.exists() else None
    
    if not html_file:
        print(f"Warning: No HTML reports found in {output_dir}", file=sys.stderr)
        print("Looking for: report.html or executive_summary.html\n")
    
    # Start HTTP server
    port = args.port
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(output_dir), **kwargs)
    
    print(f"🚀 Starting HTTP server...")
    print(f"   Directory: {output_dir}")
    print(f"   URL: http://localhost:{port}/")
    
    if html_file:
        print(f"   Report: http://localhost:{port}/{html_file.name}")
    
    print(f"\n📊 Available files:")
    for file in sorted(output_dir.iterdir()):
        if file.is_file():
            print(f"   - {file.name}")
    
    print(f"\n💡 Press Ctrl+C to stop the server\n")
    
    # Auto-open browser if requested
    if args.browser and html_file:
        url = f"http://localhost:{port}/{html_file.name}"
        print(f"🌐 Opening {url} in browser...")
        webbrowser.open(url)
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n✓ Server stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="ForgeTrace IP Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run audit
  forgetrace audit /path/to/repo --out ./results

  # Preview reports
  forgetrace preview ./results

  # Preview on custom port with auto-open
  forgetrace preview ./results --port 8080 --browser
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run IP audit on repository")
    audit_parser.add_argument("repo_path", help="Path to repository")
    audit_parser.add_argument("--out", default="./out", help="Output directory")
    audit_parser.add_argument("--config", default="config.yaml", help="Config file")
    
    # Metadata arguments for report generation
    audit_parser.add_argument("--client-name", help="Client/project name for reports")
    audit_parser.add_argument("--engagement-window", help="Engagement timeframe (e.g., 'Q4 2025')")
    audit_parser.add_argument("--prepared-by", help="Name of person/team preparing report")
    audit_parser.add_argument("--contact-email", help="Contact email for report")
    
    # Tool path overrides
    audit_parser.add_argument("--syft", help="Path to syft binary")
    audit_parser.add_argument("--scancode", help="Path to scancode")
    audit_parser.add_argument("--semgrep", help="Path to semgrep")
    audit_parser.add_argument("--trufflehog", help="Path to trufflehog")
    audit_parser.add_argument("--gitleaks", help="Path to gitleaks")

    export_parser = subparsers.add_parser(
        "export-training",
        help="Run audit and export ML training data"
    )
    export_parser.add_argument("repo_path", help="Path to repository")
    export_parser.add_argument("--out", default="./out", help="Output directory")
    export_parser.add_argument("--config", default="config.yaml", help="Config file")
    export_parser.add_argument(
        "--training-output",
        default="training_data.jsonl",
        help="Training data JSONL output path"
    )
    export_parser.add_argument("--client-name", help="Client/project name for reports")
    export_parser.add_argument(
        "--engagement-window",
        help="Engagement timeframe (e.g., 'Q4 2025')"
    )
    export_parser.add_argument("--prepared-by", help="Name of person/team preparing report")
    export_parser.add_argument("--contact-email", help="Contact email for report")
    export_parser.add_argument("--syft", help="Path to syft binary")
    export_parser.add_argument("--scancode", help="Path to scancode")
    export_parser.add_argument("--semgrep", help="Path to semgrep")
    export_parser.add_argument("--trufflehog", help="Path to trufflehog")
    export_parser.add_argument("--gitleaks", help="Path to gitleaks")
    
    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Launch HTTP server to view reports")
    preview_parser.add_argument("output_dir", help="Directory containing audit results")
    preview_parser.add_argument("--port", type=int, default=8000, help="HTTP server port (default: 8000)")
    preview_parser.add_argument("--browser", action="store_true", help="Auto-open browser")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command in {"audit", "export-training"}:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Config not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Override metadata from CLI
        if not config.get("metadata"):
            config["metadata"] = {}
        if args.client_name:
            config["metadata"]["client_name"] = args.client_name
        if args.engagement_window:
            config["metadata"]["engagement_window"] = args.engagement_window
        if args.prepared_by:
            config["metadata"]["prepared_by"] = args.prepared_by
        if args.contact_email:
            config["metadata"]["contact_email"] = args.contact_email
        
        # Override tool paths from CLI
        if args.syft:
            config["tools"]["syft"] = args.syft
        if args.scancode:
            config["tools"]["scancode"] = args.scancode
        if args.semgrep:
            config["tools"]["semgrep"] = args.semgrep
        if args.trufflehog:
            config["tools"]["trufflehog"] = args.trufflehog
        if args.gitleaks:
            config["tools"]["gitleaks"] = args.gitleaks

        if args.command == "audit":
            cmd_audit(args, config)
        else:
            cmd_export_training(args, config)
    
    elif args.command == "preview":
        cmd_preview(args)

if __name__ == "__main__":
    main()
