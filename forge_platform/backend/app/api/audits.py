from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import subprocess
import os
import json
from pathlib import Path

from ..db.session import get_db
from ..models.user import User
from ..middleware.auth import get_current_user
from pydantic import BaseModel, HttpUrl

router = APIRouter()

class AuditCreate(BaseModel):
    repository: HttpUrl
    branch: Optional[str] = "main"

class AuditResponse(BaseModel):
    id: str
    repository: str
    status: str
    filesScanned: int
    createdAt: str
    completedAt: Optional[str] = None
    
class AuditListResponse(BaseModel):
    audits: List[AuditResponse]
    total: int

# Temporary in-memory storage (replace with database)
audits_store = {}

def run_audit_task(audit_id: str, repo_url: str, output_dir: str):
    """Background task to run ForgeTrace audit"""
    try:
        audits_store[audit_id]['status'] = 'processing'
        
        # Run ForgeTrace CLI
        result = subprocess.run(
            ['forgetrace', 'audit', repo_url, '--out', output_dir],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Parse audit results
            audit_json = Path(output_dir) / 'audit.json'
            if audit_json.exists():
                with open(audit_json) as f:
                    data = json.load(f)
                    audits_store[audit_id].update({
                        'status': 'completed',
                        'filesScanned': data.get('total_files', 0),
                        'completedAt': datetime.utcnow().isoformat()
                    })
            else:
                audits_store[audit_id]['status'] = 'failed'
        else:
            audits_store[audit_id]['status'] = 'failed'
            audits_store[audit_id]['error'] = result.stderr
            
    except subprocess.TimeoutExpired:
        audits_store[audit_id]['status'] = 'failed'
        audits_store[audit_id]['error'] = 'Audit timeout'
    except Exception as e:
        audits_store[audit_id]['status'] = 'failed'
        audits_store[audit_id]['error'] = str(e)

@router.post("/audits", response_model=AuditResponse)
async def submit_audit(
    audit: AuditCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Submit a new audit"""
    audit_id = f"audit_{datetime.utcnow().timestamp()}"
    output_dir = f"/tmp/forgetrace_audits/{audit_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create audit record
    audit_record = {
        'id': audit_id,
        'repository': str(audit.repository),
        'status': 'pending',
        'filesScanned': 0,
        'createdAt': datetime.utcnow().isoformat(),
        'userId': current_user.id,
        'outputDir': output_dir
    }
    audits_store[audit_id] = audit_record
    
    # Queue background task
    background_tasks.add_task(run_audit_task, audit_id, str(audit.repository), output_dir)
    
    return AuditResponse(**audit_record)

@router.get("/audits", response_model=AuditListResponse)
async def list_audits(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """List all audits for current user"""
    user_audits = [
        AuditResponse(**audit) 
        for audit in audits_store.values() 
        if audit.get('userId') == current_user.id
    ]
    
    # Sort by creation date (newest first)
    user_audits.sort(key=lambda x: x.createdAt, reverse=True)
    
    return AuditListResponse(
        audits=user_audits[skip:skip+limit],
        total=len(user_audits)
    )

@router.get("/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get audit details"""
    audit = audits_store.get(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AuditResponse(**audit)

@router.get("/audits/{audit_id}/report")
async def download_report(
    audit_id: str,
    format: str = "json",
    current_user: User = Depends(get_current_user)
):
    """Download audit report"""
    from fastapi.responses import FileResponse
    
    audit = audits_store.get(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if audit['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Audit not completed")
    
    output_dir = Path(audit['outputDir'])
    
    if format == "json":
        file_path = output_dir / "audit.json"
    elif format == "pdf":
        file_path = output_dir / "report.pdf"
    elif format == "html":
        file_path = output_dir / "report.html"
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=str(file_path),
        filename=f"audit-{audit_id}.{format}",
        media_type="application/octet-stream"
    )

@router.delete("/audits/{audit_id}")
async def delete_audit(
    audit_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an audit"""
    audit = audits_store.get(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.get('userId') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove from store
    del audits_store[audit_id]
    
    # Clean up files
    import shutil
    output_dir = audit.get('outputDir')
    if output_dir and os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    return {"message": "Audit deleted"}
