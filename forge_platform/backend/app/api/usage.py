from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from ..db.session import get_db
from ..models.user import User
from ..middleware.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UsageHistoryItem(BaseModel):
    date: str
    count: int

class UsageStats(BaseModel):
    filesScanned: int
    apiRequests: int
    storageUsed: int
    monthlyLimit: int
    tier: str
    usageHistory: List[UsageHistoryItem]

@router.get("/usage/stats", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
):
    """Get usage statistics for current user"""
    # TODO: Replace with real database queries
    
    # Calculate monthly usage
    files_scanned = 1247  # Query from audits
    api_requests = 89     # Query from API logs
    storage_used = 1024   # Query from file storage
    
    # Get tier limits
    tier_limits = {
        'free': 1000,
        'professional': 50000,
        'enterprise': 1000000
    }
    
    tier = current_user.subscription_tier or 'free'
    monthly_limit = tier_limits.get(tier, 1000)
    
    # Generate usage history (last 4 months)
    history = []
    for i in range(4):
        date = (datetime.utcnow() - timedelta(days=30*i)).strftime('%Y-%m')
        count = files_scanned - (i * 200)  # Mock declining usage
        history.append(UsageHistoryItem(date=date, count=max(count, 0)))
    
    history.reverse()
    
    return UsageStats(
        filesScanned=files_scanned,
        apiRequests=api_requests,
        storageUsed=storage_used,
        monthlyLimit=monthly_limit,
        tier=tier,
        usageHistory=history
    )

@router.get("/usage/history")
async def get_usage_history(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get detailed usage history"""
    # TODO: Implement detailed daily usage tracking
    return {
        "period": f"last_{days}_days",
        "data": []
    }
