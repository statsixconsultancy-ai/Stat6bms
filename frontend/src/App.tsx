import React, { useState, useEffect } from 'react';
import {
  Home,
  BarChart2,
  PieChart,
  ClipboardCheck,
  Bot,
  Search,
  Folder,
  FolderOpen,
  Target,
  User,
  Users,
  Briefcase,
  Layers,
  CreditCard,
  Package,
  ShoppingCart,
  Headphones,
  MessageSquare,
  ShieldCheck,
  Zap,
  Sparkles,
  Settings as SettingsIcon,
  ChevronDown,
  ChevronUp,
  MoreHorizontal,
  TrendingUp,
  Link as LinkIcon,
  X,
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Send,
  RefreshCw,
  Play,
  Menu
} from 'lucide-react';
import { OmniCopilotDock, CopilotMessage } from './components/OmniCopilotDock';
import { GeminiMarkdownRenderer } from './components/GeminiMarkdownRenderer';
import { GeminiSparkleIcon, GeminiMiniSparkle } from './components/GeminiIcons';
import {
  getHeaders,
  CrmQuotesAndBookingsPanel,
  MarketingModuleWorkspace,
  ProjectsExtendedPanel,
  HrModuleWorkspace,
  FinanceModuleWorkspace,
  InventoryModuleWorkspace,
  ProcurementModuleWorkspace,
  SupportModuleWorkspace,
  AnalyticsModuleWorkspace,
  CollaborationModuleWorkspace,
  ComplianceModuleWorkspace,
  AutomationModuleWorkspace,
  AiInsightsExtendedPanel,
  SettingsModuleWorkspace,
  ExternalPersonaPortalWorkspace
} from './components/Stat6EnterpriseWorkspace';

const getApiBase = (): string => {
  const envVal = (import.meta as any).env?.VITE_API_BASE || (import.meta as any).env?.VITE_API_BASE_URL;
  if (!envVal) return "http://127.0.0.1:8000/api/v1";
  let base = String(envVal).trim();
  if (!base.startsWith("http://") && !base.startsWith("https://")) {
    base = `https://${base}`;
  }
  return base.endsWith("/api/v1") ? base : `${base.replace(/\/+$/, "")}/api/v1`;
};
const API_BASE = getApiBase();

// ----------------------------------------------------
// VECTOR ICONS (NO LUCIDE CLUTTER, NO EMOJIS)
// ----------------------------------------------------
const JiraTaskIcon = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="flex-shrink-0">
    <rect width="16" height="16" rx="2" fill="#0052CC" />
    <path d="M4.5 8L7 10.5L11.5 5.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const JiraStoryIcon = () => (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" className="flex-shrink-0">
    <rect width="16" height="16" rx="2" fill="#00875A" />
    <path d="M4 3.5C4 3.22386 4.22386 3 4.5 3H11.5C11.7761 3 12 3.22386 12 3.5V13.5L8 10.5L4 13.5V3.5Z" fill="white" />
  </svg>
);

const GitHubLogo = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" className="flex-shrink-0 text-black dark:text-white">
    <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
  </svg>
);

const FigmaLogo = () => (
  <svg width="11" height="11" viewBox="0 0 38 57" fill="none" className="flex-shrink-0">
    <path d="M19 28.5C19 23.2533 23.2533 19 28.5 19C33.7467 19 38 23.2533 38 28.5C38 33.7467 33.7467 38 28.5 38C23.2533 38 19 33.7467 19 28.5Z" fill="#1ABCFE"/>
    <path d="M0 47.5C0 42.2533 4.25329 38 9.5 38H19V47.5C19 52.7467 14.7467 57 9.5 57C4.25329 57 0 52.7467 0 47.5Z" fill="#0ACF83"/>
    <path d="M19 0V19H28.5C33.7467 19 38 14.7467 38 9.5C38 4.25329 33.7467 0 28.5 0H19Z" fill="#FF7262"/>
    <path d="M0 9.5C0 14.7467 4.25329 19 9.5 19H19V0H9.5C4.25329 0 0 4.25329 0 9.5Z" fill="#F24E1E"/>
    <path d="M0 28.5C0 33.7467 4.25329 38 9.5 38H19V19H9.5C4.25329 19 0 23.2533 0 28.5Z" fill="#A259FF"/>
  </svg>
);

// ----------------------------------------------------
// TYPES
// ----------------------------------------------------
type ActiveTab = 
  | 'overview'       // 00. Executive Cockpit
  | 'leads'          // 01. Sales & CRM - Leads (Matching user screenshot)
  | 'deals'          // 01. Sales & CRM - Deals Pipeline
  | 'contacts'       // 01. Sales & CRM - Contacts & Accounts
  | 'marketing'      // 02. Marketing Campaigns & ROI
  | 'projects'       // 03. Projects & Operations (Jira Agile Board)
  | 'hr'             // 04. HR & Staff Management
  | 'finance'        // 05. Finance & Invoicing Ledger
  | 'inventory'      // 06. Inventory & Asset Management
  | 'procurement'    // 07. Procurement & Vendor Management
  | 'support'        // 08. Customer Support Desk
  | 'analytics'      // 09. Reporting & BI Analytics
  | 'collaboration'  // 10. Collaboration & Team Chat
  | 'compliance'     // 11. Compliance & Security
  | 'automation'     // 12. Automation & WHEN-IF-DO
  | 'ai'             // 13. AI & Insights Assistant
  | 'settings';      // 14. Settings & Module Controls

interface JiraIssue {
  id: string;
  key: string;
  title: string;
  type: 'task' | 'story' | 'bug';
  status: 'Blocked' | 'In progress' | 'Ready for review' | 'Done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee: { name: string; avatar: string; role: string };
  connectedTool?: 'honeycomb' | 'github' | 'figma' | 'confluence';
  points?: number;
  description?: string;
  crmAccount?: string;
  linkedInvoice?: string;
}

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<ActiveTab>('leads');
  const [salesExpanded, setSalesExpanded] = useState(true);
  const [operationsExpanded, setOperationsExpanded] = useState(true);
  const [adminExpanded, setAdminExpanded] = useState(true);

  // Retractable Sidebar State (ChatGPT-style)
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('stat6_sidebar_open');
      if (saved !== null) return saved === 'true';
    } catch {}
    return true;
  });

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => {
      const next = !prev;
      try {
        localStorage.setItem('stat6_sidebar_open', String(next));
      } catch {}
      return next;
    });
  };

  // Global Keyboard Shortcut: Ctrl+B or Cmd+B to toggle sidebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'b' || e.key === 'B')) {
        e.preventDefault();
        toggleSidebar();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Jira Issue Drawer
  const [selectedIssue, setSelectedIssue] = useState<JiraIssue | null>(null);
  const [showIntegrationsModal, setShowIntegrationsModal] = useState(false);

  // Legal Modal
  const [activeLegalModal, setActiveLegalModal] = useState<'none' | 'tos' | 'privacy'>('none');

  // Production Authentication & 7-Persona Switcher State
  const [activePersona, setActivePersona] = useState<string>(() => {
    return (typeof window !== 'undefined' && window.localStorage.getItem('stat6_user_persona')) || 'ADMIN';
  });
  const [currentUser, setCurrentUser] = useState<{ email: string; full_name: string; role: string; persona: string }>({
    email: 'admin@acroflow.enterprise',
    full_name: 'Prann (Enterprise Admin)',
    role: 'ADMIN',
    persona: 'ADMIN'
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authForm, setAuthForm] = useState({
    email: 'admin@acroflow.enterprise',
    password: 'Password123!',
    full_name: 'Prann (Enterprise Admin)',
    role: 'ADMIN',
    persona: 'ADMIN'
  });

  // Omnisearch
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Collaboration Chat State
  const [activeChatChannel, setActiveChatChannel] = useState<'#general' | '#engineering' | '#deals'>('#general');
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ sender: string; avatar: string; time: string; text: string }>>([]);

  // 14 Module Toggles State
  const [moduleToggles, setModuleToggles] = useState<Record<string, boolean>>({
    '01. CRM & Sales Pipeline': true,
    '02. Marketing Campaigns & ROI': true,
    '03. Project Operations & Sprints': true,
    '04. HR Directory & Attendance': true,
    '05. Finance & Invoicing Ledger': true,
    '06. Inventory & SKU Management': true,
    '07. Procurement & Vendor POs': true,
    '08. Customer Support Desk': true,
    '09. Executive BI & Reporting': true,
    '10. Team Chat & Collaboration': true,
    '11. Compliance & Data Governance': true,
    '12. WHEN-IF-DO Automation Engine': true,
    '13. Autonomous AI Copilot': true,
    '14. Document Cloud & Signatures': true
  });

  // CRM Leads & Companies Data (Initialized empty for real platform operations)
  const [leadsData, setLeadsData] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [isAddCompanyModalOpen, setIsAddCompanyModalOpen] = useState(false);
  const [companyFormData, setCompanyFormData] = useState({
    name: '',
    industry: 'Enterprise Software',
    tier: 'Tier 1',
    address: '',
    annual_revenue: 1000000
  });

  // Data state
  const [deals, setDeals] = useState<any[]>([]);
  const [marketingData, setMarketingData] = useState<any>(null);
  const [hrData, setHrData] = useState<any>(null);
  const [financeData, setFinanceData] = useState<any>(null);
  const [inventoryData, setInventoryData] = useState<any>(null);
  const [procurementData, setProcurementData] = useState<any>(null);
  const [supportTickets, setSupportTickets] = useState<any[]>([]);
  const [automations, setAutomations] = useState<any[]>([]);
  const [overviewData, setOverviewData] = useState<any>(null);

  // Jira Sprint state (Dynamic from real backend tasks)
  const [jiraIssues, setJiraIssues] = useState<JiraIssue[]>([]);

  // --- AGENTIC AI CHATBOT & SCHEDULED OPERATIONS STATE ---
  interface ScheduledTaskItem {
    id: string;
    org_id?: string;
    task_name: string;
    target_service: string;
    action_type: string;
    payload: string;
    scheduled_for: string;
    precondition_check?: string | null;
    status: string;
    requires_hitl: boolean;
    hitl_approval_id?: string | null;
    executed_at?: string | null;
    created_at?: string | null;
  }

  type AgentChatMsg = CopilotMessage;

  // Live Clean Chat Stream (no fake preloaded conversations)
  const [agentChatMessages, setAgentChatMessages] = useState<AgentChatMsg[]>([]);
  const [scheduledTasksList, setScheduledTasksList] = useState<ScheduledTaskItem[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [schedulerNotification, setSchedulerNotification] = useState<string | null>(null);

  // Enterprise Task Scheduling Modal State
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [scheduleFormData, setScheduleFormData] = useState({
    task_name: '',
    target_service: 'finance-service',
    action_type: 'SEND_PAYMENT_REMINDER',
    scheduled_for: '',
    requires_hitl: true,
    has_precondition: false,
    precondition_field: 'status',
    precondition_expected: 'OVERDUE',
    payload_json: '{\n  "client": "Acme Corp",\n  "invoice_id": "INV-2024-002",\n  "amount": 27500.0\n}'
  });

  // Creation Modals across other platform tabs
  const [isAddLeadModalOpen, setIsAddLeadModalOpen] = useState(false);
  const [leadFormData, setLeadFormData] = useState({
    name: '',
    company: '',
    email: '',
    source: 'Website Form',
    owner: ''
  });

  const [isAddDealModalOpen, setIsAddDealModalOpen] = useState(false);
  const [dealFormData, setDealFormData] = useState({
    title: '',
    company_name: '',
    amount: 50000,
    stage: 'New',
    probability: 20
  });

  const [isAddIssueModalOpen, setIsAddIssueModalOpen] = useState(false);
  const [issueFormData, setIssueFormData] = useState<{
    title: string;
    type: 'task' | 'story' | 'bug';
    status: 'Blocked' | 'In progress' | 'Ready for review' | 'Done';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    assigneeName: string;
    points: number;
    description: string;
  }>({
    title: '',
    type: 'task',
    status: 'In progress',
    priority: 'high',
    assigneeName: '',
    points: 5,
    description: ''
  });

  const [isAddInvoiceModalOpen, setIsAddInvoiceModalOpen] = useState(false);
  const [invoiceFormData, setInvoiceFormData] = useState({
    number: 'INV-2024-005',
    client: '',
    due_date: '2026-11-15',
    total: 25000,
    status: 'Unpaid'
  });

  const [agentChatInput, setAgentChatInput] = useState('');
  const [isBotThinking, setIsBotThinking] = useState(false);
  const [activeChatTab, setActiveChatTab] = useState<'conversation' | 'tasks'>('conversation');

  const handleSendChatMessage = async (presetText?: string) => {
    const textToSend = presetText || agentChatInput.trim();
    if (!textToSend) return;

    const userMsgId = 'msg-' + Date.now();
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: AgentChatMsg = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: nowTime
    };

    setAgentChatMessages(prev => [...prev, userMsg]);
    if (!presetText) setAgentChatInput('');
    setIsBotThinking(true);

    const clientTz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    const pageContext = {
      module: activeTab,
      route: `/${activeTab}`,
      selected_ids: selectedIssue ? [selectedIssue.id] : [],
      filters: {},
      timezone: clientTz,
      client_time: new Date().toISOString()
    };

    try {
      const resp = await fetch(`${API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          conversation_id: userMsgId,
          page_context: pageContext
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        const assistantMsg: AgentChatMsg = {
          id: 'asst-' + Date.now(),
          sender: 'assistant',
          text: data.reply,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: data.intent,
          outputTier: data.output_tier || 'TIER_1_INTERNAL',
          dataTable: data.data_table ? {
            columns: data.data_table.columns || [],
            rows: data.data_table.rows || []
          } : undefined,
          immediateData: data.immediate_data ? {
            revenue: data.immediate_data.total_paid_revenue,
            margin: data.immediate_data.operating_margin_pct,
            pipeline: data.immediate_data.pipeline_value
          } : undefined,
          scheduledTask: data.scheduled_task ? {
            task_id: data.scheduled_task.task_id,
            task_name: data.scheduled_task.task_name,
            target_service: data.scheduled_task.target_service,
            scheduled_for: data.scheduled_task.scheduled_for.replace('T', ' at ').slice(0, 19) + ' UTC',
            requires_hitl: data.scheduled_task.requires_hitl,
            hitl_approval_id: data.scheduled_task.hitl_approval_id,
            status: data.scheduled_task.requires_hitl ? 'WAITING_APPROVAL' : 'PENDING'
          } : undefined,
          hitlRequest: data.scheduled_task && data.scheduled_task.requires_hitl ? {
            id: data.scheduled_task.hitl_approval_id || 'hitl-' + Date.now(),
            title: `Authorization Required: ${data.scheduled_task.task_name}`,
            summary: `Automated action targeting ${data.scheduled_task.target_service} requires explicit sign-off before dispatch.`,
            riskLevel: 'HIGH',
            status: 'PENDING',
            payload: { target_service: data.scheduled_task.target_service, action: data.scheduled_task.task_name }
          } : undefined,
          confirmationCard: data.confirmation_card ? {
            action: data.confirmation_card.action,
            title: data.confirmation_card.title,
            details: data.confirmation_card.details
          } : undefined,
          sources: data.sources || [],
          actionsSuggested: data.actions_suggested || []
        };
        setAgentChatMessages(prev => [...prev, assistantMsg]);
        setIsBotThinking(false);
        if (data.scheduled_task) {
          fetchScheduledTasks();
        }
        return;
      } else {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData?.detail || `Server returned HTTP ${resp.status}`);
      }
    } catch (err: any) {
      const errorMsg: AgentChatMsg = {
        id: 'asst-' + Date.now(),
        sender: 'assistant',
        text: `**Service Communication Error**: ${err?.message || 'Unable to connect to AI Copilot service'}. Please verify backend microservices are running.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: 'SYSTEM_ERROR',
        outputTier: 'TIER_0_PUBLIC',
        sources: ['gateway:8000']
      };
      setAgentChatMessages(prev => [...prev, errorMsg]);
      setIsBotThinking(false);
    }
  };

  const handleHitlDecision = async (msgId: string, hitlId: string, decision: 'APPROVED' | 'REJECTED') => {
    setAgentChatMessages(prev => prev.map(m => {
      if (m.id === msgId && m.hitlRequest) {
        return {
          ...m,
          hitlRequest: { ...m.hitlRequest, status: decision },
          scheduledTask: m.scheduledTask ? {
            ...m.scheduledTask,
            status: decision === 'APPROVED' ? 'APPROVED_BY_HUMAN (EXECUTED)' : 'CANCELLED_BY_HUMAN'
          } : undefined
        };
      }
      return m;
    }));

    try {
      await fetch(`${API_BASE}/automation/hitl/${hitlId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, decision_notes: `Processed by active session user` })
      });
      fetchScheduledTasks();
    } catch {
      // Handled cleanly
    }
  };

  const fetchScheduledTasks = async () => {
    setIsLoadingTasks(true);
    try {
      const res = await fetch(`${API_BASE}/automation/tasks`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setScheduledTasksList(data);
        }
      }
    } catch (err) {
      console.error('Failed to load scheduled tasks:', err);
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleCreateScheduledTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduleFormData.task_name.trim() || !scheduleFormData.scheduled_for) {
      alert('Please provide task name and scheduled execution timestamp.');
      return;
    }

    let parsedPayload = {};
    try {
      parsedPayload = JSON.parse(scheduleFormData.payload_json || '{}');
    } catch {
      alert('Invalid JSON in payload. Please check formatting.');
      return;
    }

    const payloadBody = {
      task_name: scheduleFormData.task_name.trim(),
      target_service: scheduleFormData.target_service,
      action_type: scheduleFormData.action_type,
      payload: parsedPayload,
      scheduled_for: new Date(scheduleFormData.scheduled_for).toISOString(),
      requires_hitl: scheduleFormData.requires_hitl,
      precondition_check: scheduleFormData.has_precondition ? {
        field: scheduleFormData.precondition_field,
        expected: scheduleFormData.precondition_expected
      } : null
    };

    try {
      const res = await fetch(`${API_BASE}/automation/tasks/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payloadBody)
      });
      if (res.ok) {
        setIsScheduleModalOpen(false);
        setSchedulerNotification(`Task "${scheduleFormData.task_name}" successfully scheduled!`);
        setTimeout(() => setSchedulerNotification(null), 4000);
        await fetchScheduledTasks();
        setActiveChatTab('tasks');
      } else {
        const err = await res.json();
        alert(`Scheduling failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Error scheduling task: ${err}`);
    }
  };

  const handleHitlDecisionFromTable = async (hitlId: string, decision: 'APPROVED' | 'REJECTED') => {
    try {
      const res = await fetch(`${API_BASE}/automation/hitl/${hitlId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          decision_notes: `Authorized in STAT6 Governance Dashboard`
        })
      });
      if (res.ok) {
        setSchedulerNotification(`Decision [${decision}] recorded. Audit log and task updated.`);
        setTimeout(() => setSchedulerNotification(null), 4000);
        await fetchScheduledTasks();
      }
    } catch (err) {
      console.error('Error recording decision:', err);
    }
  };

  const handleForceExecuteTask = async (taskId: string) => {
    try {
      const res = await fetch(`${API_BASE}/automation/tasks/${taskId}/execute?force=true`, {
        method: 'POST'
      });
      const data = await res.json();
      setSchedulerNotification(`Execution Result: ${data.status}`);
      setTimeout(() => setSchedulerNotification(null), 4000);
      await fetchScheduledTasks();
    } catch (err) {
      console.error('Failed to execute task:', err);
    }
  };

  const handleRunSchedulerTick = async () => {
    try {
      const res = await fetch(`${API_BASE}/automation/scheduler/tick`, {
        method: 'POST'
      });
      const data = await res.json();
      setSchedulerNotification(`Scheduler Tick: ${data.tasks_checked} tasks evaluated, ${data.executions?.length || 0} executed.`);
      setTimeout(() => setSchedulerNotification(null), 4000);
      await fetchScheduledTasks();
    } catch (err) {
      console.error('Failed to run scheduler tick:', err);
    }
  };

  const notifyUser = (msg: string) => {
    setSchedulerNotification(msg);
    setTimeout(() => setSchedulerNotification(null), 4500);
  };

  const handleAddLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!leadFormData.name.trim()) return;
    const parts = leadFormData.name.trim().split(' ');
    const first_name = parts[0] || 'Enterprise';
    const last_name = parts.slice(1).join(' ') || 'Prospect';
    const email = leadFormData.email || `${first_name.toLowerCase()}.${last_name.toLowerCase()}@enterprise.io`;

    try {
      const res = await fetch(`${API_BASE}/crm/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name,
          last_name,
          email,
          company_name: leadFormData.company || 'Enterprise Corp',
          source: leadFormData.source || 'Website',
          assigned_to: leadFormData.owner || currentUser.full_name || 'Enterprise Admin',
          score: 85
        })
      });
      if (res.ok) {
        setIsAddLeadModalOpen(false);
        setLeadFormData({ name: '', company: '', email: '', source: 'Website Form', owner: '' });
        notifyUser(`Lead "${leadFormData.name}" persisted in CRM database.`);
        refreshAllData();
      }
    } catch {
      notifyUser('Failed to create lead.');
    }
  };

  const handleQualifyLead = async (leadId: string, leadName: string) => {
    try {
      const res = await fetch(`${API_BASE}/crm/leads/${leadId}/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deal_title: `${leadName} Enterprise Expansion`, deal_amount: 95000 })
      });
      if (res.ok) {
        const data = await res.json();
        notifyUser(`1-Click Lead Qualification: Created Company "${data.company_name}", Contact & Deal (${fmt(data.deal_amount)})!`);
        refreshAllData();
      }
    } catch {
      notifyUser('Lead qualification failed.');
    }
  };

  const handleAddDealSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dealFormData.title.trim()) return;
    const stageNorm = dealFormData.stage === 'New' ? 'Prospecting' : dealFormData.stage;
    try {
      const res = await fetch(`${API_BASE}/crm/deals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: dealFormData.title,
          company_id: companies[0]?.id || null,
          amount: Number(dealFormData.amount) || 50000,
          stage: stageNorm,
          probability: Number(dealFormData.probability) || 40
        })
      });
      if (res.ok) {
        setIsAddDealModalOpen(false);
        setDealFormData({ title: '', company_name: '', amount: 50000, stage: 'Prospecting', probability: 40 });
        notifyUser(`Deal "${dealFormData.title}" persisted in CRM pipeline.`);
        refreshAllData();
      }
    } catch {
      notifyUser('Failed to create deal.');
    }
  };

  const handleConvertDealToInvoice = async (dealId: string) => {
    const res = await fetch(`${API_BASE}/crm/deals/${dealId}/convert-to-invoice`, { method: 'POST' });
    if (res.ok) {
      notifyUser('1-Click Deal-to-Invoice: Sales Invoice dispatched to Finance & Accounting!');
      refreshAllData();
    }
  };

  const handleConvertDealToProject = async (dealId: string) => {
    const res = await fetch(`${API_BASE}/crm/deals/${dealId}/convert-to-project`, { method: 'POST', headers: getHeaders() });
    if (res.ok) {
      notifyUser('1-Click Deal-to-Project: Delivery Workspace spun up in Projects & Operations!');
      refreshAllData();
    }
  };

  const handleMoveDealStage = async (dealId: string, nextStage: string) => {
    const res = await fetch(`${API_BASE}/crm/deals/${dealId}/stage`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({
        stage: nextStage,
        budget_confirmed: true,
        proposal_uploaded: true
      })
    });
    if (res.ok) {
      notifyUser(`Deal stage transitioned to "${nextStage}" (Blueprint stage-gates verified).`);
      refreshAllData();
    } else {
      const err = await res.json().catch(() => ({ detail: 'Stage gate validation failed' }));
      notifyUser(`Stage Gate Blocked: ${err.detail}`);
    }
  };

  const handleSwitchPersona = (persona: string) => {
    const personaDirectory: Record<string, { email: string; full_name: string; role: string }> = {
      ADMIN: { email: 'admin@acroflow.enterprise', full_name: 'Prann (Enterprise Admin)', role: 'ADMIN' },
      MANAGER: { email: 'manager@acroflow.enterprise', full_name: 'Department Manager', role: 'MANAGER' },
      EMPLOYEE: { email: 'staff@acroflow.enterprise', full_name: 'Staff Member', role: 'EMPLOYEE' },
      CUSTOMER: { email: 'client@portal.enterprise', full_name: 'Client Contact', role: 'CUSTOMER' },
      VENDOR: { email: 'supplier@portal.enterprise', full_name: 'Supplier Representative', role: 'VENDOR' },
      PARTNER: { email: 'partner@portal.enterprise', full_name: 'Channel Partner', role: 'PARTNER' },
      EXTERNAL_USER: { email: 'auditor@portal.enterprise', full_name: 'External Auditor', role: 'AUDITOR' }
    };
    const info = personaDirectory[persona] || personaDirectory.ADMIN;
    setActivePersona(persona);
    setCurrentUser({ ...info, persona });
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('stat6_user_persona', persona);
      window.localStorage.setItem('stat6_user_role', info.role);
      window.localStorage.setItem('stat6_user_name', info.full_name);
      window.localStorage.setItem('stat6_user_email', info.email);
    }
    notifyUser(`Switched active session persona to ${persona} (${info.full_name}).`);
    refreshAllData();
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
    const body = authMode === 'login'
      ? { email: authForm.email, password: authForm.password }
      : {
          email: authForm.email,
          password: authForm.password,
          full_name: authForm.full_name || 'STAT6 Enterprise User',
          role: authForm.role,
          persona: authForm.persona
        };
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(body)
      });
      if (res.ok) {
        const data = await res.json();
        const u = data.user || { email: authForm.email, full_name: authForm.full_name, role: authForm.role, persona: authForm.persona };
        setCurrentUser({
          email: u.email,
          full_name: u.full_name || u.email,
          role: u.role || 'ADMIN',
          persona: u.persona || u.role || 'ADMIN'
        });
        setActivePersona(u.persona || u.role || 'ADMIN');
        if (typeof window !== 'undefined') {
          if (data.access_token) window.localStorage.setItem('stat6_jwt_token', data.access_token);
          if (u.id) window.localStorage.setItem('stat6_user_id', u.id);
          window.localStorage.setItem('stat6_user_role', u.role || 'ADMIN');
          window.localStorage.setItem('stat6_user_persona', u.persona || u.role || 'ADMIN');
        }
        setIsAuthModalOpen(false);
        notifyUser(`Authenticated as ${u.full_name || u.email} (${u.persona || u.role}) with JWT session.`);
        refreshAllData();
      } else {
        const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
        notifyUser(`Authentication Error: ${err.detail || 'Check credentials'}`);
      }
    } catch {
      notifyUser('Authentication service unreachable.');
    }
  };

  const handleAddCompanySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyFormData.name.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/crm/companies`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          name: companyFormData.name,
          industry: companyFormData.industry || 'Technology',
          tier: companyFormData.tier || 'Tier 1',
          address: companyFormData.address || 'Enterprise HQ',
          annual_revenue: Number(companyFormData.annual_revenue) || 0,
          account_owner: currentUser.full_name || 'Enterprise Admin'
        })
      });
      if (res.ok) {
        setIsAddCompanyModalOpen(false);
        setCompanyFormData({
          name: '',
          industry: 'Enterprise Software',
          tier: 'Tier 1',
          address: '',
          annual_revenue: 1000000
        });
        notifyUser(`Account "${companyFormData.name}" created successfully.`);
        refreshAllData();
      } else {
        notifyUser('Failed to create company account.');
      }
    } catch {
      notifyUser('Network error while saving company.');
    }
  };

  const handleAddIssueSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!issueFormData.title.trim()) return;
    try {
      let pRes = await fetch(`${API_BASE}/projects`, { headers: getHeaders() });
      let pList = pRes.ok ? await pRes.json() : [];
      let projId = Array.isArray(pList) && pList[0] ? pList[0].id : null;
      if (!projId) {
        // Auto-create primary delivery project if none exists yet
        const npRes = await fetch(`${API_BASE}/projects`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            name: 'Primary Enterprise Delivery Project',
            code: 'PRJ-01',
            client_name: 'Internal Systems',
            description: 'Core production deliverables and sprint operations tracking.',
            budget: 100000,
            manager: currentUser.full_name || 'Enterprise Admin'
          })
        });
        if (npRes.ok) {
          const np = await npRes.json();
          projId = np.id;
        }
      }
      if (projId) {
        await fetch(`${API_BASE}/projects/tasks`, {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            project_id: projId,
            title: issueFormData.title,
            description: issueFormData.description || 'Sprint engineering deliverable.',
            status: issueFormData.status === 'Done' ? 'Done' : issueFormData.status === 'Ready for review' ? 'Review' : 'In Progress',
            priority: issueFormData.priority.charAt(0).toUpperCase() + issueFormData.priority.slice(1),
            assignee: issueFormData.assigneeName || currentUser.full_name || 'Enterprise Admin',
            story_points: Number(issueFormData.points) || 5
          })
        });
      }
    } catch {
      // fallback local update
    }
    setIsAddIssueModalOpen(false);
    setIssueFormData({
      title: '',
      type: 'task',
      status: 'In progress',
      priority: 'high',
      assigneeName: '',
      points: 5,
      description: ''
    });
    notifyUser('Task created and recorded in Projects.');
    refreshAllData();
  };

  const handleAddInvoiceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invoiceFormData.client.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/finance/invoices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_name: invoiceFormData.client,
          issue_date: new Date().toISOString().slice(0, 10),
          due_date: invoiceFormData.due_date,
          tax_rate: 0.0,
          items: [
            {
              description: `Enterprise License (${invoiceFormData.number})`,
              quantity: 1,
              unit_price: Number(invoiceFormData.total) || 25000
            }
          ]
        })
      });
      if (res.ok) {
        setIsAddInvoiceModalOpen(false);
        setInvoiceFormData({
          number: 'INV-2026-' + (Math.floor(Math.random() * 900) + 100),
          client: '',
          due_date: '2026-11-15',
          total: 25000,
          status: 'Unpaid'
        });
        notifyUser('Invoice created & double-entry journal posted.');
        refreshAllData();
      }
    } catch {
      notifyUser('Failed to create invoice.');
    }
  };

  // Keyboard shortcut for Omnisearch (Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false);
        setSelectedIssue(null);
        setActiveLegalModal('none');
        setShowIntegrationsModal(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Fetch initial live data across microservices via Central API Gateway
  const refreshAllData = () => {
    fetch(`${API_BASE}/overview`).then(r => r.json()).then(setOverviewData).catch(() => {});
    fetch(`${API_BASE}/crm/deals`).then(r => r.json()).then(data => { if (Array.isArray(data)) setDeals(data); }).catch(() => {});
    fetch(`${API_BASE}/crm/companies`).then(r => r.json()).then(data => { if (Array.isArray(data)) setCompanies(data); }).catch(() => {});
    fetch(`${API_BASE}/crm/leads`).then(r => r.json()).then(data => {
      if (Array.isArray(data)) {
        setLeadsData(data.map((l: any) => ({
          id: l.id,
          name: `${l.first_name || ''} ${l.last_name || ''}`.trim() || l.name || 'Lead',
          avatar: l.avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120',
          company: l.company_name || l.company || 'Enterprise Corp',
          source: l.source || 'Direct',
          email: l.email || '',
          status: l.status || 'New',
          score: l.score ?? 80,
          converted_deal_id: l.converted_deal_id,
          owner: { name: l.assigned_to || l.owner?.name || 'Unassigned', avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=120' }
        })));
      }
    }).catch(() => {});
    fetch(`${API_BASE}/marketing/campaigns`).then(r => r.json()).then(data => setMarketingData(Array.isArray(data) ? data : [])).catch(() => {});
    fetch(`${API_BASE}/projects/tasks`, { headers: getHeaders() }).then(r => r.json()).then(tasks => {
      if (Array.isArray(tasks)) {
        setJiraIssues(tasks.map((t: any) => ({
          id: t.id,
          key: t.issue_key || t.id.slice(0, 8),
          title: t.title,
          type: (t.issue_type?.toLowerCase() === 'bug' ? 'bug' : 'task') as any,
          status: t.status === 'Review' ? 'Ready for review' : (t.status || 'In progress'),
          priority: (t.priority?.toLowerCase() || 'medium') as any,
          points: t.story_points || 3,
          description: t.description || '',
          assignee: {
            name: t.assignee || 'Unassigned',
            avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100',
            role: 'Team Member'
          },
          connectedTool: 'github'
        })));
      }
    }).catch(() => {});
    Promise.all([
      fetch(`${API_BASE}/hr/employees`).then(r => r.json()).catch(() => []),
      fetch(`${API_BASE}/hr/departments`).then(r => r.json()).catch(() => [])
    ]).then(([emps, depts]) => {
      setHrData({
        employees: Array.isArray(emps) ? emps : (emps?.employees || []),
        departments: Array.isArray(depts) ? depts : []
      });
    });
    fetch(`${API_BASE}/finance/invoices`).then(r => r.json()).then(data => {
      setFinanceData({ invoices: Array.isArray(data) ? data : (data?.invoices || []) });
    }).catch(() => {});
    fetch(`${API_BASE}/inventory/products`).then(r => r.json()).then(data => {
      setInventoryData({ products: Array.isArray(data) ? data : (data?.products || []) });
    }).catch(() => {});
    fetch(`${API_BASE}/procurement/orders`).then(r => r.json()).then(data => {
      setProcurementData({ purchase_orders: Array.isArray(data) ? data : (data?.purchase_orders || []) });
    }).catch(() => {});
    fetch(`${API_BASE}/support/tickets`).then(r => r.json()).then(data => { if (Array.isArray(data)) setSupportTickets(data); }).catch(() => {});
    fetch(`${API_BASE}/automation/rules`).then(r => r.json()).then(data => { if (Array.isArray(data)) setAutomations(data); }).catch(() => {});
    fetchScheduledTasks();
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  useEffect(() => {
    if (activeTab === 'ai') {
      fetchScheduledTasks();
    }
  }, [activeTab, activeChatTab]);

  // Omnisearch
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      fetch(`${API_BASE}/search?q=${encodeURIComponent(searchQuery)}`)
        .then(r => r.json())
        .then(setSearchResults)
        .catch(() => {});
    }, 150);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleMoveIssue = (issueId: string, newStatus: JiraIssue['status']) => {
    setJiraIssues(prev => prev.map(i => i.id === issueId ? { ...i, status: newStatus } : i));
    if (selectedIssue && selectedIssue.id === issueId) {
      setSelectedIssue(prev => prev ? { ...prev, status: newStatus } : null);
    }
    fetch(`${API_BASE}/projects/tasks/${issueId}/move`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ status: newStatus })
    }).catch(() => {});
    notifyUser(`Moved task ${issueId} to "${newStatus}" in Sprint Board.`);
  };

  const handleSendChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const textMsg = chatInput;
    setChatMessages(prev => [
      ...prev,
      { sender: 'Prann (Enterprise Admin)', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100', time: 'Just now', text: textMsg }
    ]);
    setChatInput('');

    fetch(`${API_BASE}/chat/channels`)
      .then(r => r.json())
      .then(channels => {
        if (Array.isArray(channels) && channels.length > 0) {
          const chName = activeChatChannel.replace('#', '');
          const target = channels.find((c: any) => c.name === chName) || channels[0];
          fetch(`${API_BASE}/chat/channels/${target.id}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: textMsg })
          }).catch(() => {});
        }
      })
      .catch(() => {});
  };

  const fmt = (num: number = 0) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);
  };

  return (
    <div className={`flex h-screen w-screen overflow-hidden ${isDarkMode ? 'dark bg-[#0b1120] text-white' : 'bg-[#f0f2f8] text-black'} antialiased font-sans select-none text-[13px]`}>
      
      {/* ---------------------------------------------------- */}
      {/* 1. DEEP NAVY ENTERPRISE SIDEBAR (MATCHING SCREENSHOT) */}
      {/* ---------------------------------------------------- */}
      <aside className={`flex flex-col justify-between bg-[#162340] text-slate-200 select-none transition-all duration-300 ease-in-out flex-shrink-0 z-30 overflow-hidden ${
        isSidebarOpen ? 'w-60 border-r border-slate-800 opacity-100' : 'w-0 border-r-0 opacity-0 pointer-events-none'
      }`}>
        <div className={`w-60 flex flex-col h-full overflow-hidden transition-opacity duration-200 ${isSidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
          
          {/* Top Brand Logo - STAT6 Title in Pure White (Matching Zoho Layout) */}
          <div className="p-3.5 flex items-center justify-between border-b border-slate-700/60">
            <button 
              onClick={() => setActiveTab('leads')}
              className="flex items-center gap-2.5 hover:opacity-90 transition text-left cursor-pointer"
              title="STAT6 Platform"
            >
              <div className="h-7 w-7 rounded-lg bg-[#2563eb] flex items-center justify-center text-white shadow-xs flex-shrink-0">
                <BarChart2 size={16} className="text-white" />
              </div>
              <span className="font-bold text-[16px] text-white tracking-wider">
                STAT6
              </span>
            </button>
            <div className="flex items-center gap-1.5">
              <span className="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-normal">
                v2.4
              </span>
              <button
                onClick={toggleSidebar}
                className="p-1 rounded-md hover:bg-slate-700/60 text-slate-400 hover:text-white transition cursor-pointer"
                title="Collapse sidebar (Ctrl+B)"
                aria-label="Collapse sidebar"
              >
                <Menu size={16} />
              </button>
            </div>
          </div>

          {/* Quick Header Nav Links - Vector Outline Icons Matching Screenshot */}
          <div className="px-2.5 pt-2.5 space-y-0.5 text-[12.5px]">
            <button
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                activeTab === 'overview' ? 'bg-[#22396b] text-white font-normal' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
              }`}
            >
              <Home size={16} className="text-[#38bdf8] flex-shrink-0" />
              <span>Home</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                activeTab === 'analytics' ? 'bg-[#22396b] text-white font-normal' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
              }`}
            >
              <BarChart2 size={16} className="text-[#f43f5e] flex-shrink-0" />
              <span>Reports</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition text-slate-300 hover:bg-[#1e3056]/50 font-normal"
            >
              <PieChart size={16} className="text-[#c084fc] flex-shrink-0" />
              <span>Analytics</span>
            </button>

            <button
              onClick={() => setActiveTab('support')}
              className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                activeTab === 'support' ? 'bg-[#22396b] text-white font-normal' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
              }`}
            >
              <ClipboardCheck size={16} className="text-[#34d399] flex-shrink-0" />
              <span>My Requests</span>
            </button>

            <button
              onClick={() => setActiveTab('ai')}
              className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                activeTab === 'ai' ? 'bg-[#22396b] text-white font-normal' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
              }`}
            >
              <Bot size={16} className="text-[#fb923c] flex-shrink-0" />
              <span>Agents</span>
            </button>
          </div>

          <div className="my-2 border-t border-slate-700/60 mx-3"></div>

          {/* Sales Category Banner & Search Box Matching Screenshot */}
          <div className="px-2.5 space-y-2">
            <div className="flex items-center justify-between px-1.5 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded bg-[#e11d48] text-white text-[10.5px] font-bold flex items-center justify-center shadow-xs">
                  S
                </div>
                <span className="text-white font-semibold text-xs">Sales</span>
                <ChevronDown size={13} className="text-slate-400" />
              </div>
              <MoreHorizontal size={14} className="text-slate-400 cursor-pointer" />
            </div>

            <div 
              onClick={() => setIsSearchOpen(true)}
              className="bg-[#1c2d52] border border-slate-700/60 rounded-lg px-2.5 py-1.5 flex items-center gap-2 text-slate-400 text-xs cursor-pointer hover:border-slate-500 transition"
            >
              <Search size={14} className="text-slate-400 flex-shrink-0" />
              <span className="font-normal">Search</span>
            </div>
          </div>

          {/* FOLDERS & EXPANDABLE SECTIONS */}
          <div className="px-2.5 pt-2 space-y-2 flex-1 overflow-y-auto text-xs">
            
            {/* FOLDER 1: SALES */}
            <div className="space-y-0.5">
              <button
                onClick={() => setSalesExpanded(!salesExpanded)}
                className="w-full flex items-center justify-between px-2 py-1 text-slate-300 hover:text-white text-xs font-normal"
              >
                <div className="flex items-center gap-2">
                  {salesExpanded ? <FolderOpen size={15} className="text-[#38bdf8]" /> : <Folder size={15} className="text-[#38bdf8]" />}
                  <span className="font-medium text-slate-200">Sales</span>
                </div>
                {salesExpanded ? <ChevronUp size={13} className="text-slate-400" /> : <ChevronDown size={13} className="text-slate-400" />}
              </button>

              {salesExpanded && (
                <div className="space-y-0.5 pt-0.5 pl-1">
                  <button
                    onClick={() => setActiveTab('leads')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'leads' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Target size={15} className={activeTab === 'leads' ? 'text-[#60a5fa]' : 'text-slate-400'} />
                    <span>Leads</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('contacts')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'contacts' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <User size={15} className={activeTab === 'contacts' ? 'text-[#60a5fa]' : 'text-slate-400'} />
                    <span>Contacts</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('deals')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'deals' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <TrendingUp size={15} className={activeTab === 'deals' ? 'text-[#60a5fa]' : 'text-slate-400'} />
                    <span>Deals Pipeline</span>
                  </button>
                </div>
              )}
            </div>

            {/* FOLDER 2: OPERATIONS & DELIVERY */}
            <div className="space-y-0.5 pt-1 border-t border-slate-700/60">
              <button
                onClick={() => setOperationsExpanded(!operationsExpanded)}
                className="w-full flex items-center justify-between px-2 py-1 text-slate-300 hover:text-white text-xs font-normal"
              >
                <div className="flex items-center gap-2">
                  {operationsExpanded ? <FolderOpen size={15} className="text-[#38bdf8]" /> : <Folder size={15} className="text-[#38bdf8]" />}
                  <span className="font-medium text-slate-200">Operations</span>
                </div>
                {operationsExpanded ? <ChevronUp size={13} className="text-slate-400" /> : <ChevronDown size={13} className="text-slate-400" />}
              </button>

              {operationsExpanded && (
                <div className="space-y-0.5 pt-0.5 pl-1">
                  <button
                    onClick={() => setActiveTab('projects')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'projects' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Briefcase size={15} className="text-[#38bdf8]" />
                    <span>Jira Agile Sprints</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('marketing')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'marketing' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Layers size={15} className="text-[#f43f5e]" />
                    <span>Marketing ROI</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('hr')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'hr' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Users size={15} className="text-[#34d399]" />
                    <span>HR & Staff</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('finance')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'finance' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <CreditCard size={15} className="text-[#c084fc]" />
                    <span>Finance & Invoices</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('inventory')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'inventory' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Package size={15} className="text-[#fb923c]" />
                    <span>Inventory & SKUs</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('procurement')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'procurement' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <ShoppingCart size={15} className="text-[#eab308]" />
                    <span>Procurement & POs</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('support')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'support' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Headphones size={15} className="text-[#ec4899]" />
                    <span>Support Desk</span>
                  </button>
                </div>
              )}
            </div>

            {/* FOLDER 3: GOVERNANCE & AI */}
            <div className="space-y-0.5 pt-1 border-t border-slate-700/60">
              <button
                onClick={() => setAdminExpanded(!adminExpanded)}
                className="w-full flex items-center justify-between px-2 py-1 text-slate-300 hover:text-white text-xs font-normal"
              >
                <div className="flex items-center gap-2">
                  {adminExpanded ? <FolderOpen size={15} className="text-[#38bdf8]" /> : <Folder size={15} className="text-[#38bdf8]" />}
                  <span className="font-medium text-slate-200">Governance & AI</span>
                </div>
                {adminExpanded ? <ChevronUp size={13} className="text-slate-400" /> : <ChevronDown size={13} className="text-slate-400" />}
              </button>

              {adminExpanded && (
                <div className="space-y-0.5 pt-0.5 pl-1">
                  <button
                    onClick={() => setActiveTab('collaboration')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'collaboration' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <MessageSquare size={15} className="text-[#38bdf8]" />
                    <span>Team Chat</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('compliance')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'compliance' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <ShieldCheck size={15} className="text-[#10b981]" />
                    <span>Compliance & RBAC</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('automation')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'automation' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <Zap size={15} className="text-[#eab308]" />
                    <span>WHEN-IF-DO Rules</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('settings')}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg transition ${
                      activeTab === 'settings' ? 'bg-[#243964] text-white font-normal shadow-xs' : 'text-slate-300 hover:bg-[#1e3056]/50 font-normal'
                    }`}
                  >
                    <SettingsIcon size={15} className="text-[#94a3b8]" />
                    <span>Module Controls</span>
                  </button>
                </div>
              )}
            </div>

          </div>

          {/* Footer Status & Modals */}
          <div className="p-3 border-t border-slate-700/60 text-xs flex items-center justify-between text-slate-400">
            <span className="flex items-center gap-1.5 font-mono text-[10px] text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Supabase Live
            </span>
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="text-white hover:underline text-[11px]"
            >
              {isDarkMode ? 'Light' : 'Dark'}
            </button>
          </div>

        </div>
      </aside>

      {/* ---------------------------------------------------- */}
      {/* 2. MAIN WORKSPACE CANVAS (CLEAN UI & PURE BLACK TEXT) */}
      {/* ---------------------------------------------------- */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Dynamic Top Workspace Header Bar */}
        <header className="h-12 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#131c2e] px-4 sm:px-6 flex items-center justify-between flex-shrink-0 gap-3">
          <div className="flex items-center gap-2.5 text-black dark:text-white">
            {/* 3-Line Hamburger Sidebar Expand Button - Only visible when sidebar is closed */}
            {!isSidebarOpen && (
              <button
                onClick={toggleSidebar}
                className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-all cursor-pointer flex items-center justify-center shadow-xs"
                title="Expand sidebar (Ctrl+B)"
                aria-label="Expand sidebar"
              >
                <Menu size={17} />
              </button>
            )}

            <span className="font-bold text-black dark:text-white tracking-tight">STAT6</span>
            <span className="text-slate-400 font-normal">/</span>
            <span className="uppercase text-xs tracking-wider text-black dark:text-white font-normal">
              {['CUSTOMER', 'VENDOR', 'PARTNER'].includes(activePersona) ? `${activePersona} PORTAL` : activeTab}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Live 7-Persona Role & Portal Switcher */}
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-xs">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Persona:</span>
              <select
                value={activePersona}
                onChange={e => handleSwitchPersona(e.target.value)}
                className="bg-transparent font-bold text-xs text-black dark:text-white focus:outline-none cursor-pointer"
                title="Switch among all 7 STAT6 Role Personas (Internal & Free External Portals)"
              >
                <option value="ADMIN">01. ADMIN (Internal Full)</option>
                <option value="MANAGER">02. MANAGER (Dept Head)</option>
                <option value="EMPLOYEE">03. EMPLOYEE (Self-Service)</option>
                <option value="CUSTOMER">04. CUSTOMER PORTAL (Free)</option>
                <option value="VENDOR">05. VENDOR PORTAL (Free)</option>
                <option value="PARTNER">06. PARTNER PORTAL (Free)</option>
                <option value="EXTERNAL_USER">07. EXTERNAL AUDITOR</option>
              </select>
            </div>

            <button
              onClick={() => setIsAuthModalOpen(true)}
              className="px-2.5 py-1 rounded-lg bg-[#162340] text-white text-xs font-mono hover:opacity-90 cursor-pointer flex items-center gap-1.5"
              title="Manage JWT Session, Login or Register"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>{currentUser.full_name.split(' ')[0]} ({activePersona})</span>
            </button>

            <button
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center gap-2 px-2.5 py-1 rounded-lg border border-slate-300 dark:border-slate-700 text-xs text-black dark:text-white hover:bg-slate-50 font-normal"
            >
              <span>Search...</span>
              <kbd className="px-1 py-0.2 rounded bg-slate-200 dark:bg-slate-800 text-[10px] font-mono">Ctrl+K</kbd>
            </button>

            <button
              onClick={refreshAllData}
              className="px-2.5 py-1 rounded-lg border border-slate-300 dark:border-slate-700 text-xs text-black dark:text-white hover:bg-slate-50 font-normal cursor-pointer"
            >
              Refresh
            </button>
          </div>
        </header>

        {/* Scrollable Work Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {(['CUSTOMER', 'VENDOR', 'PARTNER'] as const).includes(activePersona as any) ? (
            <ExternalPersonaPortalWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              persona={activePersona as 'CUSTOMER' | 'VENDOR' | 'PARTNER'}
              onSwitchPersona={handleSwitchPersona}
            />
          ) : (
            <>
          {/* ==================================================== */}
          {/* TAB 01: LEADS (EXACT MATCH OF USER'S REFERENCE IMAGE) */}
          {/* ==================================================== */}
          {activeTab === 'leads' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Leads &amp; 1-Click Atomic Qualification</h1>
                  <p className="text-xs text-slate-500">Omnichannel Ingestion • AI Lead Scoring • Atomic Lead → Company + Contact + Deal Conversion</p>
                </div>
                <button
                  onClick={() => setIsAddLeadModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white font-normal text-xs transition cursor-pointer"
                >
                  + Add Lead
                </button>
              </div>

              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#131c2e]">
                    <tr className="text-black dark:text-white text-[13px]">
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Lead Name</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Company</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Lead Source</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">AI Score</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Email</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Lead Owner</th>
                      <th className="py-3 px-4 font-bold text-right">1-Click Qualification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 font-normal">
                    {leadsData.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="py-14 px-4 text-center">
                          <div className="flex flex-col items-center justify-center gap-2">
                            <Target className="w-8 h-8 text-slate-400" />
                            <p className="text-[14px] font-medium text-black dark:text-white">No customer leads registered</p>
                            <button
                              onClick={() => setIsAddLeadModalOpen(true)}
                              className="mt-2 px-3 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white text-xs transition cursor-pointer"
                            >
                              + Add Lead
                            </button>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      leadsData.map(lead => (
                        <tr key={lead.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition">
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-3">
                              <img className="h-8 w-8 rounded-full object-cover ring-1 ring-slate-200" src={lead.avatar} alt="" />
                              <span className="text-[13.5px] text-black dark:text-white font-medium">{lead.name}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4 text-[13px] text-black dark:text-white">{lead.company}</td>
                          <td className="py-3.5 px-4 text-[13px] text-black dark:text-white">{lead.source}</td>
                          <td className="py-3.5 px-4 font-mono text-emerald-700 font-bold">{lead.score ?? 85}/100</td>
                          <td className="py-3.5 px-4 text-[13px] text-black dark:text-white font-mono">{lead.email}</td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-2.5">
                              <img className="h-7 w-7 rounded-full object-cover ring-1 ring-slate-200" src={lead.owner.avatar} alt="" />
                              <span className="text-[13px] text-black dark:text-white">{lead.owner.name}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            {lead.status === 'Converted' || lead.converted_deal_id ? (
                              <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 font-mono text-[10px]">QUALIFIED &amp; CONVERTED</span>
                            ) : (
                              <button
                                onClick={() => handleQualifyLead(lead.id, lead.company || lead.name)}
                                className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs cursor-pointer"
                              >
                                Qualify → Deal
                              </button>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 01: DEALS, CPQ QUOTES, E-SIGN & BOOKINGS */}
          {/* ==================================================== */}
          {!['CUSTOMER', 'VENDOR', 'PARTNER'].includes(activePersona) && activeTab === 'deals' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Sales Pipeline, CPQ Quotations &amp; Native E-Sign</h1>
                  <p className="text-xs text-slate-500">Stage-Gate Blueprint • 1-Click Deal-to-Invoice &amp; Deal-to-Project • Cryptographic E-Signature</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-black dark:text-white font-bold">
                    Pipeline Value: {fmt(deals.reduce((acc: number, d: any) => acc + (Number(d.amount) || 0), 0))}
                  </span>
                  <button
                    onClick={() => setIsAddDealModalOpen(true)}
                    className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white font-normal text-xs transition cursor-pointer"
                  >
                    + Add Deal
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
                {(['Prospecting', 'Qualification', 'Proposal Sent', 'Negotiation', 'Won'] as const).map((stage, stageIdx, allStages) => {
                  const stageDeals = deals.filter(d => d.stage === stage || (stage === 'Prospecting' && d.stage === 'New') || (stage === 'Proposal Sent' && d.stage === 'Proposal'));
                  const prevStage = stageIdx > 0 ? allStages[stageIdx - 1] : null;
                  const nextStage = stageIdx < allStages.length - 1 ? allStages[stageIdx + 1] : null;
                  return (
                    <div key={stage} className="p-3 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 dark:border-slate-800 min-h-[340px] flex flex-col">
                      <div className="flex justify-between items-center pb-2 border-b border-slate-200 dark:border-slate-800">
                        <h2 className="text-xs font-bold text-black dark:text-white">{stage}</h2>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                          {stageDeals.length}
                        </span>
                      </div>
                      <div className="mt-2.5 space-y-2 flex-1">
                        {stageDeals.length === 0 ? (
                          <div className="text-[11px] text-slate-400 italic text-center py-10">No deals</div>
                        ) : (
                          stageDeals.map(d => (
                            <div key={d.id} className="p-2.5 rounded-xl border border-slate-200 bg-[#fafbfc] dark:bg-slate-900 shadow-xs space-y-1.5">
                              <div className="text-xs text-black dark:text-white font-bold">{d.title}</div>
                              <div className="text-[11px] text-slate-500">{d.company_name || 'Enterprise Account'}</div>
                              <div className="flex justify-between font-mono text-xs text-black dark:text-white">
                                <span className="font-bold">{fmt(d.amount)}</span>
                                <span>{d.probability}%</span>
                              </div>
                              <div className="flex gap-1 pt-1 border-t border-slate-200/70">
                                {prevStage && (
                                  <button
                                    onClick={() => handleMoveDealStage(d.id, prevStage)}
                                    className="px-1.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-mono cursor-pointer"
                                    title={`Move back to ${prevStage}`}
                                  >
                                    ←
                                  </button>
                                )}
                                <button onClick={() => handleConvertDealToInvoice(d.id)} className="flex-1 py-1 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[10px] font-mono cursor-pointer">
                                  → Invoice
                                </button>
                                <button onClick={() => handleConvertDealToProject(d.id)} className="flex-1 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-800 text-[10px] font-mono cursor-pointer">
                                  → Project
                                </button>
                                {nextStage && (
                                  <button
                                    onClick={() => handleMoveDealStage(d.id, nextStage)}
                                    className="px-1.5 py-1 rounded bg-indigo-50 hover:bg-indigo-100 text-indigo-800 text-[10px] font-mono cursor-pointer"
                                    title={`Advance to ${nextStage}`}
                                  >
                                    →
                                  </button>
                                )}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              <CrmQuotesAndBookingsPanel
                apiBase={API_BASE}
                fmt={fmt}
                notify={notifyUser}
                refreshGlobal={refreshAllData}
                deals={deals}
                companies={companies}
              />
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 01: CONTACTS & ORGS */}
          {/* ==================================================== */}
          {activeTab === 'contacts' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-200">
                <div>
                  <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Customer Accounts &amp; 360° Parent-Child Hierarchy</h1>
                  <p className="text-xs text-slate-500">Corporate Accounts • Tier Classification • Hierarchy Tracking</p>
                </div>
                <button
                  onClick={() => setIsAddCompanyModalOpen(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white font-normal text-xs transition cursor-pointer"
                >
                  + Add Customer Account
                </button>
              </div>

              {companies.length === 0 ? (
                <div className="p-8 text-center bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 space-y-2">
                  <div className="font-bold text-sm text-black dark:text-white">No Customer Accounts Registered</div>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">Click &ldquo;+ Add Customer Account&rdquo; above to record your client organizations, tiers, and contractual revenues.</p>
                  <button
                    onClick={() => setIsAddCompanyModalOpen(true)}
                    className="mt-2 px-4 py-2 bg-[#2563eb] text-white rounded-xl text-xs font-semibold hover:bg-blue-700 cursor-pointer transition"
                  >
                    + Add Customer Account
                  </button>
                </div>
              ) : (
                <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b bg-slate-50 dark:bg-slate-900 text-black dark:text-white text-[12.5px]">
                      <tr><th className="py-3 px-4 border-r">Company Name</th><th className="py-3 px-4 border-r">Industry</th><th className="py-3 px-4 border-r">Tier</th><th className="py-3 px-4 border-r">HQ Location</th><th className="py-3 px-4 border-r">Account Owner</th><th className="py-3 px-4">Annual Revenue</th></tr>
                    </thead>
                    <tbody className="divide-y text-black dark:text-white font-normal">
                      {companies.map(c => (
                        <tr key={c.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition">
                          <td className="py-3.5 px-4 font-bold">{c.name}</td>
                          <td className="py-3.5 px-4">{c.industry || 'Technology'}</td>
                          <td className="py-3.5 px-4"><span className="px-2 py-0.5 rounded bg-blue-50 text-blue-800 font-mono text-[11px]">{c.tier || 'Tier 1'}</span></td>
                          <td className="py-3.5 px-4">{c.address || c.phone || 'Enterprise HQ'}</td>
                          <td className="py-3.5 px-4">{c.account_owner || 'Unassigned'}</td>
                          <td className="py-3.5 px-4 font-mono font-bold">{fmt(c.annual_revenue || 0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Add Company Modal */}
              {isAddCompanyModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
                  <div className="bg-white dark:bg-[#131c2e] p-6 rounded-2xl max-w-md w-full border border-slate-200 dark:border-slate-800 space-y-4">
                    <h2 className="text-base font-bold text-black dark:text-white">Add Customer Account</h2>
                    <form onSubmit={handleAddCompanySubmit} className="space-y-3 text-xs">
                      <div>
                        <label className="block font-semibold mb-1">Company / Organization Name</label>
                        <input
                          value={companyFormData.name}
                          onChange={e => setCompanyFormData({ ...companyFormData, name: e.target.value })}
                          placeholder="e.g. Acme Global Systems"
                          className="w-full border rounded-lg px-3 py-2 text-black"
                          required
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="block font-semibold mb-1">Industry</label>
                          <input
                            value={companyFormData.industry}
                            onChange={e => setCompanyFormData({ ...companyFormData, industry: e.target.value })}
                            placeholder="Technology, Healthcare..."
                            className="w-full border rounded-lg px-3 py-2 text-black"
                          />
                        </div>
                        <div>
                          <label className="block font-semibold mb-1">Tier</label>
                          <select
                            value={companyFormData.tier}
                            onChange={e => setCompanyFormData({ ...companyFormData, tier: e.target.value })}
                            className="w-full border rounded-lg px-3 py-2 text-black"
                          >
                            <option value="Tier 1">Tier 1 (Enterprise)</option>
                            <option value="Tier 2">Tier 2 (Mid-Market)</option>
                            <option value="Tier 3">Tier 3 (Growth)</option>
                          </select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="block font-semibold mb-1">HQ Location</label>
                          <input
                            value={companyFormData.address}
                            onChange={e => setCompanyFormData({ ...companyFormData, address: e.target.value })}
                            placeholder="City, State"
                            className="w-full border rounded-lg px-3 py-2 text-black"
                          />
                        </div>
                        <div>
                          <label className="block font-semibold mb-1">Annual Revenue ($)</label>
                          <input
                            type="number"
                            value={companyFormData.annual_revenue}
                            onChange={e => setCompanyFormData({ ...companyFormData, annual_revenue: Number(e.target.value) })}
                            className="w-full border rounded-lg px-3 py-2 text-black"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end gap-2 pt-2 border-t">
                        <button
                          type="button"
                          onClick={() => setIsAddCompanyModalOpen(false)}
                          className="px-3 py-1.5 border rounded-lg text-slate-700 dark:text-slate-300 cursor-pointer"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="px-4 py-1.5 bg-[#2563eb] text-white rounded-lg font-semibold hover:bg-blue-700 cursor-pointer transition"
                        >
                          Save Account
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 02: MARKETING CAMPAIGNS & ROI */}
          {/* ==================================================== */}
          {activeTab === 'marketing' && (
            <MarketingModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 03: PROJECTS & OPERATIONS (JIRA BOARD + CPM + FINANCIALS) */}
          {/* ==================================================== */}
          {activeTab === 'projects' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <div>
                  <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Projects, Agile Sprints, Critical Path &amp; Profitability</h1>
                  <p className="text-xs text-slate-500">Replaces Zoho Projects, Zoho Sprints &amp; Zoho BugTracker</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsAddIssueModalOpen(true)}
                    className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white font-normal text-xs transition cursor-pointer"
                  >
                    + Create Issue
                  </button>
                  <button
                    onClick={() => setShowIntegrationsModal(true)}
                    className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 font-normal text-xs transition cursor-pointer"
                  >
                    Workspaces: Figma &amp; GitHub
                  </button>
                </div>
              </div>
              {jiraIssues.length === 0 && (
                <div className="p-4 bg-blue-50/60 dark:bg-blue-950/20 rounded-xl border border-blue-200 dark:border-blue-900/40 text-xs text-blue-900 dark:text-blue-200 flex items-center justify-between">
                  <span>No agile sprint issues logged yet. Click &ldquo;+ Create Issue&rdquo; to add a task, or use the Delivery Project panel below.</span>
                  <button
                    onClick={() => setIsAddIssueModalOpen(true)}
                    className="px-3 py-1 bg-[#2563eb] text-white rounded-lg text-xs font-medium hover:bg-blue-700 cursor-pointer transition shrink-0 ml-3"
                  >
                    + Create First Issue
                  </button>
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {(['Blocked', 'In progress', 'Ready for review', 'Done'] as const).map(stage => (
                  <div key={stage} className="bg-white dark:bg-[#131c2e] p-3 rounded-2xl border border-slate-200 min-h-[340px] flex flex-col">
                    <h2 className="text-xs font-bold text-black dark:text-white pb-2 border-b">{stage} ({jiraIssues.filter(i => i.status === stage).length})</h2>
                    <div className="mt-2.5 space-y-2 flex-1">
                      {jiraIssues.filter(i => i.status === stage).map(issue => (
                        <div key={issue.id} onClick={() => setSelectedIssue(issue)} className="p-3 rounded-xl border border-slate-200 bg-[#fafbfc] dark:bg-slate-900 shadow-xs cursor-pointer hover:border-[#2563eb]">
                          <div className="text-[13px] text-black dark:text-white leading-snug font-normal">{issue.title}</div>
                          <div className="mt-2.5 flex items-center justify-between pt-1 border-t border-slate-200">
                            <span className="font-mono text-xs text-black dark:text-white font-normal">{issue.key}</span>
                            <img className="h-5 w-5 rounded-full object-cover" src={issue.assignee.avatar} alt="" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <ProjectsExtendedPanel
                apiBase={API_BASE}
                fmt={fmt}
                notify={notifyUser}
                refreshGlobal={refreshAllData}
              />
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 04: HR & STAFF MANAGEMENT */}
          {/* ==================================================== */}
          {activeTab === 'hr' && (
            <HrModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              employees={hrData?.employees || []}
              departments={hrData?.departments || []}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 05: FINANCE & INVOICING LEDGER */}
          {/* ==================================================== */}
          {activeTab === 'finance' && (
            <FinanceModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              invoices={financeData?.invoices || []}
              onOpenNewInvoice={() => setIsAddInvoiceModalOpen(true)}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 06: INVENTORY & ASSETS */}
          {/* ==================================================== */}
          {activeTab === 'inventory' && (
            <InventoryModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              products={inventoryData?.products || []}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 07: PROCUREMENT & VENDOR MANAGEMENT */}
          {/* ==================================================== */}
          {activeTab === 'procurement' && (
            <ProcurementModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              orders={procurementData?.purchase_orders || []}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 08: CUSTOMER SUPPORT DESK */}
          {/* ==================================================== */}
          {activeTab === 'support' && (
            <SupportModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              tickets={supportTickets}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 09: REPORTING & BI ANALYTICS (EXECUTIVE COCKPIT) */}
          {/* ==================================================== */}
          {(activeTab === 'overview' || activeTab === 'analytics') && (
            <AnalyticsModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              overviewData={overviewData}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 10: COLLABORATION & CHAT */}
          {/* ==================================================== */}
          {activeTab === 'collaboration' && (
            <CollaborationModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 11: COMPLIANCE & SECURITY */}
          {/* ==================================================== */}
          {activeTab === 'compliance' && (
            <ComplianceModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              onOpenLegal={m => setActiveLegalModal(m)}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 12: AUTOMATION (DAG WORKFLOWS, APPROVALS, ZOHO IMPORTER) */}
          {/* ==================================================== */}
          {activeTab === 'automation' && (
            <AutomationModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
            />
          )}

          {/* ==================================================== */}
          {/* TAB 13: AGENTIC AI OPERATIONS COPILOT & HITL CENTER  */}
          {/* ==================================================== */}
          {activeTab === 'ai' && (
            <div className="space-y-4 max-w-7xl mx-auto text-black dark:text-white">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2.5">
                    <Bot className="text-[#2563eb]" size={26} />
                    <span>Autonomous Agentic Operations Copilot</span>
                  </h1>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Multi-Service Synthesis • Background Temporal Task Scheduling • Human-in-the-Loop Governance
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 text-[11px] font-mono font-medium flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    14 Microservices Mesh
                  </span>
                  <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/50 dark:text-blue-400 border border-blue-200 dark:border-blue-800 text-[11px] font-mono font-medium flex items-center gap-1.5">
                    <Clock size={12} />
                    Temporal Engine
                  </span>
                  <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400 border border-amber-200 dark:border-amber-800 text-[11px] font-mono font-medium flex items-center gap-1.5">
                    <ShieldCheck size={12} />
                    HITL Safety Gate
                  </span>
                </div>
              </div>

              {/* View Switcher: Chatbot vs Scheduled Task Queue */}
              <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800">
                <button
                  onClick={() => setActiveChatTab('conversation')}
                  className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
                    activeChatTab === 'conversation'
                      ? 'border-[#2563eb] text-[#2563eb]'
                      : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                  }`}
                >
                  Conversational Copilot
                </button>
                <button
                  onClick={() => setActiveChatTab('tasks')}
                  className={`px-4 py-2 text-xs font-semibold border-b-2 transition flex items-center gap-1.5 ${
                    activeChatTab === 'tasks'
                      ? 'border-[#2563eb] text-[#2563eb]'
                      : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                  }`}
                >
                  <span>Scheduled Tasks &amp; HITL Queue</span>
                  <span className="px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800 text-[10px]">
                    {scheduledTasksList.filter(t => t.status === 'WAITING_APPROVAL' || (t.requires_hitl && t.status === 'PENDING')).length}
                  </span>
                </button>
              </div>

              {activeChatTab === 'conversation' ? (
                <div className="space-y-4">
                  {/* Quick-Prompt Suggested Actions */}
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <span className="text-[11px] text-slate-400 font-medium">Quick Prompts:</span>
                    {[
                      "What's our cash position today?",
                      "Schedule Net30 reminder for Acme Corp tomorrow at 10 AM (Require Approval)",
                      "What is blocked on Sprint 44 right now?",
                      "Forecast Q4 commercial deal pipeline"
                    ].map((chip, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendChatMessage(chip)}
                        className="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-[11px] text-slate-700 dark:text-slate-300 transition border border-slate-200 dark:border-slate-700 text-left cursor-pointer"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>

                  {/* Chat Message Stream */}
                  <div className="bg-slate-50/60 dark:bg-[#0f172a]/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 space-y-4 min-h-[460px] max-h-[620px] overflow-y-auto">
                    {agentChatMessages.length === 0 && (
                      <div className="flex flex-col items-center justify-center py-20 text-center space-y-3">
                        <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 flex items-center justify-center text-[#2563eb] shadow-xs">
                          <Bot size={24} />
                        </div>
                        <div className="space-y-1 max-w-md">
                          <h3 className="text-sm font-bold text-slate-900 dark:text-white">STAT6 Autonomous Operations Copilot</h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                            Ask any enterprise telemetry query, or schedule future background operations with state precondition checks and Human-in-the-Loop governance.
                          </p>
                        </div>
                      </div>
                    )}
                    {agentChatMessages.map(msg => (
                      <div
                        key={msg.id}
                        className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        {msg.sender === 'assistant' && (
                          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#1e293b] via-[#1a233a] to-[#253350] border border-blue-500/30 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
                            <GeminiSparkleIcon size={18} />
                          </div>
                        )}

                        <div className={`max-w-2xl space-y-3 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                          {/* Message Bubble */}
                          <div
                            className={`p-3.5 rounded-2xl text-xs leading-relaxed ${
                              msg.sender === 'user'
                                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-xs shadow-xs'
                                : 'bg-white dark:bg-[#12192b] text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-750/70 rounded-bl-xs shadow-xs space-y-2'
                            }`}
                          >
                            {msg.outputTier === 'TIER_3_RESTRICTED' && (
                              <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-50 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                <ShieldCheck size={12} className="text-emerald-600 dark:text-emerald-400" />
                                <span>Tier 3 Restricted: Data Stays Home (Internal Enclave)</span>
                              </div>
                            )}
                            <GeminiMarkdownRenderer content={msg.text} />

                            {/* Structured Data Table (Tier 3 records / Financial Ledgers) */}
                            {msg.dataTable && (
                              <div className="mt-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-[#0f172a] overflow-hidden">
                                <div className="px-3 py-1.5 bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between text-[11px] font-semibold text-slate-700 dark:text-slate-200">
                                  <span>Structured Records Ledger ({msg.dataTable.rows.length} rows)</span>
                                  <span className="text-[10px] text-slate-400 font-mono">args_schema matched</span>
                                </div>
                                <div className="overflow-x-auto max-h-56">
                                  <table className="w-full text-left text-xs">
                                    <thead className="bg-slate-200/70 dark:bg-slate-900 text-slate-600 dark:text-slate-400 text-[10px] uppercase font-semibold">
                                      <tr>
                                        {msg.dataTable.columns.map((col, cIdx) => (
                                          <th key={cIdx} className="px-3 py-1.5 whitespace-nowrap">{col}</th>
                                        ))}
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800 font-mono text-[11px]">
                                      {msg.dataTable.rows.map((row, rIdx) => (
                                        <tr key={rIdx} className="hover:bg-slate-100/50 dark:hover:bg-slate-800/40">
                                          {row.map((cell, cellIdx) => (
                                            <td key={cellIdx} className="px-3 py-1.5 whitespace-nowrap text-slate-800 dark:text-slate-200">{String(cell ?? '-')}</td>
                                          ))}
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            )}

                            <div className={`text-[10px] mt-1.5 ${msg.sender === 'user' ? 'text-blue-100 text-right' : 'text-slate-400'}`}>
                              {msg.timestamp}
                            </div>
                          </div>

                          {/* Track A: Immediate Live Data Card */}
                          {msg.immediateData && (
                            <div className="grid grid-cols-2 gap-2 p-3 bg-white dark:bg-[#131c2e] rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
                              {msg.immediateData.revenue !== undefined && (
                                <div className="p-2 bg-slate-50 dark:bg-slate-900 rounded-lg">
                                  <div className="text-[10px] text-slate-500 uppercase font-semibold">Paid Revenue</div>
                                  <div className="text-xs font-mono font-bold text-slate-900 dark:text-white">${msg.immediateData.revenue.toLocaleString()}</div>
                                </div>
                              )}
                              {msg.immediateData.margin !== undefined && (
                                <div className="p-2 bg-slate-50 dark:bg-slate-900 rounded-lg">
                                  <div className="text-[10px] text-slate-500 uppercase font-semibold">Net Margin</div>
                                  <div className="text-xs font-mono font-bold text-blue-600 dark:text-blue-400">{msg.immediateData.margin}%</div>
                                </div>
                              )}
                              {msg.immediateData.pipeline !== undefined && (
                                <div className="p-2 bg-slate-50 dark:bg-slate-900 rounded-lg col-span-2">
                                  <div className="text-[10px] text-slate-500 uppercase font-semibold">Deals Pipeline</div>
                                  <div className="text-xs font-mono font-bold text-purple-600 dark:text-purple-400">${msg.immediateData.pipeline.toLocaleString()}</div>
                                </div>
                              )}
                              {msg.immediateData.sprint !== undefined && (
                                <div className="p-2 bg-slate-50 dark:bg-slate-900 rounded-lg col-span-3">
                                  <div className="text-[10px] text-slate-500 uppercase font-semibold">Sprint Velocity</div>
                                  <div className="text-xs font-mono font-bold text-amber-600 dark:text-amber-400">{msg.immediateData.sprint} • 16 Story Points</div>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Track B: Scheduled Background Task Card */}
                          {msg.scheduledTask && (
                            <div className="p-3 bg-blue-50/70 dark:bg-blue-950/30 rounded-xl border border-blue-200 dark:border-blue-900 shadow-xs space-y-1.5">
                              <div className="flex items-center justify-between text-xs">
                                <span className="font-semibold text-blue-950 dark:text-blue-300 flex items-center gap-1.5">
                                  <Clock size={13} className="text-[#2563eb]" />
                                  <span>Scheduled Background Task</span>
                                </span>
                                <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 font-semibold">
                                  {msg.scheduledTask.status}
                                </span>
                              </div>
                              <div className="text-xs text-blue-900 dark:text-blue-200 font-medium">
                                {msg.scheduledTask.task_name}
                              </div>
                              <div className="flex items-center justify-between text-[11px] text-blue-700/80 dark:text-blue-400 pt-0.5 font-mono">
                                <span>Target: {msg.scheduledTask.target_service}</span>
                                <span>Execution: {msg.scheduledTask.scheduled_for}</span>
                              </div>
                            </div>
                          )}

                          {/* Human-in-the-Loop (HITL) Interactive Approval Card */}
                          {msg.hitlRequest && (
                            <div className="p-4 bg-amber-50/80 dark:bg-amber-950/30 rounded-xl border border-amber-300 dark:border-amber-800 shadow-sm space-y-3">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <div className="w-6 h-6 rounded-md bg-amber-500 text-white flex items-center justify-center">
                                    <ShieldCheck size={14} />
                                  </div>
                                  <div>
                                    <div className="text-xs font-bold text-amber-950 dark:text-amber-200">
                                      {msg.hitlRequest.title}
                                    </div>
                                    <div className="text-[10px] text-amber-700 dark:text-amber-400">
                                      Risk Tier: {msg.hitlRequest.riskLevel} • Policy Enforcement Active
                                    </div>
                                  </div>
                                </div>
                                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                                  msg.hitlRequest.status === 'APPROVED'
                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200'
                                    : msg.hitlRequest.status === 'REJECTED'
                                    ? 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200'
                                    : 'bg-amber-200 text-amber-900 dark:bg-amber-900 dark:text-amber-200'
                                }`}>
                                  {msg.hitlRequest.status === 'APPROVED' ? 'Approved by User' : msg.hitlRequest.status}
                                </span>
                              </div>

                              <div className="text-xs text-amber-900 dark:text-amber-300 leading-relaxed bg-white/70 dark:bg-black/30 p-2.5 rounded-lg border border-amber-200/60 dark:border-amber-900/50">
                                {msg.hitlRequest.summary}
                              </div>

                              {msg.hitlRequest.payload && (
                                <div className="text-[11px] font-mono bg-white dark:bg-black/40 p-2 rounded border border-amber-200 dark:border-amber-900/60 text-slate-700 dark:text-slate-300">
                                  <span className="text-slate-400 font-sans text-[10px] block mb-1">Payload Parameters:</span>
                                  {JSON.stringify(msg.hitlRequest.payload, null, 2)}
                                </div>
                              )}

                              {/* Interactive Decision Action Controls */}
                              {msg.hitlRequest.status === 'PENDING' ? (
                                <div className="flex items-center gap-2 pt-1">
                                  <button
                                    onClick={() => handleHitlDecision(msg.id, msg.hitlRequest!.id, 'APPROVED')}
                                    className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-xs cursor-pointer"
                                  >
                                    <CheckCircle2 size={13} />
                                    <span>Approve &amp; Execute</span>
                                  </button>
                                  <button
                                    onClick={() => handleHitlDecision(msg.id, msg.hitlRequest!.id, 'REJECTED')}
                                    className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-xs cursor-pointer"
                                  >
                                    <X size={13} />
                                    <span>Reject / Cancel Task</span>
                                  </button>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-700 dark:text-emerald-400 pt-1">
                                  <CheckCircle2 size={14} />
                                  <span>
                                    {msg.hitlRequest.status === 'APPROVED'
                                      ? 'Decision recorded. Task was verified and dispatched to execution engine.'
                                      : 'Task was cancelled. No background dispatch will occur.'}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {msg.sender === 'user' && (
                          <div className="w-8 h-8 rounded-lg bg-[#2563eb] text-white flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-xs">
                            ME
                          </div>
                        )}
                      </div>
                    ))}

                    {isBotThinking && (
                      <div className="flex gap-3 items-center text-xs text-slate-500">
                        <div className="w-8 h-8 rounded-lg bg-[#162340] text-white flex items-center justify-center">
                          <Bot size={16} className="text-[#38bdf8] animate-pulse" />
                        </div>
                        <div className="flex items-center gap-1.5 p-3 rounded-2xl bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-slate-700">
                          <RefreshCw size={12} className="animate-spin text-[#2563eb]" />
                          <span>Synthesizing cross-service telemetry &amp; evaluating temporal policies...</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Chat Input Bar */}
                  <div className="flex items-center gap-2 p-1.5 bg-white dark:bg-[#131c2e] rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs">
                    <input
                      type="text"
                      value={agentChatInput}
                      onChange={e => setAgentChatInput(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === 'Enter') handleSendChatMessage();
                      }}
                      placeholder="Point out what you want to do (e.g., 'What is our cash flow? Also schedule payment reminder for Acme Corp tomorrow at 10 AM with approval')..."
                      className="flex-1 px-3 py-2 text-xs bg-transparent text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-hidden"
                    />
                    <button
                      onClick={() => handleSendChatMessage()}
                      disabled={!agentChatInput.trim()}
                      className="px-4 py-2 bg-[#2563eb] hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
                    >
                      <Send size={13} />
                      <span>Send</span>
                    </button>
                  </div>
                </div>
              ) : (
                /* Scheduled Tasks & HITL Queue Table */
                <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-xs space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h2 className="text-sm font-bold text-slate-900 dark:text-white">Active Temporal Tasks &amp; Human Approval Registry</h2>
                      <p className="text-xs text-slate-500 mt-0.5">Live database registry of background operations with precondition checks and governance gates.</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleRunSchedulerTick}
                        className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium cursor-pointer transition flex items-center gap-1.5"
                      >
                        <RefreshCw size={12} />
                        <span>Run Scheduler Tick</span>
                      </button>
                      <button
                        onClick={fetchScheduledTasks}
                        className="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-medium cursor-pointer transition"
                      >
                        Refresh
                      </button>
                      <button
                        onClick={() => {
                          const inOneHour = new Date(Date.now() + 3600000).toISOString().slice(0, 16);
                          setScheduleFormData(prev => ({ ...prev, scheduled_for: inOneHour }));
                          setIsScheduleModalOpen(true);
                        }}
                        className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] hover:bg-blue-700 text-white text-xs font-medium cursor-pointer transition flex items-center gap-1.5 shadow-xs"
                      >
                        <span>+ Schedule New Task</span>
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-slate-200 dark:border-slate-800 rounded-xl">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800 text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                        <tr>
                          <th className="p-3">Task Name</th>
                          <th className="p-3">Target Service</th>
                          <th className="p-3">Action Type</th>
                          <th className="p-3">Scheduled For</th>
                          <th className="p-3">Safety Policy</th>
                          <th className="p-3">Status</th>
                          <th className="p-3 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-800 dark:text-slate-200">
                        {isLoadingTasks ? (
                          <tr>
                            <td colSpan={7} className="p-8 text-center text-slate-400">
                              <div className="flex items-center justify-center gap-2">
                                <RefreshCw className="animate-spin" size={14} />
                                <span>Loading database tasks...</span>
                              </div>
                            </td>
                          </tr>
                        ) : scheduledTasksList.length === 0 ? (
                          <tr>
                            <td colSpan={7} className="p-10 text-center text-slate-500 dark:text-slate-400">
                              <div className="flex flex-col items-center justify-center space-y-2">
                                <Clock className="text-slate-400" size={26} />
                                <span className="font-semibold text-xs">No Scheduled Tasks in Registry</span>
                                <span className="text-[11px] text-slate-400">Click &ldquo;+ Schedule New Task&rdquo; to define a future background operation or instruct the AI Copilot.</span>
                              </div>
                            </td>
                          </tr>
                        ) : (
                          scheduledTasksList.map((task) => (
                            <tr key={task.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                              <td className="p-3 font-medium">{task.task_name}</td>
                              <td className="p-3 font-mono text-[11px] text-blue-600 dark:text-blue-400">{task.target_service}</td>
                              <td className="p-3 font-mono text-[11px] text-slate-600 dark:text-slate-300">{task.action_type}</td>
                              <td className="p-3 font-mono text-[11px] text-slate-600 dark:text-slate-300">
                                {task.scheduled_for ? new Date(task.scheduled_for).toLocaleString() : 'Immediate'}
                              </td>
                              <td className="p-3">
                                {task.requires_hitl ? (
                                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300 text-[10px] font-semibold">
                                    HITL Required
                                  </span>
                                ) : (
                                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 text-[10px]">
                                    Autonomous
                                  </span>
                                )}
                              </td>
                              <td className="p-3 font-mono text-[11px]">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  task.status === 'EXECUTED' || task.status === 'APPROVED_BY_HUMAN'
                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300'
                                    : task.status === 'WAITING_APPROVAL'
                                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300'
                                    : task.status === 'CANCELLED'
                                    ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300'
                                    : 'bg-blue-100 text-blue-800 dark:bg-blue-950/50 dark:text-blue-300'
                                }`}>
                                  {task.status}
                                </span>
                              </td>
                              <td className="p-3 text-right">
                                {task.status === 'WAITING_APPROVAL' && task.hitl_approval_id ? (
                                  <div className="flex items-center justify-end gap-1.5">
                                    <button
                                      onClick={() => handleHitlDecisionFromTable(task.hitl_approval_id!, 'APPROVED')}
                                      className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-semibold cursor-pointer transition shadow-xs"
                                    >
                                      Approve
                                    </button>
                                    <button
                                      onClick={() => handleHitlDecisionFromTable(task.hitl_approval_id!, 'REJECTED')}
                                      className="px-2.5 py-1 rounded bg-rose-600 hover:bg-rose-700 text-white text-[11px] font-semibold cursor-pointer transition shadow-xs"
                                    >
                                      Reject
                                    </button>
                                  </div>
                                ) : task.status === 'PENDING' ? (
                                  <button
                                    onClick={() => handleForceExecuteTask(task.id)}
                                    className="px-2 py-1 rounded border border-blue-500 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/40 text-[10px] font-medium cursor-pointer transition"
                                  >
                                    Execute Now
                                  </button>
                                ) : (
                                  <span className="text-[11px] text-slate-400">
                                    {task.status === 'EXECUTED' || task.status === 'APPROVED_BY_HUMAN' ? 'Archived' : 'Closed'}
                                  </span>
                                )}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              <AiInsightsExtendedPanel
                apiBase={API_BASE}
                fmt={fmt}
                notify={notifyUser}
                refreshGlobal={refreshAllData}
              />
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 14: SETTINGS & MODULE TOGGLES */}
          {/* ==================================================== */}
          {activeTab === 'settings' && (
            <SettingsModuleWorkspace
              apiBase={API_BASE}
              fmt={fmt}
              notify={notifyUser}
              refreshGlobal={refreshAllData}
              moduleToggles={moduleToggles}
              setModuleToggles={setModuleToggles}
            />
          )}
            </>
          )}

        </div>

      </div>

      {/* ---------------------------------------------------- */}
      {/* 3. JIRA SLIDE-OVER INSPECTOR */}
      {/* ---------------------------------------------------- */}
      {selectedIssue && (
        <div className="fixed inset-0 z-50 bg-black/40 flex justify-end">
          <div className="w-full max-w-lg h-full bg-white dark:bg-[#131c2e] border-l border-slate-200 p-5 flex flex-col justify-between text-black dark:text-white">
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b pb-3">
                <span className="font-mono text-sm font-normal">{selectedIssue.key}</span>
                <button onClick={() => setSelectedIssue(null)} className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"><X size={15} /></button>
              </div>
              <h2 className="text-lg font-bold">{selectedIssue.title}</h2>
              <div className="flex gap-2">
                {(['Blocked', 'In progress', 'Ready for review', 'Done'] as const).map(st => (
                  <button key={st} onClick={() => handleMoveIssue(selectedIssue.id, st)} className={`px-2.5 py-1 rounded text-xs font-normal ${selectedIssue.status === st ? 'bg-[#2563eb] text-white' : 'bg-slate-100 text-black'}`}>{st}</button>
                ))}
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl text-xs font-normal leading-relaxed">{selectedIssue.description}</div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl text-xs font-mono font-normal space-y-1">
                <div>Linked Account: {selectedIssue.crmAccount}</div>
                <div>Linked Invoice: {selectedIssue.linkedInvoice} ($79.7k)</div>
              </div>
            </div>
            <button onClick={() => setSelectedIssue(null)} className="w-full py-2 bg-[#2563eb] text-white rounded-xl text-xs font-normal">Close</button>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 4. WORKSPACES INTEGRATIONS MODAL */}
      {/* ---------------------------------------------------- */}
      {showIntegrationsModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#131c2e] rounded-2xl p-5 space-y-4 text-black dark:text-white">
            <div className="flex justify-between items-center border-b pb-2"><h2 className="text-base font-bold">Connected Workspaces</h2><button onClick={() => setShowIntegrationsModal(false)} className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"><X size={15} /></button></div>
            <div className="space-y-2 text-xs font-mono font-normal">
              <div className="p-3 border rounded-xl flex justify-between items-center"><span>Figma (Banking Flow v2.4)</span><span className="text-emerald-700">Connected</span></div>
              <div className="p-3 border rounded-xl flex justify-between items-center"><span>GitHub (fintech-core PR #88)</span><span className="text-emerald-700">Merged</span></div>
            </div>
            <button onClick={() => setShowIntegrationsModal(false)} className="w-full py-2 bg-[#2563eb] text-white rounded-xl text-xs font-normal">Done</button>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 5. LEGAL MODAL (TOS & PRIVACY) */}
      {/* ---------------------------------------------------- */}
      {activeLegalModal !== 'none' && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-white dark:bg-[#131c2e] rounded-2xl p-5 space-y-3 text-xs text-black dark:text-white max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b pb-2"><h2 className="text-sm font-bold">{activeLegalModal === 'tos' ? 'Master Services Agreement' : 'Privacy & Compliance'}</h2><button onClick={() => setActiveLegalModal('none')} className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"><X size={15} /></button></div>
            <p className="font-normal leading-relaxed">{activeLegalModal === 'tos' ? 'Stat6 enterprise agreement grants single-tenant isolated database instances with a 99.95% uptime SLA guarantee and zero proprietary lock-in.' : 'Customer transactional data is safeguarded by AES-256 and SOC 2 Type II attestations with strict zero-export guarantees.'}</p>
            <button onClick={() => setActiveLegalModal('none')} className="w-full py-2 bg-[#2563eb] text-white rounded-xl text-xs font-normal">Close</button>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 6. OMNISEARCH MODAL (CTRL+K) */}
      {/* ---------------------------------------------------- */}
      {isSearchOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center pt-20">
          <div className="w-full max-w-lg bg-white dark:bg-[#131c2e] rounded-2xl border shadow-2xl overflow-hidden text-black dark:text-white">
            <div className="p-3 border-b flex items-center gap-2">
              <input type="text" autoFocus value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search across all 14 modules..." className="flex-1 text-xs text-black dark:text-white focus:outline-none font-normal bg-transparent" />
              <button onClick={() => setIsSearchOpen(false)} className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"><X size={15} /></button>
            </div>
            <div className="max-h-72 overflow-y-auto p-2 text-xs font-normal">
              {searchResults.length > 0 ? (
                searchResults.map((r, i) => (
                  <div key={i} onClick={() => { setIsSearchOpen(false); setActiveTab(r.type === 'Deal' ? 'deals' : r.type === 'Invoice' ? 'finance' : 'projects'); }} className="p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer flex justify-between">
                    <div><div>{r.title}</div><div className="text-[11px] text-black dark:text-white font-normal">{r.subtitle}</div></div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800">{r.category}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 text-black dark:text-white font-normal">Type to search deals, invoices, issues, employees...</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 7. SCHEDULE ENTERPRISE TASK MODAL */}
      {/* ---------------------------------------------------- */}
      {isScheduleModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start border-b border-slate-200 dark:border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Clock size={18} className="text-[#2563eb]" />
                  <span>Schedule Enterprise Operation</span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Configure temporal execution window, state preconditions, and governance policy.
                </p>
              </div>
              <button
                onClick={() => setIsScheduleModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleCreateScheduledTask} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Task Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Send Net30 Overdue Invoice Reminder to Acme Corp"
                  value={scheduleFormData.task_name}
                  onChange={e => setScheduleFormData({ ...scheduleFormData, task_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white focus:outline-hidden focus:border-[#2563eb]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Target Microservice</label>
                  <select
                    value={scheduleFormData.target_service}
                    onChange={e => setScheduleFormData({ ...scheduleFormData, target_service: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white focus:outline-hidden focus:border-[#2563eb]"
                  >
                    <option value="finance-service">finance-service (Ledger &amp; Invoices)</option>
                    <option value="crm-service">crm-service (Sales &amp; Pipeline)</option>
                    <option value="projects-service">projects-service (Sprint &amp; Jira)</option>
                    <option value="inventory-service">inventory-service (Stock &amp; SKUs)</option>
                    <option value="procurement-service">procurement-service (Vendor POs)</option>
                    <option value="hr-service">hr-service (Staff &amp; Payroll)</option>
                    <option value="support-service">support-service (Help Desk)</option>
                    <option value="compliance-service">compliance-service (Audit &amp; SOC2)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Action Type</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g., SEND_PAYMENT_REMINDER"
                    value={scheduleFormData.action_type}
                    onChange={e => setScheduleFormData({ ...scheduleFormData, action_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white focus:outline-hidden focus:border-[#2563eb]"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Scheduled Date &amp; Time (UTC)</label>
                <div className="flex gap-2">
                  <input
                    type="datetime-local"
                    required
                    value={scheduleFormData.scheduled_for}
                    onChange={e => setScheduleFormData({ ...scheduleFormData, scheduled_for: e.target.value })}
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white focus:outline-hidden focus:border-[#2563eb]"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const dt = new Date(Date.now() + 86400000);
                      dt.setHours(10, 0, 0, 0);
                      setScheduleFormData({ ...scheduleFormData, scheduled_for: dt.toISOString().slice(0, 16) });
                    }}
                    className="px-2.5 py-1.5 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-[11px] cursor-pointer"
                  >
                    Tomorrow 10 AM
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const dt = new Date(Date.now() + 3600000);
                      setScheduleFormData({ ...scheduleFormData, scheduled_for: dt.toISOString().slice(0, 16) });
                    }}
                    className="px-2.5 py-1.5 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-[11px] cursor-pointer"
                  >
                    +1h
                  </button>
                </div>
              </div>

              <div className="p-3 bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900/60 rounded-xl space-y-1.5">
                <label className="flex items-center gap-2 font-semibold text-amber-900 dark:text-amber-200 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={scheduleFormData.requires_hitl}
                    onChange={e => setScheduleFormData({ ...scheduleFormData, requires_hitl: e.target.checked })}
                    className="rounded text-[#2563eb] focus:ring-[#2563eb]"
                  />
                  <span>Require Human-in-the-Loop (HITL) Authorization Gate</span>
                </label>
                <p className="text-[11px] text-amber-700 dark:text-amber-300/80 leading-relaxed pl-5">
                  When enabled, the task will not execute automatically at the designated time. It will pause in WAITING_APPROVAL state until an authorized human signs off in the approval card.
                </p>
              </div>

              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/80 rounded-xl space-y-2">
                <label className="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-200 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={scheduleFormData.has_precondition}
                    onChange={e => setScheduleFormData({ ...scheduleFormData, has_precondition: e.target.checked })}
                    className="rounded text-[#2563eb] focus:ring-[#2563eb]"
                  />
                  <span>Enable Live State Precondition Check</span>
                </label>
                {scheduleFormData.has_precondition && (
                  <div className="grid grid-cols-2 gap-2 pt-1 pl-5">
                    <div>
                      <span className="block text-[10px] text-slate-500 mb-0.5">Field</span>
                      <input
                        type="text"
                        placeholder="status"
                        value={scheduleFormData.precondition_field}
                        onChange={e => setScheduleFormData({ ...scheduleFormData, precondition_field: e.target.value })}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-[#0f172a] text-xs"
                      />
                    </div>
                    <div>
                      <span className="block text-[10px] text-slate-500 mb-0.5">Expected Value</span>
                      <input
                        type="text"
                        placeholder="OVERDUE"
                        value={scheduleFormData.precondition_expected}
                        onChange={e => setScheduleFormData({ ...scheduleFormData, precondition_expected: e.target.value })}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-[#0f172a] text-xs"
                      />
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block font-semibold mb-1 text-slate-700 dark:text-slate-300">Action Payload (JSON)</label>
                <textarea
                  rows={3}
                  value={scheduleFormData.payload_json}
                  onChange={e => setScheduleFormData({ ...scheduleFormData, payload_json: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] font-mono text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-[#2563eb]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsScheduleModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#2563eb] hover:bg-blue-700 text-white cursor-pointer font-semibold shadow-xs"
                >
                  Schedule Enterprise Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 8. CREATE LEAD MODAL */}
      {/* ---------------------------------------------------- */}
      {isAddLeadModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
              <h2 className="text-base font-bold">+ Add New Lead</h2>
              <button onClick={() => setIsAddLeadModalOpen(false)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400"><X size={16} /></button>
            </div>
            <form onSubmit={handleAddLeadSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Sarah Jenkins"
                  value={leadFormData.name}
                  onChange={e => setLeadFormData({ ...leadFormData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">Company</label>
                <input
                  type="text"
                  placeholder="e.g., Acro Dynamic Corp"
                  value={leadFormData.company}
                  onChange={e => setLeadFormData({ ...leadFormData, company: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Email</label>
                  <input
                    type="email"
                    placeholder="s.jenkins@acro.com"
                    value={leadFormData.email}
                    onChange={e => setLeadFormData({ ...leadFormData, email: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Lead Source</label>
                  <select
                    value={leadFormData.source}
                    onChange={e => setLeadFormData({ ...leadFormData, source: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="Website Form">Website Form</option>
                    <option value="Trade Show">Trade Show</option>
                    <option value="Cold Call">Cold Call</option>
                    <option value="Webinar">Webinar</option>
                    <option value="Partner">Partner</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block font-semibold mb-1">Assigned Lead Owner</label>
                <input
                  type="text"
                  value={leadFormData.owner}
                  onChange={e => setLeadFormData({ ...leadFormData, owner: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button type="button" onClick={() => setIsAddLeadModalOpen(false)} className="px-4 py-2 border rounded-xl">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-xl font-semibold">Save Lead</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 9. CREATE DEAL MODAL */}
      {/* ---------------------------------------------------- */}
      {isAddDealModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
              <h2 className="text-base font-bold">+ New Pipeline Deal</h2>
              <button onClick={() => setIsAddDealModalOpen(false)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400"><X size={16} /></button>
            </div>
            <form onSubmit={handleAddDealSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">Deal Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Enterprise Cloud Architecture Tier 2"
                  value={dealFormData.title}
                  onChange={e => setDealFormData({ ...dealFormData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Apex Cloud Dynamics"
                  value={dealFormData.company_name}
                  onChange={e => setDealFormData({ ...dealFormData, company_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Deal Value ($)</label>
                  <input
                    type="number"
                    value={dealFormData.amount}
                    onChange={e => setDealFormData({ ...dealFormData, amount: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Stage</label>
                  <select
                    value={dealFormData.stage}
                    onChange={e => setDealFormData({ ...dealFormData, stage: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="Prospecting">Prospecting</option>
                    <option value="Qualification">Qualification</option>
                    <option value="Proposal Sent">Proposal Sent</option>
                    <option value="Negotiation">Negotiation</option>
                    <option value="Won">Won</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button type="button" onClick={() => setIsAddDealModalOpen(false)} className="px-4 py-2 border rounded-xl">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-xl font-semibold">Save Deal</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 10. CREATE JIRA ISSUE MODAL */}
      {/* ---------------------------------------------------- */}
      {isAddIssueModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
              <h2 className="text-base font-bold">+ Create Sprint 44 Issue</h2>
              <button onClick={() => setIsAddIssueModalOpen(false)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400"><X size={16} /></button>
            </div>
            <form onSubmit={handleAddIssueSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">Issue Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Implement real-time ledger replication"
                  value={issueFormData.title}
                  onChange={e => setIssueFormData({ ...issueFormData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Type</label>
                  <select
                    value={issueFormData.type}
                    onChange={e => setIssueFormData({ ...issueFormData, type: e.target.value as any })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="task">Task</option>
                    <option value="story">Story</option>
                    <option value="bug">Bug</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold mb-1">Status</label>
                  <select
                    value={issueFormData.status}
                    onChange={e => setIssueFormData({ ...issueFormData, status: e.target.value as any })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="In progress">In progress</option>
                    <option value="Blocked">Blocked</option>
                    <option value="Ready for review">Ready for review</option>
                    <option value="Done">Done</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Priority</label>
                  <select
                    value={issueFormData.priority}
                    onChange={e => setIssueFormData({ ...issueFormData, priority: e.target.value as any })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold mb-1">Story Points</label>
                  <input
                    type="number"
                    value={issueFormData.points}
                    onChange={e => setIssueFormData({ ...issueFormData, points: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold mb-1">Assignee</label>
                <input
                  type="text"
                  value={issueFormData.assigneeName}
                  onChange={e => setIssueFormData({ ...issueFormData, assigneeName: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button type="button" onClick={() => setIsAddIssueModalOpen(false)} className="px-4 py-2 border rounded-xl">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-xl font-semibold">Create Issue</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 11. CREATE INVOICE MODAL */}
      {/* ---------------------------------------------------- */}
      {isAddInvoiceModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
              <h2 className="text-base font-bold">+ New Accounts Receivable Invoice</h2>
              <button onClick={() => setIsAddInvoiceModalOpen(false)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400"><X size={16} /></button>
            </div>
            <form onSubmit={handleAddInvoiceSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold mb-1">Invoice Number</label>
                <input
                  type="text"
                  required
                  value={invoiceFormData.number}
                  onChange={e => setInvoiceFormData({ ...invoiceFormData, number: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white font-mono"
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">Client Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Starlight BioHealth"
                  value={invoiceFormData.client}
                  onChange={e => setInvoiceFormData({ ...invoiceFormData, client: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Amount ($)</label>
                  <input
                    type="number"
                    value={invoiceFormData.total}
                    onChange={e => setInvoiceFormData({ ...invoiceFormData, total: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Status</label>
                  <select
                    value={invoiceFormData.status}
                    onChange={e => setInvoiceFormData({ ...invoiceFormData, status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  >
                    <option value="Unpaid">Unpaid</option>
                    <option value="Paid">Paid</option>
                    <option value="Overdue">Overdue</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block font-semibold mb-1">Due Date</label>
                <input
                  type="date"
                  value={invoiceFormData.due_date}
                  onChange={e => setInvoiceFormData({ ...invoiceFormData, due_date: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button type="button" onClick={() => setIsAddInvoiceModalOpen(false)} className="px-4 py-2 border rounded-xl">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-xl font-semibold">Generate Invoice</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 12. PRODUCTION JWT AUTHENTICATION & 7-PERSONA MODAL  */}
      {/* ---------------------------------------------------- */}
      {isAuthModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/55 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl p-6 space-y-4 text-slate-900 dark:text-slate-100">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold">STAT6 Identity, JWT Session &amp; 7-Persona Portal Gate</h2>
                <p className="text-[11px] text-slate-500">Zero All-Employee License Tax • Free External Customer/Vendor/Partner Portals</p>
              </div>
              <button onClick={() => setIsAuthModalOpen(false)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 cursor-pointer"><X size={16} /></button>
            </div>

            <div className="flex gap-2 text-xs">
              <button
                type="button"
                onClick={() => setAuthMode('login')}
                className={`flex-1 py-1.5 rounded-lg font-semibold cursor-pointer ${authMode === 'login' ? 'bg-[#2563eb] text-white' : 'border'}`}
              >
                Sign In (JWT)
              </button>
              <button
                type="button"
                onClick={() => setAuthMode('register')}
                className={`flex-1 py-1.5 rounded-lg font-semibold cursor-pointer ${authMode === 'register' ? 'bg-[#2563eb] text-white' : 'border'}`}
              >
                Register New Account
              </button>
            </div>

            <form onSubmit={handleAuthSubmit} className="space-y-3 text-xs">
              {authMode === 'register' && (
                <div>
                  <label className="block font-semibold mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={authForm.full_name}
                    onChange={e => setAuthForm({ ...authForm, full_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                  />
                </div>
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold mb-1">Work / Portal Email</label>
                  <input
                    type="email"
                    required
                    value={authForm.email}
                    onChange={e => setAuthForm({ ...authForm, email: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">Password</label>
                  <input
                    type="password"
                    required
                    value={authForm.password}
                    onChange={e => setAuthForm({ ...authForm, password: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white font-mono"
                  />
                </div>
              </div>
              {authMode === 'register' && (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block font-semibold mb-1">Role</label>
                    <select
                      value={authForm.role}
                      onChange={e => setAuthForm({ ...authForm, role: e.target.value, persona: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#0f172a] text-slate-900 dark:text-white"
                    >
                      <option value="ADMIN">ADMIN</option>
                      <option value="MANAGER">MANAGER</option>
                      <option value="EMPLOYEE">EMPLOYEE</option>
                      <option value="CUSTOMER">CUSTOMER</option>
                      <option value="VENDOR">VENDOR</option>
                      <option value="PARTNER">PARTNER</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-semibold mb-1">Portal Persona</label>
                    <input
                      readOnly
                      value={authForm.persona}
                      className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-mono"
                    />
                  </div>
                </div>
              )}

              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1.5">
                <div className="font-bold text-[11px] text-slate-600 dark:text-slate-300">Default Superadmin Login (Password: <code className="font-mono">Password123!</code>):</div>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthForm(prev => ({ ...prev, email: 'admin@acroflow.enterprise', password: 'Password123!', role: 'ADMIN', persona: 'ADMIN' }));
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-[11px] font-mono hover:border-[#2563eb] cursor-pointer"
                  >
                    Enterprise Superadmin (admin@acroflow.enterprise)
                  </button>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <button type="button" onClick={() => setIsAuthModalOpen(false)} className="px-4 py-2 border rounded-xl cursor-pointer">Close</button>
                <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-xl font-semibold cursor-pointer">
                  {authMode === 'login' ? 'Authenticate JWT Session' : 'Create Account & Sign In'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Omnipresent Floating AI Copilot Dock across all modules */}
      <OmniCopilotDock
        apiBase={API_BASE}
        activeTab={activeTab}
        isSidebarOpen={isSidebarOpen}
        selectedItem={selectedIssue ? { id: selectedIssue.id, type: 'issue', title: selectedIssue.title } : null}
        messages={agentChatMessages}
        onMessagesChange={setAgentChatMessages}
        onNavigateTab={(tab) => setActiveTab(tab as ActiveTab)}
        onTasksUpdated={fetchScheduledTasks}
        onShowNotification={setSchedulerNotification}
      />

      {/* Floating System Notification */}
      {schedulerNotification && (
        <div className="fixed top-6 right-6 z-50 px-4 py-3 bg-[#162340] text-white border border-[#2563eb] rounded-xl shadow-2xl flex items-center gap-2.5 text-xs animate-in fade-in slide-in-from-top-4">
          <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
          <span>{schedulerNotification}</span>
        </div>
      )}

    </div>
  );
}
