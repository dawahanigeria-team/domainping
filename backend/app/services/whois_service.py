import whois
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WhoisService:
    def __init__(self):
        self.timeout = int(os.getenv("WHOIS_TIMEOUT", 10))
        self.retry_count = int(os.getenv("WHOIS_RETRY_COUNT", 3))
    
    async def get_domain_info(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch domain information using WHOIS
        
        Args:
            domain_name: The domain name to query
            
        Returns:
            Dictionary with domain information or None if failed
        """
        try:
            # Clean domain name
            domain_name = domain_name.lower().strip()
            if domain_name.startswith(('http://', 'https://')):
                domain_name = domain_name.split('://')[1]
            if '/' in domain_name:
                domain_name = domain_name.split('/')[0]
            
            logger.info(f"Fetching WHOIS data for domain: {domain_name}")
            
            # Perform WHOIS lookup with retries
            for attempt in range(self.retry_count):
                try:
                    # Add timeout to prevent hanging
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("WHOIS lookup timed out")
                    
                    # Set timeout signal (only works on Unix systems)
                    try:
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(self.timeout)
                        
                        w = whois.whois(domain_name)
                        
                        signal.alarm(0)  # Cancel timeout
                        
                        if w:
                            return self._parse_whois_data(w, domain_name)
                        else:
                            logger.warning(f"WHOIS returned empty data for {domain_name}")
                            
                    except (AttributeError, OSError):
                        # signal.alarm not available on Windows or in some containers
                        logger.info("Using fallback WHOIS method without timeout")
                        w = whois.whois(domain_name)
                        
                        if w:
                            return self._parse_whois_data(w, domain_name)
                        else:
                            logger.warning(f"WHOIS returned empty data for {domain_name}")
                    
                except (TimeoutError, ConnectionError, OSError) as e:
                    logger.warning(f"WHOIS attempt {attempt + 1} failed for {domain_name}: Network error - {str(e)}")
                    if attempt == self.retry_count - 1:
                        logger.error(f"All WHOIS attempts failed for {domain_name}. Network connectivity issues.")
                        return {
                            'domain_name': domain_name,
                            'error': 'Network connectivity issues. WHOIS lookup failed.',
                            'error_type': 'network_error',
                            'last_updated': datetime.utcnow()
                        }
                except Exception as e:
                    logger.warning(f"WHOIS attempt {attempt + 1} failed for {domain_name}: {str(e)}")
                    if attempt == self.retry_count - 1:
                        logger.error(f"All WHOIS attempts failed for {domain_name}")
                        return {
                            'domain_name': domain_name,
                            'error': f'WHOIS lookup failed: {str(e)}',
                            'error_type': 'whois_error',
                            'last_updated': datetime.utcnow()
                        }
                    
        except Exception as e:
            logger.error(f"Failed to fetch WHOIS data for {domain_name}: {str(e)}")
            return {
                'domain_name': domain_name,
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unexpected_error',
                'last_updated': datetime.utcnow()
            }
    
    def _parse_whois_data(self, whois_data: Any, domain_name: str) -> Dict[str, Any]:
        """
        Parse WHOIS data into a standardized format
        
        Args:
            whois_data: Raw WHOIS data
            domain_name: Domain name being queried
            
        Returns:
            Parsed domain information
        """
        try:
            # Extract expiration date
            expiration_date = None
            if hasattr(whois_data, 'expiration_date'):
                exp_date = whois_data.expiration_date
                if isinstance(exp_date, list) and exp_date:
                    expiration_date = exp_date[0]
                elif isinstance(exp_date, datetime):
                    expiration_date = exp_date
                elif isinstance(exp_date, str):
                    try:
                        expiration_date = datetime.strptime(exp_date, "%Y-%m-%d")
                    except ValueError:
                        pass
            
            # Extract registration date
            registration_date = None
            if hasattr(whois_data, 'creation_date'):
                reg_date = whois_data.creation_date
                if isinstance(reg_date, list) and reg_date:
                    registration_date = reg_date[0]
                elif isinstance(reg_date, datetime):
                    registration_date = reg_date
                elif isinstance(reg_date, str):
                    try:
                        registration_date = datetime.strptime(reg_date, "%Y-%m-%d")
                    except ValueError:
                        pass
            
            # Extract registrar
            registrar = None
            if hasattr(whois_data, 'registrar'):
                reg = whois_data.registrar
                if isinstance(reg, list) and reg:
                    registrar = reg[0]
                elif isinstance(reg, str):
                    registrar = reg
            
            # Extract name servers
            name_servers = []
            if hasattr(whois_data, 'name_servers'):
                ns = whois_data.name_servers
                if isinstance(ns, list):
                    name_servers = [server.lower() for server in ns if server]
                elif isinstance(ns, str):
                    name_servers = [ns.lower()]
            
            # Extract status
            status = []
            if hasattr(whois_data, 'status'):
                stat = whois_data.status
                if isinstance(stat, list):
                    status = stat
                elif isinstance(stat, str):
                    status = [stat]
            
            # Extract admin email
            admin_email = None
            if hasattr(whois_data, 'emails'):
                emails = whois_data.emails
                if isinstance(emails, list) and emails:
                    admin_email = emails[0]
                elif isinstance(emails, str):
                    admin_email = emails
            
            return {
                'domain_name': domain_name,
                'expiration_date': expiration_date,
                'registration_date': registration_date,
                'registrar': registrar,
                'name_servers': name_servers,
                'status': status,
                'admin_email': admin_email,
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to parse WHOIS data for {domain_name}: {str(e)}")
            return {
                'domain_name': domain_name,
                'error': str(e),
                'last_updated': datetime.utcnow()
            }
    
    async def verify_domain_exists(self, domain_name: str) -> bool:
        """
        Verify if a domain exists and is registered
        
        Args:
            domain_name: Domain name to verify
            
        Returns:
            True if domain exists, False otherwise
        """
        try:
            domain_info = await self.get_domain_info(domain_name)
            return domain_info is not None and 'error' not in domain_info
        except Exception:
            return False
    
    async def get_expiration_date(self, domain_name: str) -> Optional[datetime]:
        """
        Get just the expiration date for a domain
        
        Args:
            domain_name: Domain name to query
            
        Returns:
            Expiration date or None if not found
        """
        try:
            domain_info = await self.get_domain_info(domain_name)
            if domain_info and 'expiration_date' in domain_info:
                return domain_info['expiration_date']
        except Exception as e:
            logger.error(f"Failed to get expiration date for {domain_name}: {str(e)}")
        
        return None 