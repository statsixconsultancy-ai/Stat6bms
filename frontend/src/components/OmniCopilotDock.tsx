import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  X,
  Maximize2,
  Minimize2,
  Sparkles,
  ShieldCheck,
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  Table as TableIcon,
  Lock,
  RefreshCw,
  Layers,
  ArrowUpRight
} from 'lucide-react';

export interface DataTableData {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

export interface ScheduledTaskSummaryData {
  task_id?: string;
  task_name: string;
  target_service: string;
  scheduled_for: string;
  requires_hitl: boolean;
  hitl_approval_id?: string | null;
  status: string;
}

export interface HITLApprovalData {
  id: string;
  title: string;
  summary: string;
  riskLevel: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  payload?: Record<string, any>;
}

export interface ConfirmationCardData {
  action: string;
  title: string;
  details: string;
}

export interface CopilotMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  intent?: string;
  outputTier?: string; // TIER_0_PUBLIC, TIER_1_INTERNAL, TIER_2_CONFIDENTIAL, TIER_3_RESTRICTED
  dataTable?: DataTableData;
  scheduledTask?: ScheduledTaskSummaryData;
  hitlRequest?: HITLApprovalData;
  confirmationCard?: ConfirmationCardData;
  immediateData?: {
    revenue?: number;
    cash?: number;
    margin?: number;
    pipeline?: number;
    sprint?: string;
  };
  sources?: string[];
  actionsSuggested?: string[];
}

export interface PageContextPayload {
  module: string;
  route: string;
  selected_ids?: string[];
  filters?: Record<string, any>;
  timezone: string;
  client_time: string;
}

interface OmniCopilotDockProps {
  apiBase: string;
  activeTab: string;
  selectedItem?: { id: string; type: string; title?: string } | null;
  messages: CopilotMessage[];
  onMessagesChange: React.Dispatch<React.SetStateAction<CopilotMessage[]>>;
  onNavigateTab: (tab: string) => void;
  onTasksUpdated?: () => void;
  onShowNotification?: (msg: string) => void;
}

export const OmniCopilotDock: React.FC<OmniCopilotDockProps> = ({
  apiBase,
  activeTab,
  selectedItem,
  messages,
  onMessagesChange,
  onNavigateTab,
  onTasksUpdated,
  onShowNotification
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [copiedTableIdx, setCopiedTableIdx] = useState<number | null>(null);
  const [activeTabInside, setActiveTabInside] = useState<'chat' | 'context'>('chat');
  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // Global hotkey: Ctrl + / or Cmd + / to toggle dock
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        setIsOpen(prev => !prev);
      } else if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  // Format module display name
  const getModuleName = (tab: string) => {
    const names: Record<string, string> = {
      dashboard: 'Executive Cockpit',
      leads: 'CRM Leads & Prospects',
      deals: 'Commercial Deals Pipeline',
      marketing: 'Marketing Campaigns & ROI',
      projects: 'Projects & Jira Board',
      hr: 'People Operations & Payroll',
      finance: 'Finance & General Ledger',
      inventory: 'Warehouse Inventory',
      procurement: 'Procurement & Vendor POs',
      helpdesk: 'Helpdesk & Client Support',
      collaboration: 'Team Collaboration Chat',
      compliance: 'SOC2 & Compliance Center',
      automation: 'Temporal Automation Engine',
      ai: 'Autonomous Operations Copilot'
    };
    return names[tab] || tab.toUpperCase();
  };

  // Context-aware prompt suggestions
  const getSuggestedPrompts = (tab: string) => {
    switch (tab) {
      case 'finance':
        return [
          'What are our current cash reserves and overdue receivables?',
          'Schedule Net30 overdue invoice reminder to Acme Corp tomorrow at 10 AM',
          'Show all unpaid invoices across enterprise clients'
        ];
      case 'hr':
        return [
          'Give me complete salary and compensation details of all employees',
          'Summarize enterprise payroll aggregation and monthly run',
          'Review team headcount across departments'
        ];
      case 'projects':
        return [
          'What issues are currently Blocked on Sprint 44?',
          'List all high-priority engineering tasks',
          'Schedule task: Multi-tenant ledger sync review tomorrow at 2 PM'
        ];
      case 'leads':
      case 'deals':
        return [
          'Forecast Q4 commercial deal pipeline and won revenue',
          'Find qualified enterprise leads in technology sector',
          'Show high-value pipeline deals above $100,000'
        ];
      case 'compliance':
      case 'automation':
        return [
          'Check SOC2 Type II compliance status and audit readiness',
          'List all scheduled background temporal tasks',
          'Verify cryptographic hash audit logs for today'
        ];
      default:
        return [
          'What is our financial health and cash position today?',
          'Give me complete salary and compensation details of all employees',
          'Schedule Net30 reminder for Acme Corp tomorrow at 10 AM (Require Approval)',
          'What is blocked on Sprint 44 right now?'
        ];
    }
  };

  // Send message through Gateway -> AI Copilot Service with DOM Context
  const handleSendMessage = async (customPrompt?: string) => {
    const textToSend = (customPrompt || inputValue).trim();
    if (!textToSend || isThinking) return;

    const userMsgId = 'msg-' + Date.now();
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMsg: CopilotMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: nowTime
    };

    onMessagesChange(prev => [...prev, userMsg]);
    if (!customPrompt) setInputValue('');
    setIsThinking(true);

    const clientTz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    const pageContextPayload: PageContextPayload = {
      module: activeTab,
      route: `/${activeTab}`,
      selected_ids: selectedItem ? [selectedItem.id] : [],
      filters: {},
      timezone: clientTz,
      client_time: new Date().toISOString()
    };

    try {
      const resp = await fetch(`${apiBase}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          conversation_id: userMsgId,
          page_context: pageContextPayload
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        
        let scheduledTaskSummary: ScheduledTaskSummaryData | undefined;
        let hitlData: HITLApprovalData | undefined;

        if (data.scheduled_task) {
          scheduledTaskSummary = {
            task_id: data.scheduled_task.task_id,
            task_name: data.scheduled_task.task_name,
            target_service: data.scheduled_task.target_service,
            scheduled_for: data.scheduled_task.scheduled_for,
            requires_hitl: data.scheduled_task.requires_hitl,
            hitl_approval_id: data.scheduled_task.hitl_approval_id,
            status: data.scheduled_task.status || (data.scheduled_task.requires_hitl ? 'WAITING_APPROVAL' : 'PENDING')
          };

          if (data.scheduled_task.requires_hitl) {
            hitlData = {
              id: data.scheduled_task.hitl_approval_id || 'hitl-' + Date.now(),
              title: `Authorization Required: ${data.scheduled_task.task_name}`,
              summary: `Automated action targeting ${data.scheduled_task.target_service} requires human approval before dispatch.`,
              riskLevel: 'HIGH',
              status: 'PENDING',
              payload: {
                target_service: data.scheduled_task.target_service,
                action: data.scheduled_task.task_name,
                scheduled_for: data.scheduled_task.scheduled_for
              }
            };
          }
        }

        const assistantMsg: CopilotMessage = {
          id: 'asst-' + Date.now(),
          sender: 'assistant',
          text: data.reply || 'Request processed successfully.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: data.intent,
          outputTier: data.output_tier || 'TIER_1_INTERNAL',
          dataTable: data.data_table ? {
            columns: data.data_table.columns || [],
            rows: data.data_table.rows || []
          } : undefined,
          scheduledTask: scheduledTaskSummary,
          hitlRequest: hitlData,
          confirmationCard: data.confirmation_card ? {
            action: data.confirmation_card.action,
            title: data.confirmation_card.title,
            details: data.confirmation_card.details
          } : undefined,
          immediateData: data.immediate_data ? {
            revenue: data.immediate_data.total_paid_revenue,
            cash: data.immediate_data.cash_reserves,
            margin: data.immediate_data.operating_margin_pct,
            pipeline: data.immediate_data.pipeline_value
          } : undefined,
          sources: data.sources || [],
          actionsSuggested: data.actions_suggested || []
        };

        onMessagesChange(prev => [...prev, assistantMsg]);
        setIsThinking(false);

        if (data.scheduled_task && onTasksUpdated) {
          onTasksUpdated();
        }
        if (onShowNotification && data.scheduled_task) {
          onShowNotification(`Task scheduled: ${data.scheduled_task.task_name}`);
        }
        return;
      } else {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData?.detail || `Gateway returned HTTP ${resp.status}`);
      }
    } catch (err: any) {
      const errorMsg: CopilotMessage = {
        id: 'asst-' + Date.now(),
        sender: 'assistant',
        text: `**Service Mesh Notification**: ${err?.message || 'Unable to connect to AI Copilot service'}. Ensure backend services are running.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: 'NETWORK_ERROR',
        outputTier: 'TIER_0_PUBLIC',
        sources: ['gateway:8000']
      };
      onMessagesChange(prev => [...prev, errorMsg]);
      setIsThinking(false);
    }
  };

  // Handle HITL Approval Decision
  const handleHitlDecision = async (msgId: string, hitlId: string, decision: 'APPROVED' | 'REJECTED') => {
    onMessagesChange(prev => prev.map(m => {
      if (m.id === msgId && m.hitlRequest) {
        return {
          ...m,
          hitlRequest: { ...m.hitlRequest, status: decision },
          scheduledTask: m.scheduledTask ? {
            ...m.scheduledTask,
            status: decision === 'APPROVED' ? 'APPROVED_BY_HUMAN (QUEUED)' : 'CANCELLED_BY_HUMAN'
          } : undefined
        };
      }
      return m;
    }));

    try {
      await fetch(`${apiBase}/automation/hitl/${hitlId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          decision_notes: `Processed via Omni-Copilot Dock by active session user`
        })
      });
      if (onTasksUpdated) onTasksUpdated();
      if (onShowNotification) {
        onShowNotification(decision === 'APPROVED' ? 'Task authorized for automated execution' : 'Task rejected by user');
      }
    } catch {
      // Local state is already updated
    }
  };

  // Copy data table as CSV
  const handleCopyTable = (table: DataTableData, idx: number) => {
    const csvContent = [
      table.columns.join(','),
      ...table.rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    navigator.clipboard.writeText(csvContent);
    setCopiedTableIdx(idx);
    setTimeout(() => setCopiedTableIdx(null), 2000);
  };

  return (
    <>
      {/* ---------------------------------------------------- */}
      {/* 1. FLOATING OMNI-COPILOT LAUNCHER BUTTON            */}
      {/* ---------------------------------------------------- */}
      <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 select-none">
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            className="group relative flex items-center gap-2.5 px-4 py-3 bg-gradient-to-r from-[#1e3a8a] via-[#1d4ed8] to-[#2563eb] hover:from-[#1d4ed8] hover:to-[#3b82f6] text-white rounded-full shadow-2xl border border-blue-400/30 transition-all duration-200 transform hover:scale-105 active:scale-95 cursor-pointer"
            title="Open STAT6 Omnipresent Copilot (Ctrl + /)"
          >
            <div className="relative flex items-center justify-center">
              <Bot size={18} className="text-amber-300 transition-transform group-hover:rotate-6" />
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-emerald-400/40 animate-ping"></span>
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold tracking-wide flex items-center gap-1.5">
                STAT6 Omni-Copilot
                <span className="px-1.5 py-0.2 text-[9px] font-mono bg-blue-900/80 text-blue-200 rounded border border-blue-400/30">
                  Agentic
                </span>
              </span>
              <span className="text-[10px] text-blue-200/80 font-mono">
                {getModuleName(activeTab)}
              </span>
            </div>
            <kbd className="hidden sm:inline-block ml-1 text-[10px] px-1.5 py-0.5 rounded bg-black/30 border border-white/20 text-blue-200 font-mono">
              Ctrl+/
            </kbd>
          </button>
        )}
      </div>

      {/* ---------------------------------------------------- */}
      {/* 2. HOVERING OMNIPRESENT COPILOT DOCK WINDOW         */}
      {/* ---------------------------------------------------- */}
      {isOpen && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex flex-col rounded-2xl shadow-2xl border border-slate-700/80 bg-[#0f172a]/95 backdrop-blur-md text-slate-100 overflow-hidden transition-all duration-200 ${
            isExpanded
              ? 'w-[95vw] sm:w-[720px] h-[85vh] max-h-[820px]'
              : 'w-[92vw] sm:w-[460px] h-[600px] max-h-[82vh]'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#1e293b]/90 border-b border-slate-700/80 flex-shrink-0">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-xs">
                <Bot size={18} className="text-amber-300" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-white tracking-wide">
                    STAT6 Omni-Copilot
                  </h3>
                  <span className="px-1.5 py-0.2 rounded-full text-[9px] font-mono font-medium bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    14 Microservices
                  </span>
                </div>
                <p className="text-[10px] text-slate-400">
                  Schema-bound execution • Privacy-first boundary
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-slate-400">
              {/* Maximize to full tab */}
              <button
                onClick={() => {
                  onNavigateTab('ai');
                  setIsOpen(false);
                }}
                className="p-1.5 rounded-lg hover:bg-slate-700/50 hover:text-white transition"
                title="Open full AI Tab"
              >
                <ArrowUpRight size={15} />
              </button>
              {/* Expand / Shrink */}
              <button
                onClick={() => setIsExpanded(prev => !prev)}
                className="p-1.5 rounded-lg hover:bg-slate-700/50 hover:text-white transition"
                title={isExpanded ? 'Shrink' : 'Expand width'}
              >
                {isExpanded ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
              </button>
              {/* Close */}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-700/50 hover:text-white transition"
                title="Close (Esc)"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          {/* Active Context Banner */}
          <div className="px-4 py-2 bg-[#131d33] border-b border-slate-800 text-[11px] flex items-center justify-between text-slate-300 flex-shrink-0">
            <div className="flex items-center gap-1.5 truncate">
              <Layers size={13} className="text-blue-400 flex-shrink-0" />
              <span className="text-slate-400">Context:</span>
              <span className="font-semibold text-white truncate">
                {getModuleName(activeTab)}
              </span>
              {selectedItem && (
                <span className="font-mono text-[10px] px-1.5 py-0.2 bg-blue-900/60 text-blue-200 rounded border border-blue-700/50">
                  #{selectedItem.id}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 flex-shrink-0 text-[10px] font-mono text-slate-400">
              <span className="hidden sm:inline">TZ: {Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'}</span>
              <button
                onClick={() => setActiveTabInside(prev => prev === 'chat' ? 'context' : 'chat')}
                className="text-blue-400 hover:text-blue-300 underline cursor-pointer"
              >
                {activeTabInside === 'chat' ? 'View Tools (12)' : 'Back to Chat'}
              </button>
            </div>
          </div>

          {/* Body Content */}
          {activeTabInside === 'context' ? (
            <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs bg-[#0b1120]">
              <div className="font-bold text-white flex items-center gap-2">
                <ShieldCheck size={16} className="text-emerald-400" />
                <span>Active Registered Domain Tools</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                All agent actions are governed by typed Pydantic <code>args_schema</code> contracts and verified against the caller's RBAC scope.
              </p>
              <div className="space-y-2 pt-1 font-mono text-[11px]">
                {[
                  { name: 'get_financial_summary', tier: 'Tier 2 (Confidential)', service: 'finance-service:8006' },
                  { name: 'get_employee_compensation', tier: 'Tier 3 (Restricted)', service: 'hr-service:8005', badge: 'Data Stays Home' },
                  { name: 'get_payroll_summary', tier: 'Tier 3 (Restricted)', service: 'hr-service:8005' },
                  { name: 'schedule_task', tier: 'Tier 2 (Temporal Action)', service: 'automation-service:8012', badge: 'HITL Gated' },
                  { name: 'find_invoices', tier: 'Tier 2 (Confidential)', service: 'finance-service:8006' },
                  { name: 'create_invoice', tier: 'Tier 2 (Write Mutation)', service: 'finance-service:8006' },
                  { name: 'find_deals', tier: 'Tier 1 (Internal)', service: 'crm-service:8002' },
                  { name: 'list_issues', tier: 'Tier 1 (Internal)', service: 'projects-service:8004' },
                  { name: 'get_compliance_status', tier: 'Tier 1 (Internal)', service: 'compliance-service:8011' }
                ].map(tool => (
                  <div key={tool.name} className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="text-blue-300 font-semibold">{tool.name}</div>
                      <div className="text-[10px] text-slate-500">{tool.service}</div>
                    </div>
                    <div className="text-right space-y-1">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                        {tool.tier}
                      </span>
                      {tool.badge && (
                        <div className="text-[9px] text-emerald-400 font-semibold">
                          🛡️ {tool.badge}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col min-h-0 bg-[#0b1120]">
              {/* Message Stream */}
              <div
                ref={chatScrollRef}
                className="flex-1 p-3.5 overflow-y-auto space-y-3.5"
              >
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center py-10 text-center space-y-3 px-2">
                    <div className="w-12 h-12 rounded-2xl bg-blue-950/60 border border-blue-800 flex items-center justify-center text-blue-400 shadow-xs">
                      <Bot size={24} className="text-amber-300" />
                    </div>
                    <div className="space-y-1 max-w-sm">
                      <h4 className="text-xs font-bold text-white">
                        Omnipresent Agentic Reasoning
                      </h4>
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        I am synced with <strong>{getModuleName(activeTab)}</strong>. Ask about metrics, inspect records, or schedule automated background tasks.
                      </p>
                    </div>

                    {/* Quick suggestion chips */}
                    <div className="w-full pt-2 space-y-1.5 text-left">
                      <div className="text-[10px] font-semibold uppercase text-slate-500 px-1">
                        Suggested in this context:
                      </div>
                      {getSuggestedPrompts(activeTab).map((prompt, i) => (
                        <button
                          key={i}
                          onClick={() => handleSendMessage(prompt)}
                          className="w-full text-left p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-[11px] text-slate-300 transition flex items-center justify-between group cursor-pointer"
                        >
                          <span className="truncate pr-2">{prompt}</span>
                          <Sparkles size={12} className="text-blue-400 opacity-0 group-hover:opacity-100 flex-shrink-0 transition" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    {/* Role Tag & Tier Guard */}
                    <div className="flex items-center gap-2 mb-1 px-1">
                      <span className="text-[10px] text-slate-400">
                        {msg.sender === 'user' ? 'You' : 'STAT6 Copilot'} • {msg.timestamp}
                      </span>
                      {msg.outputTier === 'TIER_3_RESTRICTED' && (
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
                          <Lock size={9} />
                          Tier 3: In-House Boundary
                        </span>
                      )}
                    </div>

                    {/* Bubble Content */}
                    <div
                      className={`rounded-2xl p-3 text-xs leading-relaxed max-w-[95%] ${
                        msg.sender === 'user'
                          ? 'bg-[#2563eb] text-white rounded-br-xs shadow-xs'
                          : 'bg-[#1e293b] text-slate-100 border border-slate-700/80 rounded-bl-xs shadow-xs space-y-2.5'
                      }`}
                    >
                      <div className="whitespace-pre-line">{msg.text}</div>

                      {/* DATA TABLE RENDERER (Tier 3 Employee Compensation / Ledgers) */}
                      {msg.dataTable && (
                        <div className="mt-2 rounded-xl border border-slate-700 bg-[#0f172a] overflow-hidden">
                          <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800/80 border-b border-slate-700 text-[10px]">
                            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                              <TableIcon size={12} className="text-blue-400" />
                              Structured Data View ({msg.dataTable.rows.length} rows)
                            </span>
                            <button
                              onClick={() => handleCopyTable(msg.dataTable!, idx)}
                              className="px-2 py-0.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 flex items-center gap-1 transition"
                              title="Copy CSV"
                            >
                              {copiedTableIdx === idx ? (
                                <>
                                  <Check size={10} className="text-emerald-400" />
                                  <span>Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy size={10} />
                                  <span>Export CSV</span>
                                </>
                              )}
                            </button>
                          </div>
                          <div className="overflow-x-auto max-h-56">
                            <table className="w-full text-[11px] text-left">
                              <thead className="bg-slate-900/90 text-slate-400 text-[10px] uppercase font-semibold border-b border-slate-800">
                                <tr>
                                  {msg.dataTable.columns.map((col, cIdx) => (
                                    <th key={cIdx} className="px-2.5 py-1.5 whitespace-nowrap">
                                      {col}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-800/60 font-mono">
                                {msg.dataTable.rows.map((row, rIdx) => (
                                  <tr key={rIdx} className="hover:bg-slate-800/40">
                                    {row.map((val, cellIdx) => (
                                      <td key={cellIdx} className="px-2.5 py-1.5 whitespace-nowrap text-slate-200">
                                        {String(val ?? '-')}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {/* SCHEDULED TASK CARD */}
                      {msg.scheduledTask && (
                        <div className="p-3 bg-blue-950/40 rounded-xl border border-blue-800/80 space-y-1.5">
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="font-semibold text-blue-300 flex items-center gap-1.5">
                              <Clock size={12} className="text-blue-400" />
                              Scheduled Background Task
                            </span>
                            <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                              msg.scheduledTask.status.includes('APPROVED')
                                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                                : 'bg-blue-900/60 text-blue-200 border border-blue-700'
                            }`}>
                              {msg.scheduledTask.status}
                            </span>
                          </div>
                          <div className="text-xs font-medium text-white">
                            {msg.scheduledTask.task_name}
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-0.5">
                            <span>Target: {msg.scheduledTask.target_service}</span>
                            <span>{msg.scheduledTask.scheduled_for}</span>
                          </div>
                        </div>
                      )}

                      {/* HITL GOVERNANCE APPROVAL CARD */}
                      {msg.hitlRequest && (
                        <div className="p-3 bg-amber-950/40 rounded-xl border border-amber-800/80 space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <ShieldCheck size={14} className="text-amber-400" />
                              <span className="font-bold text-amber-200 text-xs">
                                Human-in-the-Loop Gate
                              </span>
                            </div>
                            <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-bold ${
                              msg.hitlRequest.status === 'APPROVED'
                                ? 'bg-emerald-900 text-emerald-200'
                                : msg.hitlRequest.status === 'REJECTED'
                                ? 'bg-rose-900 text-rose-200'
                                : 'bg-amber-900 text-amber-200'
                            }`}>
                              {msg.hitlRequest.status}
                            </span>
                          </div>
                          <p className="text-[11px] text-amber-100/90 leading-relaxed">
                            {msg.hitlRequest.summary}
                          </p>

                          {msg.hitlRequest.status === 'PENDING' && (
                            <div className="flex items-center gap-2 pt-1">
                              <button
                                onClick={() => handleHitlDecision(msg.id, msg.hitlRequest!.id, 'APPROVED')}
                                className="flex-1 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-[11px] transition shadow-xs cursor-pointer"
                              >
                                Authorize &amp; Dispatch
                              </button>
                              <button
                                onClick={() => handleHitlDecision(msg.id, msg.hitlRequest!.id, 'REJECTED')}
                                className="py-1.5 px-3 bg-slate-800 hover:bg-rose-900/60 text-slate-300 hover:text-rose-200 border border-slate-700 rounded-lg font-semibold text-[11px] transition cursor-pointer"
                              >
                                Reject
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Action Confirmation Card */}
                      {msg.confirmationCard && (
                        <div className="p-3 bg-slate-900 rounded-xl border border-slate-700 space-y-1.5">
                          <div className="font-semibold text-white flex items-center gap-1.5">
                            <CheckCircle2 size={13} className="text-emerald-400" />
                            {msg.confirmationCard.title}
                          </div>
                          <p className="text-[11px] text-slate-300">
                            {msg.confirmationCard.details}
                          </p>
                        </div>
                      )}

                      {/* Source attribution footer */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="text-[9px] text-slate-500 pt-1 border-t border-slate-800 font-mono">
                          Sources: {msg.sources.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isThinking && (
                  <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
                    <RefreshCw size={14} className="animate-spin text-blue-400" />
                    <span>Executing args_schema verification across mesh...</span>
                  </div>
                )}
              </div>

              {/* Chat Input Bar */}
              <div className="p-3 bg-[#131d33] border-t border-slate-800 flex-shrink-0">
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="space-y-2"
                >
                  <div className="relative flex items-center">
                    <textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={e => setInputValue(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder={`Ask Copilot regarding ${getModuleName(activeTab)}...`}
                      rows={2}
                      className="w-full pl-3 pr-10 py-2 rounded-xl bg-[#0b1120] border border-slate-700/80 text-white placeholder-slate-500 text-xs resize-none focus:outline-hidden focus:border-blue-500 transition"
                    />
                    <button
                      type="submit"
                      disabled={!inputValue.trim() || isThinking}
                      className="absolute right-2.5 top-2.5 p-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-600 disabled:opacity-40 disabled:hover:bg-[#2563eb] text-white transition cursor-pointer"
                    >
                      <Send size={14} />
                    </button>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 px-1">
                    <span>Press Enter to send • Shift+Enter for newline</span>
                    <span className="font-mono text-emerald-400">12 Live Tools</span>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
};
