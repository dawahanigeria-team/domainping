from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

from ..models.database import engine
from ..models.domain import Domain
from ..models.notification import Notification, NotificationStatus, NotificationType
from ..services.domain_service import DomainService
from ..services.notification_service import NotificationService

load_dotenv()
logger = logging.getLogger(__name__)

class DomainScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.notification_service = NotificationService()
        
        # Configuration
        self.check_interval_hours = int(os.getenv("CHECK_INTERVAL_HOURS", 24))
        self.notification_time_hour = int(os.getenv("NOTIFICATION_TIME_HOUR", 9))
        self.notification_time_minute = int(os.getenv("NOTIFICATION_TIME_MINUTE", 0))
    
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule domain checks (every X hours)
            self.scheduler.add_job(
                self.check_domains_task,
                'interval',
                hours=self.check_interval_hours,
                id='check_domains',
                name='Check Domain Status',
                replace_existing=True
            )
            
            # Schedule notification processing (every hour)
            self.scheduler.add_job(
                self.process_notifications_task,
                'interval',
                hours=1,
                id='process_notifications',
                name='Process Pending Notifications',
                replace_existing=True
            )
            
            # Schedule daily summary (at configured time)
            self.scheduler.add_job(
                self.daily_summary_task,
                CronTrigger(
                    hour=self.notification_time_hour,
                    minute=self.notification_time_minute
                ),
                id='daily_summary',
                name='Daily Domain Summary',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("Domain scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise e
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Domain scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
    
    async def check_domains_task(self):
        """Background task to check domain status and update WHOIS data"""
        logger.info("Starting domain check task...")
        
        db = self.SessionLocal()
        try:
            domain_service = DomainService(db)
            
            # Get domains that need checking
            domains_to_check = domain_service.get_domains_needing_check(
                hours_since_last_check=self.check_interval_hours
            )
            
            logger.info(f"Found {len(domains_to_check)} domains to check")
            
            for domain in domains_to_check:
                try:
                    logger.info(f"Checking domain: {domain.name}")
                    await domain_service.refresh_whois_data(domain.id)
                    
                except Exception as e:
                    logger.error(f"Failed to check domain {domain.name}: {str(e)}")
                    continue
            
            logger.info("Domain check task completed")
            
        except Exception as e:
            logger.error(f"Domain check task failed: {str(e)}")
        finally:
            db.close()
    
    async def process_notifications_task(self):
        """Background task to process pending notifications"""
        logger.info("Starting notification processing task...")
        
        db = self.SessionLocal()
        try:
            # Get pending notifications that are due
            now = datetime.utcnow()
            pending_notifications = db.query(Notification).filter(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_at <= now
            ).all()
            
            logger.info(f"Found {len(pending_notifications)} pending notifications")
            
            for notification in pending_notifications:
                try:
                    await self._send_notification(notification, db)
                except Exception as e:
                    logger.error(f"Failed to send notification {notification.id}: {str(e)}")
                    notification.mark_failed(str(e))
                    db.commit()
            
            # Retry failed notifications
            failed_notifications = db.query(Notification).filter(
                Notification.status == NotificationStatus.FAILED,
                Notification.retry_count < Notification.max_retries
            ).all()
            
            logger.info(f"Found {len(failed_notifications)} failed notifications to retry")
            
            for notification in failed_notifications:
                try:
                    await self._send_notification(notification, db)
                except Exception as e:
                    logger.error(f"Failed to retry notification {notification.id}: {str(e)}")
                    notification.mark_failed(str(e))
                    db.commit()
            
            logger.info("Notification processing task completed")
            
        except Exception as e:
            logger.error(f"Notification processing task failed: {str(e)}")
        finally:
            db.close()
    
    async def daily_summary_task(self):
        """Background task to send daily domain summary"""
        logger.info("Starting daily summary task...")
        
        db = self.SessionLocal()
        try:
            domain_service = DomainService(db)
            
            # Get domain statistics
            stats = domain_service.get_domain_statistics()
            
            # Get expiring domains (next 30 days)
            expiring_domains = domain_service.get_expiring_domains(days_ahead=30)
            
            if stats['expired_domains'] > 0 or stats['critical_domains'] > 0 or stats['warning_domains'] > 0:
                # Send summary notification to admin
                # This would typically be sent to a configured admin email
                logger.info(f"Daily summary: {stats}")
                logger.info(f"Expiring domains in next 30 days: {len(expiring_domains)}")
            
            logger.info("Daily summary task completed")
            
        except Exception as e:
            logger.error(f"Daily summary task failed: {str(e)}")
        finally:
            db.close()
    
    async def _send_notification(self, notification: Notification, db):
        """Send a single notification"""
        try:
            domain = notification.domain
            if not domain:
                notification.mark_failed("Domain not found")
                db.commit()
                return
            
            success = False
            
            if notification.type == NotificationType.EMAIL:
                success = await self.notification_service.send_email_notification(
                    to_email=notification.recipient,
                    domain_name=domain.name,
                    expiration_date=domain.expiration_date,
                    days_until_expiration=notification.days_before_expiration,
                    registrar=domain.registrar,
                    renewal_cost=domain.renewal_cost,
                    notes=domain.notes
                )
            
            elif notification.type == NotificationType.SMS:
                success = await self.notification_service.send_sms_notification(
                    to_phone=notification.recipient,
                    domain_name=domain.name,
                    expiration_date=domain.expiration_date,
                    days_until_expiration=notification.days_before_expiration
                )
            
            elif notification.type == NotificationType.DESKTOP:
                success = await self.notification_service.send_desktop_notification(
                    domain_name=domain.name,
                    days_until_expiration=notification.days_before_expiration
                )
            
            if success:
                notification.mark_sent()
                logger.info(f"Sent {notification.type.value} notification for domain {domain.name}")
            else:
                notification.mark_failed("Notification service returned failure")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {str(e)}")
            raise e

# Global scheduler instance
scheduler = DomainScheduler() 