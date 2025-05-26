from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..models.database import get_db
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

class TestEmailRequest(BaseModel):
    email: str

class TestSMSRequest(BaseModel):
    phone: str

@router.post("/test-email")
async def test_email_configuration(
    request: TestEmailRequest,
    db: Session = Depends(get_db)
):
    """Test email configuration"""
    try:
        notification_service = NotificationService()
        success = await notification_service.test_email_configuration()
        if success:
            return {"message": "Email configuration test successful"}
        else:
            raise HTTPException(status_code=500, detail="Email configuration test failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")

@router.post("/test-sms")
async def test_sms_configuration(
    request: TestSMSRequest,
    db: Session = Depends(get_db)
):
    """Test SMS configuration"""
    try:
        notification_service = NotificationService()
        success = await notification_service.test_sms_configuration(request.phone)
        if success:
            return {"message": "SMS configuration test successful"}
        else:
            raise HTTPException(status_code=500, detail="SMS configuration test failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS test failed: {str(e)}")

@router.post("/test-desktop")
async def test_desktop_notification():
    """Test desktop notification"""
    try:
        notification_service = NotificationService()
        success = await notification_service.send_desktop_notification(
            domain_name="test-domain.com",
            days_until_expiration=30
        )
        if success:
            return {"message": "Desktop notification test successful"}
        else:
            raise HTTPException(status_code=500, detail="Desktop notification test failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Desktop notification test failed: {str(e)}") 