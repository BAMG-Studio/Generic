"""IP Classifier - Author: Peter"""
from pathlib import Path
from collections import defaultdict

class IPClassifier:
    def __init__(self, findings, config):
        self.findings = findings
        self.config = config
        
    def classify(self):
        """Classify code as third_party, background, foreground, or unknown"""
        classifications = {}
        
        # Third-party from SBOM
        third_party = set()
        for pkg in self.findings.get("sbom", {}).get("packages", []):
            if "file" in pkg:
                third_party.add(pkg["file"])
        
        # Licensed files
        licensed = {}
        for lic in self.findings.get("licenses", {}).get("findings", []):
            if lic.get("license"):
                licensed[lic["file"]] = lic["license"]
        
        # Git authorship
        git_data = self.findings.get("git", {})
        authors = git_data.get("authors", {})
        churn = git_data.get("churn", {})
        
        # Classify each file
        repo_files = self._get_all_files()
        for f in repo_files:
            fstr = str(f)
            if any(tp in fstr for tp in third_party):
                classifications[fstr] = {"origin": "third_party", "license": licensed.get(fstr, "unknown")}
            elif fstr in licensed and licensed[fstr] in ["MIT", "Apache-2.0", "BSD-3-Clause"]:
                classifications[fstr] = {"origin": "third_party", "license": licensed[fstr]}
            else:
                # Check git history
                primary_author = self._get_primary_author(fstr, churn)
                classifications[fstr] = {
                    "origin": "foreground",  # Default assumption
                    "primary_author": primary_author,
                    "license": licensed.get(fstr, "none")
                }
        
        return classifications
    
    def score_rewriteability(self):
        """Score how easy it is to rewrite each module"""
        classifications = self.findings.get("classification", {})
        scores = {}
        
        for filepath, data in classifications.items():
            if data["origin"] == "third_party":
                scores[filepath] = {"score": 0, "reason": "Third-party package"}
                continue
            
            p = Path(filepath)
            if not p.exists():
                continue
            
            try:
                loc = len(p.read_text(errors="ignore").splitlines())
            except:
                loc = 0
            
            complexity = min(loc / 500, 1.0)  # Normalize
            coupling = self._estimate_coupling(filepath)
            test_coverage = 0.5  # Placeholder
            
            score = (1 - complexity) * 0.4 + (1 - coupling) * 0.4 + test_coverage * 0.2
            
            scores[filepath] = {
                "score": round(score, 2),
                "complexity": round(complexity, 2),
                "coupling": round(coupling, 2),
                "loc": loc,
                "rewriteable": score > 0.6
            }
        
        return scores
    
    def estimate_cost(self):
        """Estimate replacement cost for foreground code"""
        classifications = self.findings.get("classification", {})
        rewriteability = self.findings.get("rewriteability", {})
        
        total_loc = 0
        foreground_loc = 0
        
        for filepath, data in classifications.items():
            if data["origin"] == "foreground":
                loc = rewriteability.get(filepath, {}).get("loc", 0)
                foreground_loc += loc
            total_loc += rewriteability.get(filepath, {}).get("loc", 0)
        
        cost_cfg = self.config.get("cost", {})
        days_per_kloc = cost_cfg.get("days_per_kloc", 15)
        hours_per_day = cost_cfg.get("hours_per_day", 8)
        rate = cost_cfg.get("hourly_rate", 150)
        multiplier = cost_cfg.get("complexity_multiplier", 1.5)
        
        kloc = foreground_loc / 1000
        days = kloc * days_per_kloc * multiplier
        hours = days * hours_per_day
        cost = hours * rate
        
        return {
            "total_loc": total_loc,
            "foreground_loc": foreground_loc,
            "estimated_days": round(days, 1),
            "estimated_hours": round(hours, 1),
            "estimated_cost_usd": round(cost, 2)
        }
    
    def _get_all_files(self):
        # Simplified - in production would scan repo
        return []
    
    def _get_primary_author(self, filepath, churn):
        # Simplified - would use git blame
        if churn:
            return list(churn.keys())[0] if churn else "unknown"
        return "unknown"
    
    def _estimate_coupling(self, filepath):
        # Simplified - would analyze imports/dependencies
        return 0.3
