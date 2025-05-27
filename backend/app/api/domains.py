from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.database import get_db
from ..services.domain_service import DomainService

router = APIRouter(prefix="/domains", tags=["domains"])

# Pydantic models for request/response
class DomainCreate(BaseModel):
    name: str = Field(..., description="Domain name")
    expiration_date: datetime = Field(..., description="Domain expiration date")
    registrar: Optional[str] = Field(None, description="Domain registrar")
    auto_renew: bool = Field(False, description="Auto-renewal enabled")
    renewal_cost: Optional[float] = Field(None, description="Renewal cost")
    renewal_period_years: int = Field(1, description="Renewal period in years")
    admin_email: Optional[str] = Field(None, description="Admin email")
    admin_phone: Optional[str] = Field(None, description="Admin phone")
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    email_notifications: bool = Field(True, description="Enable email notifications")
    sms_notifications: bool = Field(False, description="Enable SMS notifications")
    desktop_notifications: bool = Field(True, description="Enable desktop notifications")
    custom_reminder_days: Optional[str] = Field(None, description="Custom reminder days")

class DomainUpdate(BaseModel):
    name: Optional[str] = None
    expiration_date: Optional[datetime] = None
    registrar: Optional[str] = None
    auto_renew: Optional[bool] = None
    renewal_cost: Optional[float] = None
    renewal_period_years: Optional[int] = None
    admin_email: Optional[str] = None
    admin_phone: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    desktop_notifications: Optional[bool] = None
    custom_reminder_days: Optional[str] = None
    is_active: Optional[bool] = None

class DomainResponse(BaseModel):
    id: int
    name: str
    registrar: Optional[str]
    registration_date: Optional[datetime]
    expiration_date: datetime
    auto_renew: bool
    renewal_cost: Optional[float]
    renewal_period_years: int
    admin_email: Optional[str]
    admin_phone: Optional[str]
    is_active: bool
    last_checked: Optional[datetime]
    whois_last_updated: Optional[datetime]
    notes: Optional[str]
    tags: Optional[str]
    email_notifications: bool
    sms_notifications: bool
    desktop_notifications: bool
    custom_reminder_days: Optional[str]
    created_at: datetime
    updated_at: datetime
    days_until_expiration: Optional[int]
    is_expired: bool
    status: str

    class Config:
        from_attributes = True

@router.post("/", response_model=DomainResponse)
async def create_domain(
    domain: DomainCreate,
    db: Session = Depends(get_db)
):
    """Create a new domain"""
    try:
        domain_service = DomainService(db)
        created_domain = await domain_service.create_domain(**domain.dict())
        return created_domain
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create domain: {str(e)}")

@router.get("/", response_model=List[DomainResponse])
async def get_domains(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status: active, warning, critical, expired, inactive"),
    search: Optional[str] = Query(None, description="Search term for domain name"),
    db: Session = Depends(get_db)
):
    """Get all domains with optional filtering"""
    domain_service = DomainService(db)
    domains = domain_service.get_all_domains(
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        search=search
    )
    return domains

@router.get("/statistics")
async def get_domain_statistics(db: Session = Depends(get_db)):
    """Get domain statistics"""
    domain_service = DomainService(db)
    stats = domain_service.get_domain_statistics()
    return stats

@router.get("/expiring")
async def get_expiring_domains(
    days_ahead: int = Query(90, ge=1, le=365, description="Number of days to look ahead"),
    db: Session = Depends(get_db)
):
    """Get domains expiring within specified days"""
    domain_service = DomainService(db)
    domains = domain_service.get_expiring_domains(days_ahead=days_ahead)
    return domains

@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(domain_id: int, db: Session = Depends(get_db)):
    """Get domain by ID"""
    domain_service = DomainService(db)
    domain = domain_service.get_domain(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    domain_update: DomainUpdate,
    db: Session = Depends(get_db)
):
    """Update domain"""
    try:
        domain_service = DomainService(db)
        # Filter out None values
        update_data = {k: v for k, v in domain_update.dict().items() if v is not None}
        updated_domain = await domain_service.update_domain(domain_id, **update_data)
        if not updated_domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        return updated_domain
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update domain: {str(e)}")

@router.delete("/{domain_id}")
async def delete_domain(domain_id: int, db: Session = Depends(get_db)):
    """Delete domain"""
    try:
        domain_service = DomainService(db)
        success = domain_service.delete_domain(domain_id)
        if not success:
            raise HTTPException(status_code=404, detail="Domain not found")
        return {"message": "Domain deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete domain: {str(e)}")

@router.post("/{domain_id}/refresh-whois", response_model=DomainResponse)
async def refresh_whois_data(domain_id: int, db: Session = Depends(get_db)):
    """Refresh WHOIS data for domain"""
    try:
        domain_service = DomainService(db)
        updated_domain = await domain_service.refresh_whois_data(domain_id)
        if not updated_domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        return updated_domain
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh WHOIS data: {str(e)}")

@router.post("/check-whois")
async def check_whois_availability(domain_name: str, db: Session = Depends(get_db)):
    """Check if WHOIS data can be fetched for a domain"""
    try:
        domain_service = DomainService(db)
        whois_data = await domain_service.whois_service.get_domain_info(domain_name)
        
        if whois_data and 'error' not in whois_data:
            return {
                "success": True,
                "message": "WHOIS data available",
                "data": whois_data
            }
        elif whois_data and 'error' in whois_data:
            return {
                "success": False,
                "message": f"WHOIS lookup failed: {whois_data['error']}",
                "error_type": whois_data.get('error_type', 'unknown'),
                "manual_entry_required": True
            }
        else:
            return {
                "success": False,
                "message": "WHOIS lookup returned no data",
                "manual_entry_required": True
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"WHOIS check failed: {str(e)}",
            "manual_entry_required": True
        }

@router.get("/name/{domain_name}", response_model=DomainResponse)
async def get_domain_by_name(domain_name: str, db: Session = Depends(get_db)):
    """Get domain by name"""
    domain_service = DomainService(db)
    domain = domain_service.get_domain_by_name(domain_name)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain 