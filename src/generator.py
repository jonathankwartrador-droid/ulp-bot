import random
import logging
from typing import List
from .parser import ULPParser, ULPRecord

logger = logging.getLogger(__name__)


class CredentialGenerator:
    """Generate credentials from search results"""

    @staticmethod
    def generate(records: List[ULPRecord], quantity: int = 1, 
                output_format: str = 'WITH_URL', random_selection: bool = True) -> List[str]:
        """
        Generate credentials from records
        """
        if not records:
            return []

        quantity = min(quantity, len(records))

        if random_selection:
            selected = random.sample(records, quantity)
        else:
            selected = records[:quantity]

        formatted = []
        for record in selected:
            formatted_record = ULPParser.format_record(record, output_format)
            if formatted_record:
                formatted.append(formatted_record)

        return formatted

    @staticmethod
    def generate_with_duplicates_protection(records: List[ULPRecord], quantity: int = 1,
                                           output_format: str = 'WITH_URL') -> List[str]:
        """Generate without duplicate credentials"""
        if not records:
            return []

        quantity = min(quantity, len(records))

        seen = set()
        result = []

        random_records = random.sample(records, min(len(records), quantity * 2))

        for record in random_records:
            formatted = ULPParser.format_record(record, output_format)
            if formatted and formatted not in seen:
                seen.add(formatted)
                result.append(formatted)
                if len(result) >= quantity:
                    break

        return result[:quantity]

    @staticmethod
    def preview_generation(records: List[ULPRecord], quantity: int = 1,
                          output_format: str = 'WITH_URL') -> str:
        """Generate preview of credentials"""
        generated = CredentialGenerator.generate(records, quantity, output_format)
        
        preview = f"📋 **Generation Preview**\n"
        preview += f"Format: {output_format}\n"
        preview += f"Quantity: {len(generated)}\n"
        preview += f"Available: {len(records)}\n"
        preview += f"\n"

        if generated:
            preview += "**Sample (first 5):**\n"
            for idx, cred in enumerate(generated[:5], 1):
                preview += f"{idx}. `{cred}`\n"
            
            if len(generated) > 5:
                preview += f"\n... and {len(generated) - 5} more"
        else:
            preview += "No credentials to preview"

        return preview
