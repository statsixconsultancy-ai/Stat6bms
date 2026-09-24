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
  X
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api/v1";

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

  // Jira Issue Drawer
  const [selectedIssue, setSelectedIssue] = useState<JiraIssue | null>(null);
  const [showIntegrationsModal, setShowIntegrationsModal] = useState(false);

  // Legal Modal
  const [activeLegalModal, setActiveLegalModal] = useState<'none' | 'tos' | 'privacy'>('none');

  // Omnisearch
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Collaboration Chat State
  const [activeChatChannel, setActiveChatChannel] = useState<'#general' | '#engineering' | '#deals'>('#general');
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([
    { sender: 'Marcus Chen', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100', time: '10:42 AM', text: 'PR #88 for OAuth token renewal is merged. Deploying to canary.' },
    { sender: 'Elena Rostova', avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100', time: '10:45 AM', text: 'Verified staging database latency is under 0.8ms across all tenants.' }
  ]);

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

  // Leads Data (Matching user screenshot)
  const [leadsData, setLeadsData] = useState([
    {
      id: 'L-1',
      name: 'Greg Howard',
      avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120',
      company: 'Howard Techno',
      source: 'Trade Show',
      email: 'greg@howard.com',
      owner: { name: 'Bob Ross', avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=120' }
    },
    {
      id: 'L-2',
      name: 'Robert Green',
      avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=120',
      company: 'Hitech Solution',
      source: 'Cold Call',
      email: 'green.robert@hitech.com',
      owner: { name: 'Tim Roberts', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120' }
    },
    {
      id: 'L-3',
      name: 'Kris Marrier',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=120',
      company: 'Brown Horizon LLC',
      source: 'Advertisement',
      email: 'kris@brownhorizon.com',
      owner: { name: 'Richard Mc', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120' }
    },
    {
      id: 'L-4',
      name: 'Amelia Burrows',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=120',
      company: 'GemStone Tech',
      source: 'Webinar',
      email: 'b.amelia@zylker.com',
      owner: { name: 'Bob Ross', avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=120' }
    },
    {
      id: 'L-5',
      name: 'Krishna Das',
      avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=120',
      company: 'Zylker Logistics',
      source: 'Email Campaign',
      email: 'krishna.das@zylker.com',
      owner: { name: 'Richard Mc', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120' }
    }
  ]);

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

  // Jira Sprint 44 state
  const [jiraIssues, setJiraIssues] = useState<JiraIssue[]>([
    {
      id: 'FIN-50',
      key: 'FIN-50',
      title: 'Automate Stripe webhook idempotent retry logic',
      type: 'task',
      status: 'Blocked',
      priority: 'high',
      assignee: { name: 'Marcus Chen', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100', role: 'Staff Backend Architect' },
      connectedTool: 'github',
      points: 5,
      description: 'Webhook verification failures on payment settlement must be retried with exponential backoff and recorded in PostgreSQL audit logs.',
      crmAccount: 'Nexus Robotics Corp',
      linkedInvoice: 'INV-2024-001'
    },
    {
      id: 'FIN-51',
      key: 'FIN-51',
      title: 'Real-time multi-tenant ledger synchronization',
      type: 'story',
      status: 'In progress',
      priority: 'urgent',
      assignee: { name: 'Elena Rostova', avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=100', role: 'Lead Platform Engineer' },
      connectedTool: 'honeycomb',
      points: 8,
      description: 'Zero sync latency implementation eliminating Deluge script overhead. Direct indexed table writes in PostgreSQL.',
      crmAccount: 'Starlight BioHealth',
      linkedInvoice: 'INV-2024-002'
    },
    {
      id: 'FIN-52',
      key: 'FIN-52',
      title: 'Design high-density enterprise typography system',
      type: 'story',
      status: 'Ready for review',
      priority: 'medium',
      assignee: { name: 'Sofia Patel', avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100', role: 'Principal Product Designer' },
      connectedTool: 'figma',
      points: 3,
      description: 'High-contrast typography with bold headlines and pure black text for all workspace elements.',
      crmAccount: 'Apex Cloud Infrastructure',
      linkedInvoice: 'INV-2024-003'
    },
    {
      id: 'FIN-53',
      key: 'FIN-53',
      title: 'SOC 2 Type II attestation report ingestion pipeline',
      type: 'task',
      status: 'Done',
      priority: 'low',
      assignee: { name: 'David Kim', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100', role: 'Security & Compliance Lead' },
      points: 2,
      description: 'Automated cryptographic signature verification for third-party vendor security audits.',
      crmAccount: 'Global Freight Dynamics',
      linkedInvoice: 'INV-2024-004'
    }
  ]);

  // Operations AI Assistant
  const [assistantLogs] = useState([
    {
      q: "Explain why invoice INV-2024-002 for Starlight Bio is 6 days overdue and recommend action.",
      a: "Invoice INV-2024-002 ($27,500.00) reached Net30 on September 15. The client contact Dr. Aris Thorne flagged a milestone sign-off delay on Sprint Task FIN-51. Automated action recommendation: Trigger WHEN-IF-DO dunning sequence #2 with grace period extended by 4 business days upon PR #88 merge.",
      actionTag: "WHEN-IF-DO Trigger Ready"
    },
    {
      q: "Which product inventory SKU requires urgent reorder?",
      a: "SKU HW-204 (Optical Sensor Model 204) has 4 units remaining in Warehouse East, which is below the minimum safety threshold of 10 units. Automated PO draft PO-2024-099 prepared for vendor Precision Micro-Optics Inc for 50 units ($8,500).",
      actionTag: "Procurement Actionable"
    }
  ]);

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
    fetch(`${API_BASE}/crm/leads`).then(r => r.json()).then(data => {
      if (Array.isArray(data) && data.length > 0) {
        setLeadsData(data.map((l: any) => ({
          id: l.id,
          name: `${l.first_name} ${l.last_name}`,
          avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120',
          company: l.company_name,
          source: l.source,
          email: l.email,
          owner: { name: l.assigned_to, avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=120' }
        })));
      }
    }).catch(() => {});
    fetch(`${API_BASE}/marketing/campaigns`).then(r => r.json()).then(setMarketingData).catch(() => {});
    fetch(`${API_BASE}/hr/employees`).then(r => r.json()).then(setHrData).catch(() => {});
    fetch(`${API_BASE}/finance/invoices`).then(r => r.json()).then(setFinanceData).catch(() => {});
    fetch(`${API_BASE}/inventory/products`).then(r => r.json()).then(setInventoryData).catch(() => {});
    fetch(`${API_BASE}/procurement/orders`).then(r => r.json()).then(setProcurementData).catch(() => {});
    fetch(`${API_BASE}/support/tickets`).then(r => r.json()).then(data => { if (Array.isArray(data)) setSupportTickets(data); }).catch(() => {});
    fetch(`${API_BASE}/automation/rules`).then(r => r.json()).then(data => { if (Array.isArray(data)) setAutomations(data); }).catch(() => {});
  };

  useEffect(() => {
    refreshAllData();
  }, []);

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
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    }).catch(() => {});
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
      <aside className="w-60 flex-shrink-0 flex flex-col justify-between bg-[#162340] text-slate-200 select-none border-r border-slate-800">
        <div className="flex flex-col h-full overflow-hidden">
          
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
            <span className="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-normal">
              v2.4
            </span>
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
        <header className="h-12 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#131c2e] px-6 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-2 text-black dark:text-white">
            <span className="font-bold text-black dark:text-white tracking-tight">STAT6</span>
            <span className="text-slate-400 font-normal">/</span>
            <span className="uppercase text-xs tracking-wider text-black dark:text-white font-normal">{activeTab}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center gap-2 px-2.5 py-1 rounded-lg border border-slate-300 dark:border-slate-700 text-xs text-black dark:text-white hover:bg-slate-50 font-normal"
            >
              <span>Search anything...</span>
              <kbd className="px-1 py-0.2 rounded bg-slate-200 dark:bg-slate-800 text-[10px] font-mono">Ctrl+K</kbd>
            </button>

            <button
              onClick={refreshAllData}
              className="px-2.5 py-1 rounded-lg border border-slate-300 dark:border-slate-700 text-xs text-black dark:text-white hover:bg-slate-50 font-normal"
            >
              Refresh
            </button>
          </div>
        </header>

        {/* Scrollable Work Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          
          {/* ==================================================== */}
          {/* TAB 01: LEADS (EXACT MATCH OF USER'S REFERENCE IMAGE) */}
          {/* ==================================================== */}
          {activeTab === 'leads' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Leads</h1>
                <button className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] text-white font-normal text-xs">+ Add Lead</button>
              </div>

              {/* Exact clean white table from user image */}
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#131c2e]">
                    <tr className="text-black dark:text-white text-[13px]">
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold">Lead Name</span>
                          <span className="font-normal text-slate-800 dark:text-slate-200 ml-1">All</span>
                          <span className="text-[10px] font-normal">▾</span>
                        </div>
                      </th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Company</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Lead Source</th>
                      <th className="py-3 px-4 border-r border-slate-200 dark:border-slate-800 font-bold">Email</th>
                      <th className="py-3 px-4 font-bold">Lead Owner</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 font-normal">
                    {leadsData.map(lead => (
                      <tr key={lead.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition">
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-3">
                            <img className="h-8 w-8 rounded-full object-cover ring-1 ring-slate-200" src={lead.avatar} alt="" />
                            <span className="text-[13.5px] text-black dark:text-white font-normal">{lead.name}</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-[13px] text-black dark:text-white font-normal">{lead.company}</td>
                        <td className="py-3.5 px-4 text-[13px] text-black dark:text-white font-normal">{lead.source}</td>
                        <td className="py-3.5 px-4 text-[13px] text-black dark:text-white font-normal">{lead.email}</td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2.5">
                            <img className="h-7 w-7 rounded-full object-cover ring-1 ring-slate-200" src={lead.owner.avatar} alt="" />
                            <span className="text-[13px] text-black dark:text-white font-normal">{lead.owner.name}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {/* Skeleton loader rows from reference image */}
                    {[1, 2, 3].map(s => (
                      <tr key={s} className="opacity-40 animate-pulse">
                        <td className="py-3.5 px-4"><div className="flex items-center gap-3"><div className="h-8 w-8 rounded-full bg-slate-300"></div><div className="h-3.5 w-24 bg-slate-300 rounded"></div></div></td>
                        <td className="py-3.5 px-4"><div className="h-3.5 w-28 bg-slate-300 rounded"></div></td>
                        <td className="py-3.5 px-4"><div className="h-3.5 w-20 bg-slate-300 rounded"></div></td>
                        <td className="py-3.5 px-4"><div className="h-3.5 w-36 bg-slate-300 rounded"></div></td>
                        <td className="py-3.5 px-4"><div className="flex items-center gap-2.5"><div className="h-7 w-7 rounded-full bg-slate-300"></div><div className="h-3.5 w-20 bg-slate-300 rounded"></div></div></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 01: DEALS & SALES PIPELINE */}
          {/* ==================================================== */}
          {activeTab === 'deals' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Sales Pipeline & Deals</h1>
                <span className="font-mono text-sm text-black dark:text-white font-normal">Pipeline Value: $580,000</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-6 gap-2.5">
                {['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Won'].map(stage => (
                  <div key={stage} className="p-3 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 dark:border-slate-800 min-h-[460px] flex flex-col">
                    <h2 className="text-xs font-bold text-black dark:text-white pb-2 border-b border-slate-200">{stage}</h2>
                    <div className="mt-2.5 space-y-2 flex-1">
                      {deals.filter(d => d.stage === stage).map(d => (
                        <div key={d.id} className="p-2.5 rounded-xl border border-slate-200 bg-[#fafbfc] dark:bg-slate-900 shadow-xs">
                          <div className="text-xs text-black dark:text-white font-normal">{d.title}</div>
                          <div className="text-[11px] text-black dark:text-white mt-1 font-normal">{d.company_name}</div>
                          <div className="mt-2 flex justify-between font-mono text-xs text-black dark:text-white font-normal">
                            <span>{fmt(d.amount)}</span>
                            <span>{d.probability}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 01: CONTACTS & ORGS */}
          {/* ==================================================== */}
          {activeTab === 'contacts' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Customer Accounts & 360° Directory</h1>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="border-b bg-white dark:bg-[#131c2e] text-black dark:text-white font-normal text-[12.5px]">
                    <tr><th className="py-3 px-4 border-r">Company Name</th><th className="py-3 px-4 border-r">Industry</th><th className="py-3 px-4 border-r">Employees</th><th className="py-3 px-4 border-r">Location</th><th className="py-3 px-4">Annual Revenue</th></tr>
                  </thead>
                  <tbody className="divide-y text-black dark:text-white font-normal">
                    <tr><td className="py-3.5 px-4">Nexus Robotics Corp</td><td className="py-3.5 px-4">Autonomous Systems</td><td className="py-3.5 px-4">250 staff</td><td className="py-3.5 px-4">Boston, MA</td><td className="py-3.5 px-4 font-mono">$45,000,000</td></tr>
                    <tr><td className="py-3.5 px-4">Starlight BioHealth</td><td className="py-3.5 px-4">Clinical Therapeutics</td><td className="py-3.5 px-4">120 staff</td><td className="py-3.5 px-4">San Diego, CA</td><td className="py-3.5 px-4 font-mono">$18,500,000</td></tr>
                    <tr><td className="py-3.5 px-4">Apex Cloud Infrastructure</td><td className="py-3.5 px-4">Edge Compute</td><td className="py-3.5 px-4">400 staff</td><td className="py-3.5 px-4">Austin, TX</td><td className="py-3.5 px-4 font-mono">$82,000,000</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 02: MARKETING CAMPAIGNS & ROI */}
          {/* ==================================================== */}
          {activeTab === 'marketing' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Marketing Campaigns & Channel ROI</h1>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 dark:border-slate-800 shadow-xs">
                  <div className="text-xs text-black dark:text-white font-normal">Active Campaigns</div>
                  <div className="mt-2 text-2xl font-mono text-black dark:text-white font-normal">3 Channels</div>
                </div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 dark:border-slate-800 shadow-xs">
                  <div className="text-xs text-black dark:text-white font-normal">Total Leads Captured</div>
                  <div className="mt-2 text-2xl font-mono text-black dark:text-white font-normal">428 Inbound</div>
                </div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 dark:border-slate-800 shadow-xs">
                  <div className="text-xs text-black dark:text-white font-normal">Blended Marketing ROI</div>
                  <div className="mt-2 text-2xl font-mono text-black dark:text-white font-normal">312.5%</div>
                </div>
              </div>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs text-black dark:text-white">
                  <thead className="border-b text-[12.5px] font-normal">
                    <tr><th className="py-3 px-4 border-r">Campaign</th><th className="py-3 px-4 border-r">Channel</th><th className="py-3 px-4 border-r">Budget</th><th className="py-3 px-4 border-r">Spent</th><th className="py-3 px-4">ROI</th></tr>
                  </thead>
                  <tbody className="divide-y font-normal">
                    <tr><td className="py-3.5 px-4">Q3 Enterprise Inbound</td><td className="py-3.5 px-4">Google Search</td><td className="py-3.5 px-4 font-mono">$15,000</td><td className="py-3.5 px-4 font-mono">$12,400</td><td className="py-3.5 px-4 font-mono">340%</td></tr>
                    <tr><td className="py-3.5 px-4">FinTech Decision Maker Outreach</td><td className="py-3.5 px-4">LinkedIn Ads</td><td className="py-3.5 px-4 font-mono">$8,000</td><td className="py-3.5 px-4 font-mono">$7,200</td><td className="py-3.5 px-4 font-mono">285%</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 03: PROJECTS & OPERATIONS (JIRA AGILE BOARD) */}
          {/* ==================================================== */}
          {activeTab === 'projects' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">FinTech Platform Core (Sprint 44)</h1>
                <button onClick={() => setShowIntegrationsModal(true)} className="px-3.5 py-1.5 rounded-lg bg-[#2563eb] text-white font-normal text-xs">Workspaces: Figma & GitHub</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {(['Blocked', 'In progress', 'Ready for review', 'Done'] as const).map(stage => (
                  <div key={stage} className="bg-white dark:bg-[#131c2e] p-3 rounded-2xl border border-slate-200 min-h-[480px] flex flex-col">
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
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 04: HR & STAFF MANAGEMENT */}
          {/* ==================================================== */}
          {activeTab === 'hr' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Staff & Department Directory</h1>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Headcount</div><div className="text-2xl mt-1 font-mono font-normal">5 Staff</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Attendance</div><div className="text-2xl mt-1 font-mono font-normal">97.4%</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Monthly Payroll</div><div className="text-2xl mt-1 font-mono font-normal">$68,500</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Pending Leave</div><div className="text-2xl mt-1 font-mono font-normal">1 Request</div></div>
              </div>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs text-black dark:text-white">
                  <thead className="border-b text-[12.5px] font-normal"><tr><th className="py-3 px-4 border-r">Code</th><th className="py-3 px-4 border-r">Name</th><th className="py-3 px-4 border-r">Department</th><th className="py-3 px-4 border-r">Role</th><th className="py-3 px-4">Attendance</th></tr></thead>
                  <tbody className="divide-y font-normal">{hrData?.employees?.map((emp: any) => (<tr key={emp.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-mono">{emp.code}</td><td className="py-3 px-4">{emp.name}</td><td className="py-3 px-4">{emp.department}</td><td className="py-3 px-4">{emp.role}</td><td className="py-3 px-4 font-mono">{emp.attendance}%</td></tr>))}</tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 05: FINANCE & INVOICING LEDGER */}
          {/* ==================================================== */}
          {activeTab === 'finance' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Finance Ledger & Invoices</h1>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Total Billed</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(187000)}</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Expenses</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(13420)}</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Net Margin</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(66330)}</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Overdue Receivables</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(27500)}</div></div>
              </div>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs text-black dark:text-white">
                  <thead className="border-b text-[12.5px] font-normal"><tr><th className="py-3 px-4 border-r">Invoice #</th><th className="py-3 px-4 border-r">Client</th><th className="py-3 px-4 border-r">Due Date</th><th className="py-3 px-4 border-r">Total</th><th className="py-3 px-4">Status</th></tr></thead>
                  <tbody className="divide-y font-normal">{financeData?.invoices?.map((inv: any) => (<tr key={inv.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-mono">{inv.number}</td><td className="py-3 px-4">{inv.client}</td><td className="py-3 px-4">{inv.due_date}</td><td className="py-3 px-4 font-mono">{fmt(inv.total)}</td><td className="py-3 px-4"><span className={`px-2 py-0.5 rounded-full text-xs font-normal ${inv.status === 'Paid' ? 'bg-emerald-100 text-emerald-900' : 'bg-rose-100 text-rose-900'}`}>{inv.status}</span></td></tr>))}</tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 06: INVENTORY & ASSETS */}
          {/* ==================================================== */}
          {activeTab === 'inventory' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Warehouse Inventory & Asset Register</h1>
              <div className="p-3 rounded-2xl border border-rose-300 bg-rose-50 text-rose-900 text-xs flex justify-between items-center font-normal">
                <span>Critical Stock Warning: Optical Sensor Model 204 has 4 units left (Threshold: 10).</span>
                <button className="px-3 py-1 rounded-lg bg-rose-600 text-white font-normal">Auto-Draft PO</button>
              </div>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs text-black dark:text-white">
                  <thead className="border-b text-[12.5px] font-normal"><tr><th className="py-3 px-4 border-r">SKU</th><th className="py-3 px-4 border-r">Product Name</th><th className="py-3 px-4 border-r">Category</th><th className="py-3 px-4 border-r">Price</th><th className="py-3 px-4">In Stock</th></tr></thead>
                  <tbody className="divide-y font-normal">{inventoryData?.products?.map((p: any) => (<tr key={p.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-mono">{p.sku}</td><td className="py-3 px-4">{p.name}</td><td className="py-3 px-4">{p.category}</td><td className="py-3 px-4 font-mono">{fmt(p.price)}</td><td className="py-3 px-4 font-mono">{p.stock} units {p.is_low_stock && '(Low)'}</td></tr>))}</tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 07: PROCUREMENT & VENDOR MANAGEMENT */}
          {/* ==================================================== */}
          {activeTab === 'procurement' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Procurement & Purchase Orders</h1>
              <div className="bg-white dark:bg-[#131c2e] rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs text-black dark:text-white">
                  <thead className="border-b text-[12.5px] font-normal"><tr><th className="py-3 px-4 border-r">PO Number</th><th className="py-3 px-4 border-r">Vendor</th><th className="py-3 px-4 border-r">Total Amount</th><th className="py-3 px-4 border-r">Delivery Date</th><th className="py-3 px-4">Status</th></tr></thead>
                  <tbody className="divide-y font-normal">{procurementData?.purchase_orders?.map((po: any) => (<tr key={po.id} className="hover:bg-slate-50"><td className="py-3 px-4 font-mono">{po.po_number}</td><td className="py-3 px-4">{po.vendor}</td><td className="py-3 px-4 font-mono">{fmt(po.total)}</td><td className="py-3 px-4">{po.delivery_date}</td><td className="py-3 px-4"><span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-900 font-normal">{po.status}</span></td></tr>))}</tbody>
                </table>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 08: CUSTOMER SUPPORT DESK */}
          {/* ==================================================== */}
          {activeTab === 'support' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Customer Support Queue & SLAs</h1>
              <div className="space-y-2">
                {[
                  { id: "TICK-101", title: "API Gateway token renewal latency under peak load", client: "Nexus Robotics Corp", priority: "High", sla: "2h 45m left", status: "In Progress", agent: "Marcus Chen" },
                  { id: "TICK-102", title: "Invoice statement discrepancy in clinical export module", client: "Starlight BioHealth", priority: "Medium", sla: "6h 10m left", status: "Investigating", agent: "Elena Rostova" }
                ].map(t => (
                  <div key={t.id} className="p-3.5 rounded-2xl border border-slate-200 bg-white dark:bg-[#131c2e] flex items-center justify-between text-black dark:text-white">
                    <div><div className="flex items-center gap-2"><span className="font-mono text-xs">{t.id}</span><span className="font-normal">{t.title}</span></div><div className="text-xs text-black mt-1 font-normal">Client: {t.client} • Assigned: {t.agent}</div></div>
                    <div className="flex gap-2 text-xs font-mono font-normal"><span className="px-2 py-0.5 rounded bg-amber-100 text-amber-900">{t.sla}</span><span className="px-2 py-0.5 rounded bg-blue-100 text-blue-900">{t.status}</span></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 09: REPORTING & BI ANALYTICS (EXECUTIVE COCKPIT) */}
          {/* ==================================================== */}
          {(activeTab === 'overview' || activeTab === 'analytics') && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Executive Telemetry & BI Analytics</h1>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Paid Revenue (YTD)</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(overviewData?.kpis?.total_revenue_paid || 79750)}</div><div className="text-xs mt-1 text-emerald-800 font-normal">+24.8% vs last month</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Deal Pipeline</div><div className="text-2xl mt-1 font-mono font-normal">{fmt(overviewData?.kpis?.total_pipeline || 580000)}</div><div className="text-xs mt-1 font-normal">6 active contracts</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">Overdue Receivables</div><div className="text-2xl mt-1 font-mono text-amber-800 font-normal">{fmt(overviewData?.kpis?.overdue_receivables || 27500)}</div><div className="text-xs mt-1 text-amber-900 font-normal">Starlight Bio (6d overdue)</div></div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white"><div className="text-xs font-normal">SLA Compliance</div><div className="text-2xl mt-1 font-mono font-normal">100.0%</div><div className="text-xs mt-1 font-normal">Avg 14m response</div></div>
              </div>
              <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white">
                <h2 className="text-sm font-bold pb-2 border-b border-slate-200">Consolidated Monthly Trajectory</h2>
                <div className="h-40 flex items-end justify-between gap-3 pt-4">
                  {[{ m: 'Apr', v: '$45k', h: 50 }, { m: 'May', v: '$52k', h: 60 }, { m: 'Jun', v: '$49k', h: 55 }, { m: 'Jul', v: '$63k', h: 75 }, { m: 'Aug', v: '$58k', h: 68 }, { m: 'Sep', v: '$79.7k', h: 95 }].map((b, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end text-black dark:text-white">
                      <span className="text-[11px] font-mono font-normal">{b.v}</span>
                      <div style={{ height: `${b.h}%` }} className={`w-full max-w-[40px] rounded-t ${idx === 5 ? 'bg-[#2563eb]' : 'bg-slate-300'}`}></div>
                      <span className="text-xs font-normal">{b.m}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 10: COLLABORATION & CHAT */}
          {/* ==================================================== */}
          {activeTab === 'collaboration' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <div className="flex items-center justify-between pb-2 border-b">
                <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Team Collaboration & Channels</h1>
                <div className="flex gap-2">
                  {(['#general', '#engineering', '#deals'] as const).map(ch => (
                    <button key={ch} onClick={() => setActiveChatChannel(ch)} className={`px-3 py-1 rounded-full text-xs font-normal ${activeChatChannel === ch ? 'bg-[#2563eb] text-white' : 'bg-white border text-black'}`}>{ch}</button>
                  ))}
                </div>
              </div>
              <div className="bg-white dark:bg-[#131c2e] p-4 rounded-2xl border border-slate-200 shadow-xs h-96 flex flex-col justify-between">
                <div className="overflow-y-auto space-y-3 text-black dark:text-white">
                  {chatMessages.map((msg, i) => (
                    <div key={i} className="flex gap-3 items-start">
                      <img className="h-8 w-8 rounded-full object-cover" src={msg.avatar} alt="" />
                      <div><div className="flex items-center gap-2"><span className="text-xs font-bold text-black dark:text-white">{msg.sender}</span><span className="text-[10px] text-black dark:text-white font-normal">{msg.time}</span></div><div className="text-[13px] font-normal mt-0.5">{msg.text}</div></div>
                    </div>
                  ))}
                </div>
                <form onSubmit={handleSendChat} className="flex gap-2 pt-3 border-t">
                  <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder={`Message ${activeChatChannel}...`} className="flex-1 border rounded-lg px-3 py-2 text-xs text-black focus:outline-none focus:border-[#2563eb] font-normal" />
                  <button type="submit" className="px-4 py-2 bg-[#2563eb] text-white rounded-lg text-xs font-normal">Send</button>
                </form>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 11: COMPLIANCE & SECURITY */}
          {/* ==================================================== */}
          {activeTab === 'compliance' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">Compliance & Enterprise Security</h1>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-black dark:text-white">
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200">
                  <h2 className="text-sm font-bold">SOC 2 Type II</h2>
                  <div className="text-sm mt-1 text-emerald-800 font-normal">Verified & Active</div>
                </div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200">
                  <h2 className="text-sm font-bold">GDPR & HIPAA</h2>
                  <div className="text-sm mt-1 text-emerald-800 font-normal">DPA Compliant</div>
                </div>
                <div className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200">
                  <h2 className="text-sm font-bold">Single-Tenant RLS</h2>
                  <div className="text-sm mt-1 text-emerald-800 font-normal">Enforced at DB Layer</div>
                </div>
              </div>
              <div className="bg-white dark:bg-[#131c2e] p-4 rounded-2xl border border-slate-200 text-black dark:text-white space-y-2">
                <h2 className="text-sm font-bold border-b pb-2">Enterprise Master Agreements</h2>
                <div className="flex gap-3">
                  <button onClick={() => setActiveLegalModal('tos')} className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-normal text-black">View Master Services Agreement (TOS)</button>
                  <button onClick={() => setActiveLegalModal('privacy')} className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-normal text-black">View Privacy Policy & DPA</button>
                </div>
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 12: AUTOMATION (WHEN-IF-DO) */}
          {/* ==================================================== */}
          {activeTab === 'automation' && (
            <div className="space-y-4 max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-black dark:text-white tracking-tight">WHEN-IF-DO Automation Rules</h1>
              <div className="space-y-2.5">
                {[
                  { name: "Deal Won -> Auto Invoice & Sprint Task", t: "WHEN Deal.stage == 'Won'", c: "IF Deal.amount >= 50000", a: "DO Invoice.create(Net30) && Jira.createTask(FIN)" },
                  { name: "Overdue Invoice Dunning Escalation", t: "WHEN Invoice.dueDate < NOW()", c: "IF Invoice.status == 'Unpaid' && days >= 5", a: "DO Email.sendDunning() && Slack.notify(Owner)" },
                  { name: "Warehouse Stock Reorder Sentinel", t: "WHEN Product.stock <= Product.reorderLevel", c: "IF Vendor.status == 'Active'", a: "DO PO.draft() && Email.notify(Procurement)" }
                ].map((r, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs text-black dark:text-white space-y-2">
                    <div className="flex justify-between items-center"><h2 className="text-sm font-bold">{r.name}</h2><span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 text-xs font-normal">Active</span></div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 font-mono text-xs">
                      <div className="p-2 rounded bg-slate-100 dark:bg-slate-800"><div className="text-[10px] text-black dark:text-white font-normal">TRIGGER</div><div className="font-normal">{r.t}</div></div>
                      <div className="p-2 rounded bg-slate-100 dark:bg-slate-800"><div className="text-[10px] text-black dark:text-white font-normal">CONDITION</div><div className="font-normal">{r.c}</div></div>
                      <div className="p-2 rounded bg-slate-100 dark:bg-slate-800"><div className="text-[10px] text-black dark:text-white font-normal">ACTION</div><div className="font-normal">{r.a}</div></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 13: AI & INSIGHTS ASSISTANT */}
          {/* ==================================================== */}
          {activeTab === 'ai' && (
            <div className="space-y-4 max-w-7xl mx-auto text-black dark:text-white">
              <h1 className="text-2xl font-bold tracking-tight">AI Insights & Operations Assistant</h1>
              <div className="space-y-3">
                {assistantLogs.map((log, i) => (
                  <div key={i} className="p-4 rounded-2xl bg-white dark:bg-[#131c2e] border border-slate-200 shadow-xs space-y-2">
                    <div className="flex justify-between items-center"><h2 className="text-sm font-bold">Q: "{log.q}"</h2><span className="px-2 py-0.5 rounded bg-blue-100 text-blue-900 text-xs font-normal">{log.actionTag}</span></div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl text-xs font-normal leading-relaxed">{log.a}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ==================================================== */}
          {/* TAB 14: SETTINGS & MODULE TOGGLES */}
          {/* ==================================================== */}
          {activeTab === 'settings' && (
            <div className="space-y-4 max-w-4xl mx-auto text-black dark:text-white">
              <h1 className="text-2xl font-bold tracking-tight">Enterprise Module Controls (All 14 Services)</h1>
              <div className="bg-white dark:bg-[#131c2e] p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {Object.entries(moduleToggles).map(([k, v]) => (
                    <div key={k} className="p-3 rounded-xl border border-slate-200 flex justify-between items-center bg-slate-50 dark:bg-slate-900">
                      <span className="text-xs font-normal">{k}</span>
                      <button onClick={() => setModuleToggles(p => ({ ...p, [k]: !p[k] }))} className={`px-3 py-1 rounded-full text-xs font-normal ${v ? 'bg-[#2563eb] text-white' : 'bg-slate-200 text-black'}`}>{v ? 'ENABLED' : 'DISABLED'}</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
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

    </div>
  );
}
