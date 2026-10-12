import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("CRMSeed")

def seed_crm_data(session: Session, org_id: str = "org-acroflow-main"):
    """
    Production CRM environment: No template customer data is preloaded.
    All accounts, leads, deals, and quotations are created dynamically by platform users or AI Copilot.
    """
    logger.info("CRM Service initialized in clean production state (zero template customer data).")
    return
