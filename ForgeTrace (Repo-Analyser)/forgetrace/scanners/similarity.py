"""Similarity Scanner - Author: Peter"""
from pathlib import Path
from collections import defaultdict
import hashlib

try:
    import tlsh
    HAS_TLSH = True
except:
    HAS_TLSH = False

try:
    import ssdeep
    HAS_SSDEEP = True
except:
    HAS_SSDEEP = False

class SimilarityScanner:
    def __init__(self, repo_path, config):
        self.repo_path = Path(repo_path)
        self.config = config
        self.shingle_size = config.get("similarity", {}).get("shingle_size", 5)
        
    def scan(self):
        files = self._get_source_files()
        shingles = self._compute_shingles(files)
        duplicates = self._find_duplicates(shingles)
        fuzzy = self._compute_fuzzy_hashes(files)
        
        return {
            "total_files": len(files),
            "duplicates": duplicates,
            "fuzzy_hashes": fuzzy,
            "has_tlsh": HAS_TLSH,
            "has_ssdeep": HAS_SSDEEP
        }
    
    def _get_source_files(self):
        exts = {".py", ".js", ".java", ".go", ".rb", ".php", ".ts", ".cpp", ".c", ".cs"}
        files = []
        for ext in exts:
            files.extend(self.repo_path.rglob(f"*{ext}"))
        return [f for f in files if f.stat().st_size < 1000000]
    
    def _compute_shingles(self, files):
        shingles = {}
        for f in files:
            try:
                content = f.read_text(errors="ignore")
                lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                if len(lines) >= self.shingle_size:
                    file_shingles = set()
                    for i in range(len(lines) - self.shingle_size + 1):
                        shingle = "\n".join(lines[i:i+self.shingle_size])
                        file_shingles.add(hashlib.md5(shingle.encode()).hexdigest())
                    shingles[str(f)] = file_shingles
            except:
                pass
        return shingles
    
    def _find_duplicates(self, shingles):
        duplicates = []
        files = list(shingles.keys())
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                s1, s2 = shingles[files[i]], shingles[files[j]]
                if s1 and s2:
                    jaccard = len(s1 & s2) / len(s1 | s2)
                    if jaccard > 0.6:
                        duplicates.append({
                            "file1": files[i],
                            "file2": files[j],
                            "similarity": round(jaccard, 3)
                        })
        return duplicates
    
    def _compute_fuzzy_hashes(self, files):
        hashes = {}
        for f in files[:100]:  # Limit for performance
            try:
                content = f.read_text(errors="ignore")
                h = {}
                if HAS_TLSH and len(content) > 256:
                    h["tlsh"] = tlsh.hash(content.encode())
                if HAS_SSDEEP:
                    h["ssdeep"] = ssdeep.hash(content)
                if h:
                    hashes[str(f)] = h
            except:
                pass
        return hashes
