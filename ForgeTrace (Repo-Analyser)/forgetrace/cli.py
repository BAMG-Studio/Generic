#!/usr/bin/env python3
"""CLI for ForgeTrace - Author: Peter"""
import argparse
import sys
from pathlib import Path
import yaml
from .audit import AuditEngine

def main():
    parser = argparse.ArgumentParser(description="ForgeTrace IP Audit Tool")
    parser.add_argument("command", choices=["audit"], help="Command to run")
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("--out", default="./out", help="Output directory")
    parser.add_argument("--config", default="config.yaml", help="Config file")
    parser.add_argument("--syft", help="Path to syft binary")
    parser.add_argument("--scancode", help="Path to scancode")
    parser.add_argument("--semgrep", help="Path to semgrep")
    parser.add_argument("--trufflehog", help="Path to trufflehog")
    parser.add_argument("--gitleaks", help="Path to gitleaks")
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
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
    
    engine = AuditEngine(args.repo_path, args.out, config)
    engine.run()
    print(f"✓ Audit complete. Results in {args.out}/")

if __name__ == "__main__":
    main()
