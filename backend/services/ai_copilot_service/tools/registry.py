import json
import logging
from typing import Dict, List, Optional, Any
from pydantic import ValidationError

from services.ai_copilot_service.tools.base import ToolDefinition, DataTier, ApprovalRequirement
from services.ai_copilot_service.tools.finance_tools import FINANCE_TOOLS
from services.ai_copilot_service.tools.hr_tools import HR_TOOLS
from services.ai_copilot_service.tools.crm_tools import CRM_TOOLS
from services.ai_copilot_service.tools.projects_tools import PROJECTS_TOOLS
from services.ai_copilot_service.tools.automation_tools import AUTOMATION_TOOLS
from services.ai_copilot_service.tools.compliance_tools import COMPLIANCE_TOOLS

logger = logging.getLogger("ToolRegistry")


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        # Auto-register all domain tools
        all_tools = (
            FINANCE_TOOLS +
            HR_TOOLS +
            CRM_TOOLS +
            PROJECTS_TOOLS +
            AUTOMATION_TOOLS +
            COMPLIANCE_TOOLS
        )
        for t in all_tools:
            self.register_tool(t)

    def register_tool(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self, user_role: str = "admin") -> List[ToolDefinition]:
        """Filters tool catalogue by authenticated user's role scope."""
        role_lower = str(user_role).lower()
        allowed = []
        for tool in self._tools.values():
            # Founder / Admin / Super Admin gets unrestricted tool access
            if role_lower in ["admin", "super_admin", "founder"]:
                allowed.append(tool)
                continue

            # Executive compensation is strictly founder/admin only
            if tool.name == "get_employee_compensation":
                continue

            # Role-specific pruning
            if "finance" in role_lower and tool.category in ["finance", "automation", "compliance"]:
                allowed.append(tool)
            elif "hr" in role_lower and tool.category in ["hr", "automation", "compliance"]:
                allowed.append(tool)
            elif "sales" in role_lower and tool.category in ["crm", "finance", "automation"]:
                # Sales rep can view invoices and CRM, but not payroll
                if tool.category != "hr":
                    allowed.append(tool)
            elif "project" in role_lower or "engineer" in role_lower:
                if tool.category in ["projects", "automation", "compliance"]:
                    allowed.append(tool)
            else:
                # Default staff member: read-only general tools
                if tool.output_tier != DataTier.TIER_3_RESTRICTED:
                    allowed.append(tool)

        return allowed

    def get_tools_json_schema(self, user_role: str = "admin") -> List[Dict[str, Any]]:
        """Returns JSON schema array for OpenAI / Groq tool calling format."""
        tools = self.list_tools(user_role)
        return [t.get_json_schema() for t in tools]

    def execute_tool(self, tool_name: str, raw_args: Dict[str, Any], user_ctx: Any) -> Dict[str, Any]:
        """
        Executes tool with:
        1. Pydantic schema validation.
        2. Role-based access enforcement.
        3. Side-effect classification.
        4. Data tier tagging.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": "TOOL_NOT_FOUND",
                "message": f"Tool '{tool_name}' is not registered in the system."
            }

        # Role permission check
        user_role = getattr(user_ctx, "role", "admin")
        permitted_tools = [t.name for t in self.list_tools(user_role)]
        if tool_name not in permitted_tools:
            return {
                "success": False,
                "error": "FORBIDDEN",
                "message": f"User with role '{user_role}' lacks permission to invoke '{tool_name}'."
            }

        # Validate arguments against Pydantic args_schema
        try:
            validated_args = tool.args_schema(**raw_args)
        except ValidationError as ve:
            return {
                "success": False,
                "error": "SCHEMA_VALIDATION_ERROR",
                "message": f"Arguments failed validation for '{tool_name}': {ve.errors()}",
                "details": ve.errors()
            }

        # Execute executor
        try:
            if not tool.executor:
                return {
                    "success": False,
                    "error": "NO_EXECUTOR",
                    "message": f"Tool '{tool_name}' has no defined executor."
                }

            result = tool.executor(validated_args, user_ctx)
            return {
                "success": True,
                "tool_name": tool_name,
                "output_tier": tool.output_tier.value,
                "side_effect": tool.side_effect.value,
                "approval_required": tool.approval_requirement != ApprovalRequirement.NONE,
                "approver_role": tool.approver_role,
                "data": result
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "EXECUTION_EXCEPTION",
                "message": str(e)
            }


# Singleton registry instance
default_registry = ToolRegistry()
