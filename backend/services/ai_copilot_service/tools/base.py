from enum import Enum
from typing import Type, Callable, Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DataTier(str, Enum):
    TIER_0_PUBLIC = "TIER_0_PUBLIC"           # Product names, help guides, documentation
    TIER_1_INTERNAL = "TIER_1_INTERNAL"       # Aggregated KPIs, ticket titles, stock counts
    TIER_2_CONFIDENTIAL = "TIER_2_CONFIDENTIAL" # Customer names, deal values, invoice amounts (pseudonymized before model)
    TIER_3_RESTRICTED = "TIER_3_RESTRICTED"   # Salaries, payslips, bank accounts (NEVER sent to external models)


class SideEffect(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    SCHEDULE = "SCHEDULE"
    EXTERNAL = "EXTERNAL"


class ApprovalRequirement(str, Enum):
    NONE = "NONE"
    USER_CONFIRM = "USER_CONFIRM"
    ROLE_APPROVAL = "ROLE_APPROVAL"


class ToolDefinition(BaseModel):
    name: str = Field(description="Unique tool identifier")
    description: str = Field(description="Comprehensive tool capability description")
    category: str = Field(default="general", description="Module category e.g. finance, hr, crm, projects, automation")
    args_schema: Type[BaseModel] = Field(description="Pydantic model defining typed arguments")
    output_schema: Optional[Type[BaseModel]] = Field(default=None, description="Pydantic model defining return shape")
    side_effect: SideEffect = Field(default=SideEffect.READ)
    required_permission: str = Field(default="authenticated")
    output_tier: DataTier = Field(default=DataTier.TIER_1_INTERNAL)
    approval_requirement: ApprovalRequirement = Field(default=ApprovalRequirement.NONE)
    approver_role: Optional[str] = Field(default=None)
    executor: Optional[Callable[..., Any]] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def get_json_schema(self) -> Dict[str, Any]:
        """Generate standard OpenAI / Groq compatible tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema()
            }
        }
