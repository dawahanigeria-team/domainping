import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from twilio.rest import Client
from plyer import notification
import jinja2

load_dotenv()

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "DomainPing")
        
        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio client if credentials are provided
        self.twilio_client = None
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                logger.warning(f"Failed to initialize Twilio client: {str(e)}")
        
        # Template environment
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_templates())
        )
    
    def _get_templates(self) -> dict:
        """Get email and SMS templates"""
        return {
            'email_reminder': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .alert { padding: 15px; border-radius: 5px; margin: 20px 0; }
        .alert-warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-danger { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .domain-info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 DomainPing Alert</h1>
            <p>Your domain <strong>{{ domain_name }}</strong> needs attention!</p>
        </div>
        
        {% if days_until_expiration <= 0 %}
        <div class="alert alert-danger">
            <strong>⚠️ EXPIRED:</strong> Your domain has expired!
        </div>
        {% elif days_until_expiration <= 7 %}
        <div class="alert alert-danger">
            <strong>🔥 CRITICAL:</strong> Your domain expires in {{ days_until_expiration }} day(s)!
        </div>
        {% else %}
        <div class="alert alert-warning">
            <strong>⏰ REMINDER:</strong> Your domain expires in {{ days_until_expiration }} day(s).
        </div>
        {% endif %}
        
        <div class="domain-info">
            <h3>Domain Details:</h3>
            <ul>
                <li><strong>Domain:</strong> {{ domain_name }}</li>
                <li><strong>Expiration Date:</strong> {{ expiration_date.strftime('%B %d, %Y') }}</li>
                {% if registrar %}<li><strong>Registrar:</strong> {{ registrar }}</li>{% endif %}
                {% if renewal_cost %}<li><strong>Estimated Renewal Cost:</strong> ${{ renewal_cost }}</li>{% endif %}
            </ul>
        </div>
        
        <h3>What you need to do:</h3>
        <ol>
            <li>Log into your domain registrar's website</li>
            <li>Navigate to domain management</li>
            <li>Renew your domain for at least 1 year</li>
            <li>Update the expiration date in your DomainPing system</li>
        </ol>
        
        {% if notes %}
        <div class="domain-info">
            <h3>Notes:</h3>
            <p>{{ notes }}</p>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>This is an automated reminder from your DomainPing system.</p>
            <p>Never lose a domain again! 🛡️</p>
        </div>
    </div>
</body>
</html>
            ''',
            'sms_reminder': '''
🚨 Domain Alert: {{ domain_name }} expires in {{ days_until_expiration }} day(s) on {{ expiration_date.strftime('%m/%d/%Y') }}. Renew now to avoid losing your domain! 
            ''',
            'desktop_reminder': '''
Domain {{ domain_name }} expires in {{ days_until_expiration }} day(s)!
            '''
        }
    
    async def send_email_notification(
        self, 
        to_email: str, 
        domain_name: str, 
        expiration_date: datetime,
        days_until_expiration: int,
        registrar: Optional[str] = None,
        renewal_cost: Optional[float] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Send email notification about domain expiration
        
        Args:
            to_email: Recipient email address
            domain_name: Domain name
            expiration_date: Domain expiration date
            days_until_expiration: Days until expiration
            registrar: Domain registrar
            renewal_cost: Estimated renewal cost
            notes: Additional notes
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
                logger.error("Email configuration is incomplete")
                return False
            
            # Prepare template data
            template_data = {
                'domain_name': domain_name,
                'expiration_date': expiration_date,
                'days_until_expiration': days_until_expiration,
                'registrar': registrar,
                'renewal_cost': renewal_cost,
                'notes': notes
            }
            
            # Render email content
            template = self.template_env.get_template('email_reminder')
            html_content = template.render(**template_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Domain Renewal Alert: {domain_name} expires in {days_until_expiration} day(s)"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent successfully to {to_email} for domain {domain_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    async def send_sms_notification(
        self,
        to_phone: str,
        domain_name: str,
        expiration_date: datetime,
        days_until_expiration: int
    ) -> bool:
        """
        Send SMS notification about domain expiration
        
        Args:
            to_phone: Recipient phone number
            domain_name: Domain name
            expiration_date: Domain expiration date
            days_until_expiration: Days until expiration
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        try:
            if not self.twilio_client:
                logger.error("Twilio client not initialized")
                return False
            
            # Prepare template data
            template_data = {
                'domain_name': domain_name,
                'expiration_date': expiration_date,
                'days_until_expiration': days_until_expiration
            }
            
            # Render SMS content
            template = self.template_env.get_template('sms_reminder')
            message_content = template.render(**template_data)
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=message_content,
                from_=self.twilio_phone_number,
                to=to_phone
            )
            
            logger.info(f"SMS notification sent successfully to {to_phone} for domain {domain_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False
    
    async def send_desktop_notification(
        self,
        domain_name: str,
        days_until_expiration: int
    ) -> bool:
        """
        Send desktop notification about domain expiration
        
        Args:
            domain_name: Domain name
            days_until_expiration: Days until expiration
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Prepare template data
            template_data = {
                'domain_name': domain_name,
                'days_until_expiration': days_until_expiration
            }
            
            # Render notification content
            template = self.template_env.get_template('desktop_reminder')
            message_content = template.render(**template_data)
            
            # Determine urgency and icon
            if days_until_expiration <= 0:
                title = "🚨 Domain EXPIRED!"
                timeout = 0  # Persistent
            elif days_until_expiration <= 7:
                title = "🔥 Critical Domain Alert"
                timeout = 30
            else:
                title = "⏰ DomainPing Alert"
                timeout = 10
            
            # Send desktop notification
            notification.notify(
                title=title,
                message=message_content,
                timeout=timeout,
                app_name="DomainPing"
            )
            
            logger.info(f"Desktop notification sent for domain {domain_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {str(e)}")
            return False
    
    async def test_email_configuration(self) -> bool:
        """
        Test email configuration by sending a test email
        
        Returns:
            True if test email sent successfully, False otherwise
        """
        try:
            test_email = self.smtp_username
            if not test_email:
                return False
            
            return await self.send_email_notification(
                to_email=test_email,
                domain_name="test-domain.com",
                expiration_date=datetime.now() + timedelta(days=30),
                days_until_expiration=30,
                registrar="Test Registrar",
                notes="This is a test notification to verify email configuration."
            )
        except Exception as e:
            logger.error(f"Email configuration test failed: {str(e)}")
            return False
    
    async def test_sms_configuration(self, test_phone: str) -> bool:
        """
        Test SMS configuration by sending a test SMS
        
        Args:
            test_phone: Phone number to send test SMS to
            
        Returns:
            True if test SMS sent successfully, False otherwise
        """
        try:
            return await self.send_sms_notification(
                to_phone=test_phone,
                domain_name="test-domain.com",
                expiration_date=datetime.now() + timedelta(days=30),
                days_until_expiration=30
            )
        except Exception as e:
            logger.error(f"SMS configuration test failed: {str(e)}")
            return False 