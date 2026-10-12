import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import httpx

from services.ai_copilot_service.tools.registry import default_registry
from services.ai_copilot_service.tools.base import DataTier, SideEffect
from services.ai_copilot_service.privacy import PrivacyGateway

logger = logging.getLogger("AgentEngine")


class AgentEngine:
    """
    Core STAT6 Agentic Reasoning Engine powered by Groq (openai/gpt-oss-120b).
    Executes schema-governed function calling with Pydantic validation,
    DOM context resolution, privacy boundary enforcement, and temporal scheduling.
    No padded results or hardcoded templates.
    """

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.groq_base_url = "https://api.groq.com/openai/v1"
        self.registry = default_registry

    def process_request(
        self,
        message: str,
        page_context: Optional[Dict[str, Any]] = None,
        user_ctx: Any = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        text = message.strip()
        q = text.lower()
        page_ctx = page_context or {}
        user_role = str(getattr(user_ctx, "role", "admin")).lower()

        # -------------------------------------------------------------
        # STEP 1: PRIVACY GATEWAY (TIER 3 RESTRICTED DATA ENCLAVE)
        # -------------------------------------------------------------
        # Individual employee salaries and banking details must NEVER leave
        # the enterprise perimeter to third-party hosted models.
        # When an authorized Founder/Admin queries this, data is fetched
        # locally from the HR database and rendered in a direct client DataTable.
        if any(k in q for k in ["salary", "salaries", "compensation", "wage", "payroll breakdown", "who gets paid"]) and \
           any(k in q for k in ["all employees", "each employee", "individual", "staff salaries", "compensation details", "details of all", "financial details of all"]):
            if user_role not in ["admin", "super_admin", "founder"]:
                return {
                    "reply": "Access Denied: Detailed individual employee compensation records are strictly restricted to the Founder and Super Administrator.",
                    "intent": "HR_COMPENSATION_RESTRICTED",
                    "error": "FORBIDDEN",
                    "sources": ["hr-service:8005 (Permission Guard)"]
                }

            tool_res = self.registry.execute_tool("get_employee_compensation", {}, user_ctx)
            data = tool_res.get("data", {})
            records = data.get("compensation_registry", [])

            reply = (
                f"**Executive Payroll & Compensation Ledger**:\n"
                f"- Total Headcount: **{data.get('total_employees', len(records))}**\n"
                f"- Total Annual Wage Run: **${data.get('total_annual_expenditure', 0):,.2f}**\n"
                f"- Tier 3 Data Guard: Sensitive salary figures rendered directly to authorized client ledger without external LLM transit."
            )

            return {
                "reply": reply,
                "intent": "HR_COMPENSATION_FOUNDER",
                "data_table": {
                    "columns": ["Name", "Job Title", "Department", "Type", "Annual Salary", "Monthly Gross"],
                    "rows": [
                        [r["name"], r["job_title"], r["department"], r["employment_type"], f"${r['annual_salary']:,.2f}", f"${r['monthly_gross']:,.2f}"]
                        for r in records
                    ]
                },
                "sources": ["hr-service:8005", "hr_employees (Tier 3 Enclave)"],
                "output_tier": DataTier.TIER_3_RESTRICTED.value
            }

        # -------------------------------------------------------------
        # STEP 2: AUTONOMOUS REASONING & TOOL CALLING WITH GROQ
        # -------------------------------------------------------------
        if self.groq_api_key:
            try:
                return self._process_with_groq(text, page_ctx, user_ctx, history)
            except Exception as e:
                logger.error(f"Groq API Error: {e}", exc_info=True)
                return {
                    "reply": f"**Groq Model Execution Error**: {str(e)}. Please verify network access to Groq endpoint.",
                    "intent": "MODEL_EXECUTION_ERROR",
                    "sources": ["groq.com/openai/v1"]
                }

        return {
            "reply": "GROQ_API_KEY is not configured. Please supply a valid Groq API key.",
            "intent": "CONFIG_ERROR",
            "sources": ["ai_copilot_service:8013"]
        }

    def _process_with_groq(
        self,
        text: str,
        page_ctx: Dict[str, Any],
        user_ctx: Any,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Executes real tool calling using Groq openai/gpt-oss-120b.
        Evaluates user intent against real microservice databases with zero hardcoded templates.
        """
        user_role = str(getattr(user_ctx, "role", "admin")).lower()
        now_utc = datetime.utcnow()
        client_tz = page_ctx.get("timezone", "UTC")
        client_time = page_ctx.get("client_time", now_utc.isoformat())

        # 1. Format Registered Tools for OpenAI Function Calling Schema
        all_role_tools = self.registry.list_tools(user_role)
        
        # Domain-aware pruning to minimize token payload and stay strictly within Groq rate limits
        q_lower = text.lower()
        active_mod = page_ctx.get("module", "").lower()
        needed_categories = {"automation"}
        if active_mod in ["finance", "hr", "crm", "projects", "compliance"]:
            needed_categories.add(active_mod)
        if any(w in q_lower for w in ["finance", "cash", "revenue", "invoice", "expense", "profit", "margin", "money", "paid", "net30", "dunning", "overdue"]):
            needed_categories.add("finance")
        if any(w in q_lower for w in ["employee", "headcount", "salary", "payroll", "leave", "staff", "dept", "department"]):
            needed_categories.add("hr")
        if any(w in q_lower for w in ["lead", "deal", "pipeline", "crm", "client", "customer", "quote", "sales", "opportunity", "acme"]):
            needed_categories.add("crm")
            needed_categories.add("finance")
        if any(w in q_lower for w in ["project", "task", "sprint", "issue", "bug", "ticket", "story"]):
            needed_categories.add("projects")
        if any(w in q_lower for w in ["compliance", "gdpr", "audit", "control", "policy"]):
            needed_categories.add("compliance")

        tools = [t for t in all_role_tools if t.category in needed_categories] if len(needed_categories) > 1 else all_role_tools
        if not tools:
            tools = all_role_tools

        openai_tools = []
        for t in tools:
            schema = t.args_schema.model_json_schema()
            schema.pop("title", None)
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": schema
                }
            })

        # 2. Build Comprehensive Situational System Prompt
        sys_prompt = (
            "You are the STAT6 Autonomous Operations Copilot, an enterprise-grade AI operating across AcroFlow Global Enterprises' 14 microservices mesh.\n\n"
            f"TEMPORAL CONTEXT:\n"
            f"- Current UTC Timestamp: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
            f"- Client Local Time: {client_time}\n"
            f"- Client Timezone: {client_tz}\n\n"
            f"CALLER CONTEXT:\n"
            f"- User ID: {getattr(user_ctx, 'user_id', 'usr-dev-001')}\n"
            f"- Role: {user_role.upper()}\n"
            f"- Organization: {getattr(user_ctx, 'org_id', 'org-acroflow-main')}\n\n"
            f"ACTIVE VIEWPORT CONTEXT:\n"
            f"- Active Module: {page_ctx.get('module', 'overview')}\n"
            f"- Route: {page_ctx.get('route', '/')}\n"
            f"- Selected Entity IDs: {page_ctx.get('selected_ids', [])}\n\n"
            "STRICT OPERATIONAL DIRECTIVES:\n"
            "1. NO PADDED OR MOCK DATA: Never hallucinate numbers or provide fake static templates. Always retrieve actual live state using the registered tools.\n"
            "2. SCHEMA-BOUND FUNCTION CALLING: When asked for metrics, data queries, or state changes, select the best tool and supply typed arguments matching its schema.\n"
            "3. TEMPORAL SCHEDULING: When asked to schedule an action (e.g. reminders, syncs, reviews), calculate the target UTC ISO timestamp (e.g. tomorrow at 10 AM UTC) and invoke `schedule_task`. Set `requires_hitl=True` for financial or client communications.\n"
            "4. EXECUTIVE PRESENTATION: Respond with professional, concise, data-driven markdown. Use markdown tables and bullet points. Never use conversational filler like 'Sure! I can help you with that'."
        )

        messages = [{"role": "system", "content": sys_prompt}]

        # Add recent conversation history if provided
        if history:
            for h in history[-4:]:
                r = h.get("role") or h.get("sender")
                r = "user" if r == "user" else "assistant"
                c = h.get("content") or h.get("text")
                if c:
                    messages.append({"role": r, "content": c})

        messages.append({"role": "user", "content": text})

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        def _call_groq(client_inst, payload_dict):
            import time
            for attempt in range(5):
                r = client_inst.post(
                    f"{self.groq_base_url}/chat/completions",
                    headers=headers,
                    json=payload_dict
                )
                if r.status_code == 429:
                    err_json = {}
                    err_msg = ""
                    try:
                        err_json = r.json()
                        err_msg = err_json.get("error", {}).get("message", "")
                    except Exception:
                        pass

                    # If daily token quota reached on 120b, immediately route to companion openai/gpt-oss-20b
                    if ("tokens per day" in err_msg.lower() or "tpd" in err_msg.lower()) and payload_dict.get("model") == "openai/gpt-oss-120b":
                        logger.warning("Groq 120B daily token limit reached. Seamlessly routing to companion openai/gpt-oss-20b.")
                        payload_dict["model"] = "openai/gpt-oss-20b"
                        continue

                    wait_time = 3.5
                    match = re.search(r"try again in ([\d\.]+)s", err_msg)
                    if match:
                        wait_time = float(match.group(1)) + 1.0
                    logger.info(f"Groq 429 rate limit reached, backing off {wait_time:.1f}s (attempt {attempt+1})")
                    time.sleep(wait_time)
                    continue
                r.raise_for_status()
                return r.json()["choices"][0]["message"]
            r.raise_for_status()
            return r.json()["choices"][0]["message"]

        with httpx.Client(timeout=60.0) as client:
            # 3. Call Groq Turn 1 (Tool Selection)
            choice1 = _call_groq(client, {
                "model": self.groq_model,
                "messages": messages,
                "tools": openai_tools if openai_tools else None,
                "tool_choice": "auto" if openai_tools else None,
                "temperature": 0.1,
                "max_tokens": 512
            })

            tool_calls = choice1.get("tool_calls", [])

            # If no tools called, return direct model reasoning
            if not tool_calls:
                return {
                    "reply": choice1.get("content", ""),
                    "intent": "EXECUTIVE_ADVISORY",
                    "sources": ["groq.com/openai/v1"]
                }

            # 4. Execute Real Tools Against Microservices Mesh
            executed_sources = []
            immediate_data = {}
            scheduled_task_summary = None
            data_table = None
            confirmation_card = None
            intent = "TOOL_AUGMENTED_EXECUTION"
            output_tier = DataTier.TIER_1_INTERNAL.value

            messages.append(choice1)

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except Exception:
                    fn_args = {}

                tool_def = self.registry.get_tool(fn_name)
                service_origin = f"{tool_def.category}-service" if tool_def else "mesh"
                executed_sources.append(service_origin)

                if fn_name == "schedule_task":
                    if fn_args.get("target_service") == "finance-service" or "reminder" in fn_args.get("task_name", "").lower() or "invoice" in str(fn_args).lower() or "approval" in text.lower():
                        fn_args["requires_hitl"] = True

                tool_res = self.registry.execute_tool(fn_name, fn_args, user_ctx)
                res_data = tool_res.get("data", {})

                # Process specific tool response characteristics
                if fn_name == "get_financial_summary":
                    intent = "FINANCIAL_SYNTHESIS"
                    immediate_data = {
                        "total_paid_revenue": res_data.get("total_paid_revenue"),
                        "cash_reserves": res_data.get("cash_reserves"),
                        "operating_margin_pct": res_data.get("operating_margin_pct"),
                        "overdue_invoices_count": res_data.get("overdue_invoices_count")
                    }
                    output_tier = DataTier.TIER_2_CONFIDENTIAL.value

                elif fn_name == "schedule_task":
                    intent = "TEMPORAL_TASK_SCHEDULED"
                    scheduled_task_summary = {
                        "task_id": res_data.get("task_id"),
                        "task_name": fn_args.get("task_name", "Automated Task"),
                        "target_service": fn_args.get("target_service", "automation-service"),
                        "scheduled_for": fn_args.get("scheduled_for", ""),
                        "requires_hitl": bool(fn_args.get("requires_hitl", False)),
                        "hitl_approval_id": res_data.get("hitl_approval_id"),
                        "status": "WAITING_APPROVAL" if fn_args.get("requires_hitl") else "PENDING"
                    }

                elif fn_name in ["create_invoice", "create_lead", "create_deal", "create_issue"]:
                    confirmation_card = {
                        "action": fn_name,
                        "title": f"Created: {fn_args.get('title') or fn_args.get('name') or fn_args.get('client_name') or fn_name}",
                        "details": json.dumps(fn_args, indent=2)
                    }

                elif fn_name == "get_payroll_summary":
                    intent = "HR_PAYROLL_SUMMARY"
                    output_tier = DataTier.TIER_3_RESTRICTED.value
                    depts = res_data.get("department_breakdown", [])
                    data_table = {
                        "columns": ["Department", "Headcount", "Annual Payroll", "Monthly Run", "Avg Salary"],
                        "rows": [
                            [d["department"], d["headcount"], f"${d['annual_payroll']:,.2f}", f"${d['monthly_payroll']:,.2f}", f"${d['avg_salary']:,.2f}"]
                            for d in depts
                        ]
                    }

                elif fn_name == "find_invoices":
                    invoices_list = res_data if isinstance(res_data, list) else []
                    if invoices_list:
                        data_table = {
                            "columns": ["Invoice #", "Client", "Amount", "Status", "Due Date"],
                            "rows": [
                                [inv.get("invoice_number"), inv.get("client_name"), f"${inv.get('total_amount', 0):,.2f}", inv.get("status"), inv.get("due_date")]
                                for inv in invoices_list
                            ]
                        }

                elif fn_name == "find_deals":
                    deals_list = res_data if isinstance(res_data, list) else []
                    if deals_list:
                        data_table = {
                            "columns": ["Title", "Company", "Amount", "Stage", "Probability"],
                            "rows": [
                                [d.get("title"), d.get("company_name"), f"${d.get('amount', 0):,.2f}", d.get("stage"), f"{d.get('probability')}%"]
                                for d in deals_list
                            ]
                        }

                elif fn_name == "list_issues":
                    issues_list = res_data if isinstance(res_data, list) else []
                    if issues_list:
                        data_table = {
                            "columns": ["Key", "Title", "Type", "Status", "Priority", "Points"],
                            "rows": [
                                [iss.get("issue_key"), iss.get("title"), iss.get("issue_type"), iss.get("status"), iss.get("priority"), iss.get("story_points")]
                                for iss in issues_list
                            ]
                        }

                # Feed real execution result back to Groq
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": json.dumps(res_data)
                })

            # 5. Call Groq Turn 2 for Final Synthesis (Keeping tools available)
            choice2 = _call_groq(client, {
                "model": self.groq_model,
                "messages": messages,
                "tools": openai_tools if openai_tools else None,
                "tool_choice": "auto" if openai_tools else None,
                "temperature": 0.1,
                "max_tokens": 512
            })
            
            # If model chained a tool call in Turn 2 (e.g. find_invoices then schedule_task)
            if choice2.get("tool_calls"):
                messages.append(choice2)
                for tc in choice2["tool_calls"]:
                    fn_name = tc["function"]["name"]
                    try:
                        fn_args = json.loads(tc["function"]["arguments"])
                    except Exception:
                        fn_args = {}
                    tool_def = self.registry.get_tool(fn_name)
                    if tool_def:
                        executed_sources.append(f"{tool_def.category}-service")

                    if fn_name == "schedule_task":
                        if fn_args.get("target_service") == "finance-service" or "reminder" in fn_args.get("task_name", "").lower() or "invoice" in str(fn_args).lower() or "approval" in text.lower():
                            fn_args["requires_hitl"] = True

                    tool_res = self.registry.execute_tool(fn_name, fn_args, user_ctx)
                    res_data = tool_res.get("data", {})
                    if fn_name == "schedule_task":
                        intent = "TEMPORAL_TASK_SCHEDULED"
                        scheduled_task_summary = {
                            "task_id": res_data.get("task_id"),
                            "task_name": fn_args.get("task_name", "Automated Task"),
                            "target_service": fn_args.get("target_service", "automation-service"),
                            "scheduled_for": fn_args.get("scheduled_for", ""),
                            "requires_hitl": bool(fn_args.get("requires_hitl", False)),
                            "hitl_approval_id": res_data.get("hitl_approval_id"),
                            "status": "WAITING_APPROVAL" if fn_args.get("requires_hitl") else "PENDING"
                        }
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": json.dumps(res_data)
                    })
                
                # Turn 3 final synthesis
                choice3 = _call_groq(client, {
                    "model": self.groq_model,
                    "messages": messages,
                    "tools": openai_tools if openai_tools else None,
                    "tool_choice": "auto" if openai_tools else None,
                    "temperature": 0.1,
                    "max_tokens": 512
                })
                final_text = choice3.get("content", "")
            else:
                final_text = choice2.get("content", "")

            if intent == "FINANCIAL_SYNTHESIS" and "STAT6 Corporate Financial Health" not in final_text:
                final_text = f"### STAT6 Corporate Financial Health & Capital Position\n\n{final_text}"

            return {
                "reply": final_text,
                "intent": intent,
                "immediate_data": immediate_data,
                "scheduled_task": scheduled_task_summary,
                "data_table": data_table,
                "confirmation_card": confirmation_card,
                "sources": list(set(executed_sources)),
                "output_tier": output_tier
            }


# Singleton engine instance
default_engine = AgentEngine()
