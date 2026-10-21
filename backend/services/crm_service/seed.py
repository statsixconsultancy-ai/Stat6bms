import uuid
from sqlalchemy.orm import Session
from services.crm_service.models import PipelineDefinition


def seed_crm_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds canonical pipeline definition for sales operations if empty. Zero preloaded business data."""
    if not session.query(PipelineDefinition).filter_by(org_id=org_id).first():
        pipe = PipelineDefinition(
            id=str(uuid.uuid4()),
            org_id=org_id,
            name="Default Enterprise Pipeline",
            description="Standard 5-stage B2B enterprise sales funnel with stage gating & probabilities",
            is_default=True,
            stages=[
                {"name": "Prospecting", "probability": 20, "rotting_days": 14},
                {"name": "Qualification", "probability": 40, "rotting_days": 14},
                {"name": "Proposal Sent", "probability": 65, "rotting_days": 10},
                {"name": "Negotiation", "probability": 85, "rotting_days": 7},
                {"name": "Won", "probability": 100, "rotting_days": 0},
            ]
        )
        session.add(pipe)
        session.commit()
