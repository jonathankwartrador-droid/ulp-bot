import os
import logging
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from .parser import ULPParser, ULPRecord

logger = logging.getLogger(__name__)


class InventoryManager:
    """Manage ULP inventory files"""

    def __init__(self, inventory_path: str, db):
        self.inventory_path = inventory_path
        self.db = db
        Path(inventory_path).mkdir(parents=True, exist_ok=True)
        self.cache = {}
        self.load_all_inventories()

    def load_all_inventories(self):
        """Load all TXT files from inventory directory"""
        txt_files = list(Path(self.inventory_path).glob('*.txt'))
        
        for file_path in txt_files:
            self.load_inventory_file(file_path)

    def load_inventory_file(self, file_path):
        """Load a single inventory file"""
        try:
            filename = file_path.name
            file_size = file_path.stat().st_size

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            valid_records = []
            invalid_count = 0
            domains = set()

            for line in lines:
                record = ULPParser.parse(line)
                if record.is_valid:
                    valid_records.append(record)
                    if record.domain:
                        domains.add(record.domain)
                else:
                    invalid_count += 1

            self.db.add_inventory(
                filename=filename,
                file_path=str(file_path),
                record_count=len(valid_records),
                domain_count=len(domains),
                file_size=file_size
            )

            self.cache[filename] = {
                'records': valid_records,
                'domains': domains,
                'file_path': str(file_path),
                'invalid_count': invalid_count
            }

            logger.info(f"Loaded inventory: {filename} ({len(valid_records)} records, {len(domains)} domains)")
            return True
        except Exception as e:
            logger.error(f"Error loading inventory file {file_path}: {e}")
            return False

    def reload_inventory(self, filename: str = None):
        """Reload inventory file(s)"""
        if filename:
            file_path = Path(self.inventory_path) / filename
            if file_path.exists():
                return self.load_inventory_file(file_path)
            return False
        else:
            self.cache.clear()
            self.load_all_inventories()
            return True

    def get_inventory_stats(self) -> Dict:
        """Get overall inventory statistics"""
        inventories = self.db.get_all_inventory()
        total_records = sum(inv['record_count'] for inv in inventories)
        total_domains = sum(inv['domain_count'] for inv in inventories)

        return {
            'total_files': len(inventories),
            'total_records': total_records,
            'total_domains': total_domains,
            'inventories': inventories
        }

    def search_domain(self, domain: str, inventory_file: str = None, 
                     exact_match: bool = True) -> List[ULPRecord]:
        """Search for domain in inventory"""
        results = []

        domain = domain.lower().strip()

        files_to_search = {}
        if inventory_file:
            if inventory_file in self.cache:
                files_to_search[inventory_file] = self.cache[inventory_file]
        else:
            files_to_search = self.cache

        for file_name, file_data in files_to_search.items():
            for record in file_data['records']:
                if not record.domain:
                    continue

                record_domain = record.domain.lower()

                if exact_match:
                    if record_domain == domain:
                        results.append(record)
                else:
                    if domain in record_domain or record_domain in domain:
                        results.append(record)

        seen = set()
        unique_results = []
        for record in results:
            key = (record.url, record.login, record.password)
            if key not in seen:
                seen.add(key)
                unique_results.append(record)

        return unique_results

    def get_available_inventories(self) -> List[str]:
        """Get list of available inventory files"""
        return list(self.cache.keys())
