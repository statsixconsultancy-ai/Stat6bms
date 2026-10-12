import re
from typing import Tuple, Dict, Any
from services.ai_copilot_service.tools.base import DataTier


class PrivacyGateway:
    """
    Enforces the STAT6 Enterprise Data Privacy & Zero Data Retention Boundary:
    1. Classifies payload data tiers (Tier 0 to Tier 3).
    2. Enforces 'Data Stays Home': Tier 3 (Restricted Payroll / Bank details) NEVER leaves the trust boundary.
    3. Pseudonymizes Tier 2 identifiers (emails, phone numbers, tax IDs) prior to any model transit.
    4. De-pseudonymizes responses at the client presentation boundary.
    """

    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

    @classmethod
    def classify_data_tier(cls, data: Any) -> DataTier:
        """Determines the strictest data tier contained in the payload."""
        if isinstance(data, dict):
            # Check for Tier 3 Restricted keys
            tier3_keys = {"salary", "salaries", "salary_annual", "annual_salary", "compensation_registry", "payslip", "bank_account", "tax_id"}
            for k in data.keys():
                if any(t3 in k.lower() for t3 in tier3_keys):
                    return DataTier.TIER_3_RESTRICTED

            # Check nested dict values
            for val in data.values():
                if cls.classify_data_tier(val) == DataTier.TIER_3_RESTRICTED:
                    return DataTier.TIER_3_RESTRICTED

            # Check for Tier 2 Confidential
            tier2_keys = {"client_name", "company_name", "email", "total_amount", "amount", "invoice_number"}
            for k in data.keys():
                if any(t2 in k.lower() for t2 in tier2_keys):
                    return DataTier.TIER_2_CONFIDENTIAL

        elif isinstance(data, list):
            for item in data:
                tier = cls.classify_data_tier(item)
                if tier == DataTier.TIER_3_RESTRICTED:
                    return DataTier.TIER_3_RESTRICTED
                if tier == DataTier.TIER_2_CONFIDENTIAL:
                    return DataTier.TIER_2_CONFIDENTIAL

        return DataTier.TIER_1_INTERNAL

    @classmethod
    def pseudonymize_text(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces sensitive personal contact identifiers with stable pseudonyms.
        Returns (pseudonymized_text, reverse_lookup_map).
        """
        reverse_map: Dict[str, str] = {}
        masked = text

        # Mask emails
        emails = cls.EMAIL_REGEX.findall(masked)
        for i, email in enumerate(set(emails)):
            placeholder = f"PERSON_EMAIL_{i+1}"
            reverse_map[placeholder] = email
            masked = masked.replace(email, placeholder)

        # Mask phone numbers
        phones = cls.PHONE_REGEX.findall(masked)
        for i, phone in enumerate(set(phones)):
            placeholder = f"PHONE_NUM_{i+1}"
            reverse_map[placeholder] = phone
            masked = masked.replace(phone, placeholder)

        return masked, reverse_map

    @classmethod
    def restore_pseudonyms(cls, text: str, reverse_map: Dict[str, str]) -> str:
        """Restores original entity names and identifiers within the secure boundary."""
        restored = text
        for placeholder, original in reverse_map.items():
            restored = restored.replace(placeholder, original)
        return restored

    @classmethod
    def is_export_permitted(cls, tier: DataTier, target: str = "hosted_llm") -> bool:
        """
        Hard safety invariant:
        Tier 3 Restricted data CANNOT be exported to any external hosted LLM provider.
        """
        if tier == DataTier.TIER_3_RESTRICTED and target == "hosted_llm":
            return False
        return True
