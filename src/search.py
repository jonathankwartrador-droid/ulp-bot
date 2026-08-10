import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchEngine:
    """Fast search with caching and indexing"""

    def __init__(self, inventory_manager, db):
        self.inventory = inventory_manager
        self.db = db
        self.search_cache = {}
        self.cache_ttl = 3600  # 1 hour

    def search(self, domain: str, inventory_file: str = None, 
              exact_match: bool = True, user_id: int = None) -> Dict:
        """Search for domain"""
        cache_key = f"{domain}:{inventory_file}:{exact_match}"
        if cache_key in self.search_cache:
            cached_data = self.search_cache[cache_key]
            if datetime.now() - cached_data['cached_at'] < timedelta(seconds=self.cache_ttl):
                cached_data['cached'] = True
                
                if user_id:
                    self.db.add_search_history(user_id, domain, len(cached_data['results']))
                
                return cached_data

        try:
            results = self.inventory.search_domain(domain, inventory_file, exact_match)

            search_result = {
                'success': True,
                'domain': domain,
                'results': results,
                'count': len(results),
                'cached': False,
                'cached_at': datetime.now()
            }

            self.search_cache[cache_key] = search_result

            if user_id:
                self.db.add_search_history(user_id, domain, len(results))

            return search_result

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'success': False,
                'error': str(e),
                'domain': domain
            }

    def clear_cache(self):
        """Clear search cache"""
        self.search_cache.clear()

    def get_domain_statistics(self, domain: str) -> Dict:
        """Get statistics for a domain"""
        all_records = self.inventory.search_domain(domain, exact_match=True)
        
        return {
            'domain': domain,
            'total_records': len(all_records)
        }

    def autocomplete_domain(self, partial_domain: str, limit: int = 10) -> List[str]:
        """Autocomplete domain suggestions"""
        suggestions = set()

        for file_name, file_data in self.inventory.cache.items():
            for domain in file_data['domains']:
                if partial_domain.lower() in domain.lower():
                    suggestions.add(domain)
                    if len(suggestions) >= limit:
                        break
            if len(suggestions) >= limit:
                break

        return sorted(list(suggestions))[:limit]
