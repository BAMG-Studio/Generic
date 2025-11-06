"""JSON Reporter - Author: Peter"""
import json
from pathlib import Path

class JSONReporter:
    def __init__(self, findings, output_dir):
        self.findings = findings
        self.output_dir = Path(output_dir)
        
    def generate(self):
        output_file = self.output_dir / "audit.json"
        with open(output_file, "w") as f:
            json.dump(self.findings, f, indent=2, default=str)
