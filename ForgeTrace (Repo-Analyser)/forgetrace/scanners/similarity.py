"""Similarity Scanner - Author: Peter"""
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Set
import hashlib

try:
    import tlsh  # type: ignore
    HAS_TLSH: bool = True
except ImportError:
    HAS_TLSH = False

try:
    import ppdeep as ssdeep  # type: ignore
    HAS_SSDEEP: bool = True
except ImportError:
    try:
        import ssdeep  # type: ignore
        HAS_SSDEEP = True
    except ImportError:
        HAS_SSDEEP = False


class SimilarityScanner:
    """Scanner for detecting code similarity and duplicates."""
    
    def __init__(self, repo_path: str | Path, config: Dict[str, Any]) -> None:
        self.repo_path = Path(repo_path)
        self.config = config
        self.shingle_size: int = config.get("similarity", {}).get("shingle_size", 5)
        
    def scan(self) -> Dict[str, Any]:
        """Scan repository for code similarity and duplicates."""
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
    
    def _get_source_files(self) -> List[Path]:
        """Get all source code files from repository."""
        exts = {".py", ".js", ".java", ".go", ".rb", ".php", ".ts", ".cpp", ".c", ".cs"}
        files: List[Path] = []
        for ext in exts:
            files.extend(self.repo_path.rglob(f"*{ext}"))
        # Filter out large files (> 1MB)
        return [f for f in files if f.stat().st_size < 1000000]
    
    def _compute_shingles(self, files: List[Path]) -> Dict[str, Set[str]]:
        """Compute n-gram shingles for each file."""
        shingles: Dict[str, Set[str]] = {}
        for f in files:
            try:
                content = f.read_text(errors="ignore")
                lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                if len(lines) >= self.shingle_size:
                    file_shingles: Set[str] = set()
                    for i in range(len(lines) - self.shingle_size + 1):
                        shingle = "\n".join(lines[i:i+self.shingle_size])
                        file_shingles.add(hashlib.md5(shingle.encode()).hexdigest())
                    shingles[str(f)] = file_shingles
            except Exception:
                pass
        return shingles
    
    def _find_duplicates(self, shingles: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
        """Find duplicate code based on Jaccard similarity."""
        duplicates: List[Dict[str, Any]] = []
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
    
    def _compute_fuzzy_hashes(self, files: List[Path]) -> Dict[str, Dict[str, str]]:
        """Compute fuzzy hashes (TLSH, ssdeep) for files."""
        hashes: Dict[str, Dict[str, str]] = {}
        for f in files[:100]:  # Limit for performance
            try:
                content = f.read_text(errors="ignore")
                h: Dict[str, str] = {}
                if HAS_TLSH and len(content) > 256:
                    h["tlsh"] = tlsh.hash(content.encode())  # type: ignore
                if HAS_SSDEEP:
                    h["ssdeep"] = ssdeep.hash(content)  # type: ignore
                if h:
                    hashes[str(f)] = h
            except Exception:
                pass
        return hashes
