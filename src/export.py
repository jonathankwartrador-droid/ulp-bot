import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


class ExportManager:
    """Handle credential export to TXT files"""

    def __init__(self, export_path: str = "exports/"):
        self.export_path = export_path
        Path(export_path).mkdir(parents=True, exist_ok=True)

    def export_credentials(self, credentials: List[str], domain: str = None, 
                          user_id: int = None) -> dict:
        """Export credentials to TXT file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if domain:
                filename = f"ulp_{domain}_{timestamp}.txt"
            else:
                filename = f"ulp_export_{timestamp}.txt"

            file_path = Path(self.export_path) / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                for cred in credentials:
                    f.write(cred + '\n')

            file_size = file_path.stat().st_size

            logger.info(f"Exported {len(credentials)} credentials to {filename}")

            return {
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'count': len(credentials),
                'size': file_size
            }

        except Exception as e:
            logger.error(f"Error exporting credentials: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_export_file(self, filename: str) -> bytes:
        """Get exported file for download"""
        try:
            file_path = Path(self.export_path) / filename
            if not file_path.exists():
                return None

            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading export file: {e}")
            return None

    def list_exports(self, limit: int = 20) -> List[dict]:
        """List recent exports"""
        try:
            exports = []
            files = sorted(Path(self.export_path).glob('*.txt'), 
                          key=lambda x: x.stat().st_mtime, reverse=True)[:limit]

            for file_path in files:
                stat = file_path.stat()
                exports.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime)
                })

            return exports
        except Exception as e:
            logger.error(f"Error listing exports: {e}")
            return []
