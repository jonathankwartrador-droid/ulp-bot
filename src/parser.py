import re
import logging
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class ULPRecord:
    url: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    domain: Optional[str] = None
    scheme: Optional[str] = None
    original: Optional[str] = None
    is_valid: bool = True
    error_message: str = None

    def __str__(self):
        return f"{self.url}:{self.login}:{self.password}"


class ULPParser:
    """Parse various ULP format variations"""

    # Regex patterns for different ULP formats
    PATTERNS = {
        # Standard: URL:LOGIN:PASS
        'standard': r'^([^:]+):([^:]+):(.+)$',
        
        # HTTPS/HTTP: https://domain.com:login:pass
        'https_http': r'^(https?://[^:]+):([^:]+):(.+)$',
        
        # Custom scheme: scheme://credential@domain/:login:pass
        'scheme_at': r'^([a-zA-Z][a-zA-Z0-9+\-.]*://[^/:]+@[^/]+)/:([^:]+):(.+)$',
        
        # Custom scheme variant: scheme://credential@domain:login:pass
        'scheme_variant': r'^([a-zA-Z][a-zA-Z0-9+\-.]*://[^/:@]+@[^/:]+):([^:]+):(.+)$',
    }

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL to standard format"""
        if not url:
            return url
        
        url = url.strip()
        
        # Add scheme if missing
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', url):
            # Check if it looks like a domain
            if '.' in url or 'localhost' in url:
                url = f"https://{url}"
        
        return url

    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            if not url:
                return None
            
            # Remove scheme if present
            url_to_parse = url
            if '://' in url:
                url_to_parse = url.split('://', 1)[1]
            
            # Extract domain part (before port or path)
            domain = url_to_parse.split('/')[0].split(':')[0].split('@')[-1]
            
            return domain if domain else None
        except Exception as e:
            logger.debug(f"Error extracting domain: {e}")
            return None

    @classmethod
    def parse(cls, line: str) -> ULPRecord:
        """Parse a single ULP line"""
        if not line or not line.strip():
            record = ULPRecord(original=line)
            record.is_valid = False
            record.error_message = "Empty line"
            return record

        line = line.strip()
        original = line

        # Try each pattern
        for pattern_name, pattern in cls.PATTERNS.items():
            match = re.match(pattern, line)
            if match:
                url, login, password = match.groups()
                url = cls.normalize_url(url)
                domain = cls.extract_domain(url)

                return ULPRecord(
                    url=url,
                    login=login,
                    password=password,
                    domain=domain,
                    scheme=pattern_name,
                    original=original,
                    is_valid=True
                )

        # If no pattern matched, try to split by colons and be lenient
        parts = line.split(':')
        if len(parts) >= 3:
            # Find the last two colons (login:pass)
            password = parts[-1]
            login = parts[-2]
            url = ':'.join(parts[:-2])
            
            url = cls.normalize_url(url)
            domain = cls.extract_domain(url)

            return ULPRecord(
                url=url,
                login=login,
                password=password,
                domain=domain,
                scheme='lenient',
                original=original,
                is_valid=True
            )

        # Invalid record
        record = ULPRecord(original=original)
        record.is_valid = False
        record.error_message = "Could not parse ULP format"
        return record

    @classmethod
    def parse_batch(cls, lines: List[str]) -> tuple:
        """Parse multiple lines, return (valid_records, invalid_records)"""
        valid = []
        invalid = []

        for line in lines:
            record = cls.parse(line)
            if record.is_valid:
                valid.append(record)
            else:
                invalid.append(record)

        return valid, invalid

    @staticmethod
    def format_record(record: ULPRecord, output_format: str = 'WITH_URL') -> str:
        """Format record based on output format"""
        if not record.is_valid:
            return None

        if output_format == 'WITH_URL':
            return f"{record.url}:{record.login}:{record.password}"
        elif output_format == 'WITHOUT_URL':
            return f"{record.login}:{record.password}"
        elif output_format == 'URL_ONLY':
            return record.url
        elif output_format == 'LOGIN_ONLY':
            return record.login
        else:
            return f"{record.url}:{record.login}:{record.password}"
