from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

from ..models.domain import Domain
from ..models.notification import Notification, NotificationType, NotificationStatus
from .whois_service import WhoisService

load_dotenv()
logger = logging.getLogger(__name__)

class DomainService:
    def __init__(self, db: Session):
        self.db = db
        self.whois_service = WhoisService()
        self.default_reminder_days = [
            int(day.strip()) 
            for day in os.getenv("DEFAULT_REMINDER_DAYS", "90,30,14,7,3,1").split(",")
            if day.strip().isdigit()
        ]
    
    async def create_domain(
        self,
        name: str,
        expiration_date: datetime,
        registrar: Optional[str] = None,
        **kwargs
    ) -> Domain:
        """Create a new domain entry"""
        try:
            # Clean domain name
            name = name.lower().strip()
            if name.startswith(('http://', 'https://')):
                name = name.split('://')[1]
            if '/' in name:
                name = name.split('/')[0]
            
            # Check if domain already exists
            existing_domain = self.db.query(Domain).filter(Domain.name == name).first()
            if existing_domain:
                raise ValueError(f"Domain {name} already exists")
            
            # Create domain object
            domain_data = {
                'name': name,
                'expiration_date': expiration_date,
                'registrar': registrar,
                'last_checked': datetime.utcnow(),
                **kwargs
            }
            
            domain = Domain(**domain_data)
            self.db.add(domain)
            self.db.commit()
            self.db.refresh(domain)
            
            logger.info(f"Created domain: {name}")
            return domain
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create domain {name}: {str(e)}")
            raise e
    
    def get_domain(self, domain_id: int) -> Optional[Domain]:
        """Get domain by ID"""
        return self.db.query(Domain).filter(Domain.id == domain_id).first()
    
    def get_domain_by_name(self, name: str) -> Optional[Domain]:
        """Get domain by name"""
        return self.db.query(Domain).filter(Domain.name == name.lower()).first()
    
    def get_all_domains(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Domain]:
        """Get all domains with optional filtering"""
        query = self.db.query(Domain)
        
        # Apply search filter
        if search:
            query = query.filter(Domain.name.contains(search.lower()))
        
        # Apply status filter
        if status_filter:
            now = datetime.utcnow()
            if status_filter == "expired":
                query = query.filter(Domain.expiration_date < now)
            elif status_filter == "critical":
                query = query.filter(
                    and_(
                        Domain.expiration_date >= now,
                        Domain.expiration_date <= now + timedelta(days=7)
                    )
                )
            elif status_filter == "warning":
                query = query.filter(
                    and_(
                        Domain.expiration_date > now + timedelta(days=7),
                        Domain.expiration_date <= now + timedelta(days=30)
                    )
                )
            elif status_filter == "active":
                query = query.filter(Domain.expiration_date > now + timedelta(days=30))
            elif status_filter == "inactive":
                query = query.filter(Domain.is_active == False)
        
        return query.offset(skip).limit(limit).all()
    
    async def update_domain(self, domain_id: int, **kwargs) -> Optional[Domain]:
        """Update domain information"""
        try:
            domain = self.get_domain(domain_id)
            if not domain:
                return None
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(domain, key):
                    setattr(domain, key, value)
            
            domain.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(domain)
            
            logger.info(f"Updated domain: {domain.name}")
            return domain
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update domain {domain_id}: {str(e)}")
            raise e
    
    def delete_domain(self, domain_id: int) -> bool:
        """Delete domain"""
        try:
            domain = self.get_domain(domain_id)
            if not domain:
                return False
            
            self.db.delete(domain)
            self.db.commit()
            
            logger.info(f"Deleted domain: {domain.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete domain {domain_id}: {str(e)}")
            raise e
    
    async def refresh_whois_data(self, domain_id: int) -> Optional[Domain]:
        """Refresh WHOIS data for a domain"""
        try:
            domain = self.get_domain(domain_id)
            if not domain:
                return None
            
            whois_data = await self.whois_service.get_domain_info(domain.name)
            if not whois_data or 'error' in whois_data:
                logger.warning(f"Failed to fetch WHOIS data for {domain.name}")
                return domain
            
            # Update domain with WHOIS data
            updates = {}
            if 'expiration_date' in whois_data and whois_data['expiration_date']:
                updates['expiration_date'] = whois_data['expiration_date']
            if 'registrar' in whois_data and whois_data['registrar']:
                updates['registrar'] = whois_data['registrar']
            if 'registration_date' in whois_data and whois_data['registration_date']:
                updates['registration_date'] = whois_data['registration_date']
            if 'admin_email' in whois_data and whois_data['admin_email']:
                updates['admin_email'] = whois_data['admin_email']
            
            updates['whois_last_updated'] = datetime.utcnow()
            updates['last_checked'] = datetime.utcnow()
            
            return await self.update_domain(domain_id, **updates)
            
        except Exception as e:
            logger.error(f"Failed to refresh WHOIS data for domain {domain_id}: {str(e)}")
            raise e
    
    def get_expiring_domains(self, days_ahead: int = 90) -> List[Domain]:
        """Get domains expiring within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return self.db.query(Domain).filter(
            and_(
                Domain.is_active == True,
                Domain.expiration_date <= cutoff_date
            )
        ).order_by(Domain.expiration_date).all()
    
    def get_domain_statistics(self) -> Dict[str, Any]:
        """Get domain statistics"""
        now = datetime.utcnow()
        
        total_domains = self.db.query(Domain).filter(Domain.is_active == True).count()
        expired_domains = self.db.query(Domain).filter(
            and_(Domain.is_active == True, Domain.expiration_date < now)
        ).count()
        critical_domains = self.db.query(Domain).filter(
            and_(
                Domain.is_active == True,
                Domain.expiration_date >= now,
                Domain.expiration_date <= now + timedelta(days=7)
            )
        ).count()
        warning_domains = self.db.query(Domain).filter(
            and_(
                Domain.is_active == True,
                Domain.expiration_date > now + timedelta(days=7),
                Domain.expiration_date <= now + timedelta(days=30)
            )
        ).count()
        
        return {
            'total_domains': total_domains,
            'expired_domains': expired_domains,
            'critical_domains': critical_domains,
            'warning_domains': warning_domains,
            'active_domains': total_domains - expired_domains
        }
    
    def get_domains_needing_check(self, hours_since_last_check: int = 24) -> List[Domain]:
        """Get domains that need WHOIS checking"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_since_last_check)
        return self.db.query(Domain).filter(
            and_(
                Domain.is_active == True,
                or_(
                    Domain.last_checked < cutoff_time,
                    Domain.last_checked.is_(None)
                )
            )
        ).all() 