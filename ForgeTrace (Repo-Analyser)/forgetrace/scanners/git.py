"""Git Scanner - Author: Peter"""

import subprocess
from collections import defaultdict
from pathlib import Path


class GitScanner:
    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config

    def scan(self):
        if not (self.repo_path / ".git").exists():
            return {"error": "Not a git repository"}

        authors = self._get_authors()
        churn = self._get_churn()
        timeline = self._get_timeline()

        return {
            "authors": authors,
            "churn": churn,
            "timeline": timeline,
            "total_commits": sum(a["commits"] for a in authors.values()),
        }

    def _get_authors(self):
        result = subprocess.run(
            ["git", "shortlog", "-sn", "--all"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        authors = {}
        for line in result.stdout.splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                count, name = parts
                authors[name] = {
                    "commits": int(count),
                    "lines_added": 0,
                    "lines_removed": 0,
                }
        return authors

    def _get_churn(self):
        result = subprocess.run(
            ["git", "log", "--numstat", "--format=%aN"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        churn = defaultdict(lambda: {"added": 0, "removed": 0, "files": set()})
        current_author = None

        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            if "\t" not in line:
                current_author = line.strip()
            else:
                parts = line.split("\t")
                if len(parts) == 3 and current_author:
                    added, removed, filepath = parts
                    if added.isdigit() and removed.isdigit():
                        churn[current_author]["added"] += int(added)
                        churn[current_author]["removed"] += int(removed)
                        churn[current_author]["files"].add(filepath)

        return {
            k: {"added": v["added"], "removed": v["removed"], "files": len(v["files"])}
            for k, v in churn.items()
        }

    def _get_timeline(self):
        result = subprocess.run(
            ["git", "log", "--format=%aN|%aI", "--all"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        commits = []
        for line in result.stdout.splitlines():
            if "|" in line:
                author, date = line.split("|", 1)
                commits.append({"author": author, "date": date})
        return commits
