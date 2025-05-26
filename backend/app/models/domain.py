from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    registrar = Column(String(255), nullable=True)
    registration_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=False)
    renewal_cost = Column(Float, nullable=True)
    renewal_period_years = Column(Integer, default=1)
    
    # Contact information
    admin_email = Column(String(255), nullable=True)
    admin_phone = Column(String(50), nullable=True)
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    whois_last_updated = Column(DateTime, nullable=True)
    
    # Notes and tags
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    desktop_notifications = Column(Boolean, default=True)
    custom_reminder_days = Column(String(100), nullable=True)  # Comma-separated days
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notifications = relationship("Notification", back_populates="domain", cascade="all, delete-orphan")
    
    @property
    def days_until_expiration(self):
        """Calculate days until expiration"""
        if self.expiration_date:
            delta = self.expiration_date - datetime.utcnow()
            return delta.days
        return None
    
    @property
    def is_expired(self):
        """Check if domain is expired"""
        if self.expiration_date:
            return datetime.utcnow() > self.expiration_date
        return False
    
    @property
    def status(self):
        """Get domain status"""
        if not self.is_active:
            return "inactive"
        if self.is_expired:
            return "expired"
        
        days_left = self.days_until_expiration
        if days_left is None:
            return "unknown"
        elif days_left <= 0:
            return "expired"
        elif days_left <= 7:
            return "critical"
        elif days_left <= 30:
            return "warning"
        else:
            return "active"
    
    @property
    def tag_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        return []
    
    @tag_list.setter
    def tag_list(self, tags):
        """Set tags from a list"""
        if tags:
            self.tags = ",".join([tag.strip() for tag in tags if tag.strip()])
        else:
            self.tags = None
    
    @property
    def reminder_days_list(self):
        """Get custom reminder days as a list"""
        if self.custom_reminder_days:
            return [int(day.strip()) for day in self.custom_reminder_days.split(",") if day.strip().isdigit()]
        return []
    
    @reminder_days_list.setter
    def reminder_days_list(self, days):
        """Set reminder days from a list"""
        if days:
            self.custom_reminder_days = ",".join([str(day) for day in days])
        else:
            self.custom_reminder_days = None
    
    def __repr__(self):
        return f"<Domain(name='{self.name}', expires='{self.expiration_date}', status='{self.status}')>" 