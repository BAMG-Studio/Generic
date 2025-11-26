"""
Scanner Service - Integrates ForgeTrace CLI with Platform API
"""
import subprocess
import json
import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import tempfile
import shutil

from ..core.config import settings
from ..models.scan import Scan, ScanStatus
from sqlalchemy.ext.asyncio import AsyncSession
from .s3_storage import s3_storage


class ScannerService:
    """Service for executing ForgeTrace scans"""
    
    def __init__(self):
        # Resolve project root safely in container (shallow path) or via env override
        env_root = os.getenv("FORGETRACE_PROJECT_ROOT")
        if env_root:
            self.project_root = Path(env_root).resolve()
        else:
            resolved = Path(__file__).resolve()
            # /app/app/services/scanner.py -> parents[0]=services, [1]=app, [2]=/app
            # Clamp to the highest available parent to avoid IndexError in thin images.
            self.project_root = resolved.parents[2] if len(resolved.parents) > 2 else resolved.parent

        self.forge_cli = self.project_root / "forgetrace"
        self.config_path = self.project_root / "config.yaml"
        
    async def execute_scan(
        self,
        scan_id: str,
        repository_url: str,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Execute a ForgeTrace scan for a repository"""
        
        # Create temporary directory for clone
        temp_dir = Path(tempfile.mkdtemp(prefix="forge_scan_"))
        
        try:
            # Update scan status to running
            if db:
                await self._update_scan_status(
                    db,
                    scan_id,
                    ScanStatus.RUNNING,
                    started_at=datetime.now(timezone.utc).isoformat()
                )
            
            # Clone repository
            clone_result = await self._clone_repository(repository_url, temp_dir, branch)
            if not clone_result["success"]:
                raise Exception(f"Clone failed: {clone_result['error']}")
            
            # Checkout specific commit if provided
            if commit_sha:
                await self._checkout_commit(temp_dir, commit_sha)
            
            # Run ForgeTrace scan
            scan_result = await self._run_forgetrace_scan(temp_dir)
            
            # Update scan with results
            if db:
                await self._update_scan_results(db, scan_id, scan_result)
            
            return scan_result
            
        except Exception as e:
            # Update scan status to failed
            if db:
                await self._update_scan_status(
                    db, 
                    scan_id, 
                    ScanStatus.FAILED,
                    error_message=str(e),
                    completed_at=datetime.now(timezone.utc).isoformat()
                )
            raise
        finally:
            # Cleanup temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def _clone_repository(self, url: str, target_dir: Path, branch: Optional[str] = None) -> Dict[str, Any]:
        """Clone a git repository"""
        try:
            cmd = ["git", "clone"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([url, str(target_dir)])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {"success": True, "path": str(target_dir)}
            else:
                return {
                    "success": False,
                    "error": stderr.decode() if stderr else "Clone failed"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _checkout_commit(self, repo_dir: Path, commit_sha: str):
        """Checkout a specific commit"""
        process = await asyncio.create_subprocess_exec(
            "git", "checkout", commit_sha,
            cwd=repo_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Failed to checkout commit {commit_sha}")
    
    async def _run_forgetrace_scan(self, repo_dir: Path) -> Dict[str, Any]:
        """Run ForgeTrace CLI scan on the repository"""
        start_time = datetime.now(timezone.utc)
        output_dir = repo_dir / "forgetrace_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        config_args = []
        if self.config_path.exists():
            config_args = ["--config", str(self.config_path)]
        
        # Run ForgeTrace audit command
        process = await asyncio.create_subprocess_exec(
            "python", "-m", "forgetrace",
            "audit",
            str(repo_dir),
            "--out", str(output_dir),
            *config_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_root
        )
        
        stdout_data, stderr_data = await process.communicate()
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        if process.returncode != 0:
            raise Exception(f"ForgeTrace scan failed: {stderr_data.decode() if stderr_data else 'Unknown error'}")
        
        # Read results
        results_file = output_dir / "audit.json"
        if not results_file.exists():
            results_file = repo_dir / "audit_results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                results = json.load(f)
        else:
            # Parse from stdout if no file
            results = json.loads(stdout_data.decode())
        
        # Extract summary metrics
        summary = self._extract_summary(results)
        
        return {
            "success": True,
            "duration_seconds": int(duration),
            "results": results,
            "summary": summary,
            "completed_at": end_time.isoformat()
        }
    
    def _extract_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary metrics from scan results"""
        summary = {
            "total_files": 0,
            "foreground_count": 0,
            "third_party_count": 0,
            "background_count": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
        }
        
        # Count files by classification
        if "files" in results:
            for file_result in results["files"]:
                summary["total_files"] += 1
                classification = file_result.get("classification", "unknown")
                
                if classification == "foreground":
                    summary["foreground_count"] += 1
                elif classification == "third_party":
                    summary["third_party_count"] += 1
                elif classification == "background":
                    summary["background_count"] += 1
        
        # Count issues by severity
        if "issues" in results:
            for issue in results["issues"]:
                severity = issue.get("severity", "low").lower()
                if severity == "critical":
                    summary["critical_issues"] += 1
                elif severity == "high":
                    summary["high_issues"] += 1
                elif severity == "medium":
                    summary["medium_issues"] += 1
                else:
                    summary["low_issues"] += 1
        
        return summary
    
    async def _update_scan_status(
        self,
        db: AsyncSession,
        scan_id: str,
        status: ScanStatus,
        **kwargs: Any
    ) -> None:
        """Update scan status in database"""
        from sqlalchemy import update
        
        update_data: Dict[str, Any] = {"status": status}
        update_data.update(kwargs)
        
        stmt = (
            update(Scan)
            .where(Scan.id == scan_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()
    
    async def _update_scan_results(
        self,
        db: AsyncSession,
        scan_id: str,
        scan_result: Dict[str, Any]
    ):
        """Update scan with results and upload to S3 if enabled"""
        from sqlalchemy import select, update
        
        # Get scan with tenant_id
        result = await db.execute(
            select(Scan).where(Scan.id == scan_id)
        )
        scan = result.scalar_one_or_none()
        
        if not scan:
            return
        
        summary = scan_result.get("summary", {})
        
        # Upload to S3 if enabled
        s3_url = None
        if s3_storage.is_enabled():
            s3_url = await s3_storage.upload_scan_result(
                tenant_id=str(scan.tenant_id),
                scan_id=scan_id,
                result_data=scan_result.get("results", {})
            )
        
        # Build update data
        update_data: Dict[str, Any] = {
            "status": ScanStatus.COMPLETED,
            "completed_at": scan_result.get("completed_at"),
            "duration_seconds": scan_result.get("duration_seconds"),
            "total_files": summary.get("total_files", 0),
            "foreground_count": summary.get("foreground_count", 0),
            "third_party_count": summary.get("third_party_count", 0),
            "background_count": summary.get("background_count", 0),
            "critical_issues": summary.get("critical_issues", 0),
            "high_issues": summary.get("high_issues", 0),
            "medium_issues": summary.get("medium_issues", 0),
            "low_issues": summary.get("low_issues", 0),
            "scan_metadata": scan_result.get("results", {})
        }
        
        if s3_url:
            update_data["results_url"] = s3_url
        
        stmt = (
            update(Scan)
            .where(Scan.id == scan_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()


# Global instance
scanner_service = ScannerService()
