from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

class NotificationType(PyEnum):
    EMAIL = "email"
    SMS = "sms"
    DESKTOP = "desktop"

class NotificationStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    
    # Notification details
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    days_before_expiration = Column(Integer, nullable=False)
    
    # Message content
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    recipient = Column(String(255), nullable=False)  # Email or phone number
    
    # Timing
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="notifications")
    
    @property
    def is_due(self):
        """Check if notification is due to be sent"""
        return (
            self.status == NotificationStatus.PENDING and
            datetime.utcnow() >= self.scheduled_at
        )
    
    @property
    def can_retry(self):
        """Check if notification can be retried"""
        return (
            self.status == NotificationStatus.FAILED and
            self.retry_count < self.max_retries
        )
    
    def mark_sent(self):
        """Mark notification as sent"""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
        self.error_message = None
    
    def mark_failed(self, error_message: str):
        """Mark notification as failed"""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
    
    def mark_cancelled(self):
        """Mark notification as cancelled"""
        self.status = NotificationStatus.CANCELLED
    
    def __repr__(self):
        return f"<Notification(domain='{self.domain.name if self.domain else 'Unknown'}', type='{self.type.value}', status='{self.status.value}')>" 