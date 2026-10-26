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
  ArrowUpRight,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Move,
  GripVertical
} from 'lucide-react';
import { GeminiMarkdownRenderer } from './GeminiMarkdownRenderer';
import { GeminiSparkleIcon, GeminiMiniSparkle } from './GeminiIcons';

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
    expenses?: number;
    profit?: number;
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
  isSidebarOpen?: boolean;
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
  isSidebarOpen = true,
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
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, 'up' | 'down'>>({});
  const [activeTabInside, setActiveTabInside] = useState<'chat' | 'context'>('chat');
  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  // --- APPLE UI FLOATING & DRAGGING STATE ---
  const getMinX = () => (isSidebarOpen ? 256 : 16);

  const getDefaultFloatPos = () => {
    if (typeof window === 'undefined') return { x: 900, y: 650 };
    return {
      x: Math.max(getMinX(), window.innerWidth - 240),
      y: Math.max(16, window.innerHeight - 84)
    };
  };

  const [floatPos, setFloatPos] = useState<{ x: number; y: number }>(() => {
    try {
      const saved = localStorage.getItem('stat6_copilot_float_pos');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.x === 'number' && typeof parsed.y === 'number') {
          return parsed;
        }
      }
    } catch {}
    return getDefaultFloatPos();
  });

  // Display mode: 'pill' (Apple Dynamic Capsule) | 'orb' (Apple AssistiveTouch Squircle)
  const [orbMode, setOrbMode] = useState<'pill' | 'orb'>(() => {
    try {
      const saved = localStorage.getItem('stat6_copilot_orb_mode');
      if (saved === 'orb' || saved === 'pill') return saved;
    } catch {}
    return 'pill';
  });

  // Dragging states for floating launcher
  const isDraggingRef = useRef(false);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  const elementStartPos = useRef({ x: 0, y: 0 });
  const currentFloatPosRef = useRef(floatPos);
  const hasMovedRef = useRef(false);

  // Position and dragging states for Chat Window
  const [dockPos, setDockPos] = useState<{ x: number; y: number } | null>(null);
  const isWindowDraggingRef = useRef(false);
  const [isWindowDragging, setIsWindowDragging] = useState(false);
  const windowDragStartPos = useRef({ x: 0, y: 0 });
  const windowElementStartPos = useRef({ x: 0, y: 0 });

  // Viewport clamp utility
  const clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max);

  const clampPosition = (x: number, y: number, width: number, height: number) => {
    if (typeof window === 'undefined') return { x, y };
    const pad = 12;
    const minX = getMinX();
    const maxX = Math.max(minX, window.innerWidth - width - pad);
    const maxY = Math.max(pad, window.innerHeight - height - pad);
    return {
      x: clamp(x, minX, maxX),
      y: clamp(y, pad, maxY)
    };
  };

  // Apple AssistiveTouch Move-Aside Snap: smoothly glides to nearest side margin (left or right)
  const snapToAsideEdge = (pos: { x: number; y: number }) => {
    if (typeof window === 'undefined') return pos;
    const launcherW = orbMode === 'orb' ? 56 : 220;
    const minX = getMinX();
    const maxX = Math.max(minX, window.innerWidth - launcherW - 16);
    const midPoint = (minX + maxX) / 2;
    const snappedX = pos.x < midPoint ? minX : maxX;
    return { x: snappedX, y: clamp(pos.y, 16, window.innerHeight - 70) };
  };

  // If sidebar expands, automatically move AI icon aside so it never overlaps the sidebar!
  useEffect(() => {
    if (isSidebarOpen && floatPos.x < 252) {
      setFloatPos(prev => {
        const next = { ...prev, x: 258 };
        currentFloatPosRef.current = next;
        return next;
      });
    }
  }, [isSidebarOpen, floatPos.x]);

  // Handle window resizing to keep floating icon and window inside viewport
  useEffect(() => {
    const handleResize = () => {
      const w = orbMode === 'orb' ? 56 : 220;
      const h = 54;
      setFloatPos(prev => {
        const clamped = clampPosition(prev.x, prev.y, w, h);
        currentFloatPosRef.current = clamped;
        return clamped;
      });

      if (dockPos) {
        const winW = isExpanded ? Math.min(760, window.innerWidth - 24) : Math.min(480, window.innerWidth - 24);
        const winH = isExpanded ? Math.min(840, window.innerHeight - 24) : Math.min(620, window.innerHeight - 24);
        setDockPos(prev => prev ? clampPosition(prev.x, prev.y, winW, winH) : null);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [orbMode, isExpanded, dockPos, isSidebarOpen]);

  // Centered Window Calculation: puts the chat window directly in the centre of the workspace
  const getCenteredWindowPos = (expanded: boolean) => {
    if (typeof window === 'undefined') return { x: 400, y: 150 };
    const winW = expanded ? Math.min(760, window.innerWidth - 32) : Math.min(480, window.innerWidth - 32);
    const winH = expanded ? Math.min(840, window.innerHeight - 32) : Math.min(620, window.innerHeight - 32);
    const leftOffset = isSidebarOpen ? 240 : 0;
    const targetX = Math.round(leftOffset + Math.max(0, window.innerWidth - leftOffset - winW) / 2);
    const targetY = Math.round(Math.max(16, (window.innerHeight - winH) / 2));
    return { x: targetX, y: targetY };
  };

  // When the chat window opens in the centre, the AI icon automatically moves aside to the side edge!
  useEffect(() => {
    if (isOpen) {
      // 1. Center the chat window in the workspace
      setDockPos(getCenteredWindowPos(isExpanded));

      // 2. Automatically move the AI icon aside to the edge of the screen
      setFloatPos(prev => {
        const aside = snapToAsideEdge(prev);
        currentFloatPosRef.current = aside;
        return aside;
      });
    }
  }, [isOpen, isSidebarOpen]);

  // When expanding / shrinking window width with green traffic light
  useEffect(() => {
    if (isOpen && !isWindowDragging) {
      setDockPos(getCenteredWindowPos(isExpanded));
    }
  }, [isExpanded]);

  const handleLauncherPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest('.no-drag')) return;
    if (e.button !== 0) return;

    isDraggingRef.current = true;
    hasMovedRef.current = false;
    dragStartPos.current = { x: e.clientX, y: e.clientY };
    elementStartPos.current = { ...floatPos };

    try {
      e.currentTarget.setPointerCapture(e.pointerId);
    } catch {}
    setIsDragging(true);
  };

  const handleLauncherPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDraggingRef.current) return;
    const dx = e.clientX - dragStartPos.current.x;
    const dy = e.clientY - dragStartPos.current.y;

    if (Math.hypot(dx, dy) > 4) {
      hasMovedRef.current = true;
    }

    const w = orbMode === 'orb' ? 56 : 220;
    const h = 54;
    const newPos = clampPosition(elementStartPos.current.x + dx, elementStartPos.current.y + dy, w, h);
    currentFloatPosRef.current = newPos;
    setFloatPos(newPos);
  };

  const handleLauncherPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    setIsDragging(false);

    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {}

    if (!hasMovedRef.current) {
      // Clean tap/click without drag -> toggle open/close
      setIsOpen(prev => !prev);
    } else {
      // Drag completed -> snap to nearest side edge (Apple AssistiveTouch move aside)
      const snapped = snapToAsideEdge(currentFloatPosRef.current);
      currentFloatPosRef.current = snapped;
      setFloatPos(snapped);
      try {
        localStorage.setItem('stat6_copilot_float_pos', JSON.stringify(snapped));
      } catch {}
    }
  };

  const toggleOrbMode = (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextMode = orbMode === 'pill' ? 'orb' : 'pill';
    setOrbMode(nextMode);
    try {
      localStorage.setItem('stat6_copilot_orb_mode', nextMode);
    } catch {}
    const w = nextMode === 'orb' ? 56 : 220;
    setFloatPos(prev => snapToAsideEdge(clampPosition(prev.x, prev.y, w, 54)));
  };

  const handleWindowPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest('.no-drag, button, input, textarea, a')) return;
    if (e.button !== 0) return;

    isWindowDraggingRef.current = true;
    windowDragStartPos.current = { x: e.clientX, y: e.clientY };
    windowElementStartPos.current = dockPos || getCenteredWindowPos(isExpanded);

    try {
      e.currentTarget.setPointerCapture(e.pointerId);
    } catch {}
    setIsWindowDragging(true);
  };

  const handleWindowPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isWindowDraggingRef.current) return;
    const dx = e.clientX - windowDragStartPos.current.x;
    const dy = e.clientY - windowDragStartPos.current.y;

    const winW = isExpanded ? Math.min(760, window.innerWidth - 24) : Math.min(480, window.innerWidth - 24);
    const winH = isExpanded ? Math.min(840, window.innerHeight - 24) : Math.min(620, window.innerHeight - 24);

    const newX = windowElementStartPos.current.x + dx;
    const newY = windowElementStartPos.current.y + dy;
    setDockPos(clampPosition(newX, newY, winW, winH));
  };

  const handleWindowPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isWindowDraggingRef.current) return;
    isWindowDraggingRef.current = false;
    setIsWindowDragging(false);
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {}
  };

  const handleCopyMessage = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

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
          'What is our financial health and operating revenue today?',
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
          'What is our financial performance and operating margin today?',
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
            expenses: data.immediate_data.total_expenses,
            profit: data.immediate_data.net_operating_profit,
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
      {/* 1. FLOATING APPLE DRAGGABLE COPILOT LAUNCHER        */}
      {/* ---------------------------------------------------- */}
      <div
        style={{
          position: 'fixed',
          left: `${floatPos.x}px`,
          top: `${floatPos.y}px`,
          zIndex: 9999,
          touchAction: 'none',
          transition: isDragging ? 'none' : 'left 0.35s cubic-bezier(0.16, 1, 0.3, 1), top 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.15s ease'
        }}
        onPointerDown={handleLauncherPointerDown}
        onPointerMove={handleLauncherPointerMove}
        onPointerUp={handleLauncherPointerUp}
        onPointerCancel={handleLauncherPointerUp}
        className={`group select-none ${
          isDragging ? 'cursor-grabbing scale-105' : 'cursor-grab hover:scale-[1.03]'
        }`}
        title="Drag anywhere across platform • Click to toggle Copilot (Ctrl+/)"
      >
        {/* Apple Intelligence Multi-tone Aura Glow */}
        <div
          className={`absolute -inset-1 rounded-full bg-gradient-to-r from-[#4285F4] via-[#9B72CF] via-[#D96570] to-[#F4B400] blur-md transition-opacity duration-300 pointer-events-none ${
            isOpen ? 'opacity-80 ring-2 ring-blue-400/50' : 'opacity-40 group-hover:opacity-85 animate-pulse'
          }`}
        />

        {orbMode === 'pill' ? (
          /* Apple Intelligence Dynamic Capsule Pill */
          <div className="relative flex items-center gap-2 pl-2.5 pr-2.5 py-2 rounded-full bg-black/85 dark:bg-[#070b14]/90 backdrop-blur-2xl border border-white/20 text-white shadow-[0_12px_40px_rgba(0,0,0,0.65),inset_0_1px_1px_rgba(255,255,255,0.4)]">
            {/* Apple Tactile Drag Grip */}
            <div className="flex flex-col gap-0.5 px-0.5 text-white/40 group-hover:text-white/80 transition-colors pointer-events-none">
              <div className="flex gap-0.5">
                <span className="w-1 h-1 rounded-full bg-current" />
                <span className="w-1 h-1 rounded-full bg-current" />
              </div>
              <div className="flex gap-0.5">
                <span className="w-1 h-1 rounded-full bg-current" />
                <span className="w-1 h-1 rounded-full bg-current" />
              </div>
              <div className="flex gap-0.5">
                <span className="w-1 h-1 rounded-full bg-current" />
                <span className="w-1 h-1 rounded-full bg-current" />
              </div>
            </div>

            {/* Glowing Orb Jewel */}
            <div className="relative w-8 h-8 rounded-full bg-gradient-to-tr from-[#1e293b] via-[#1a233a] to-[#253350] border border-white/25 flex items-center justify-center flex-shrink-0 shadow-inner">
              <GeminiSparkleIcon
                size={18}
                className="transition-transform group-hover:rotate-45 duration-500"
              />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-emerald-400/40 animate-ping" />
            </div>

            {/* Typography & Context */}
            <div className="flex flex-col text-left pointer-events-none">
              <div className="flex items-center gap-1.5 leading-tight">
                <span className="text-[11px] font-bold tracking-tight text-white">
                  STAT6
                </span>
                <span className="px-1.5 py-0.2 text-[8px] font-semibold bg-gradient-to-r from-blue-500/30 to-purple-500/30 text-blue-200 rounded-full border border-blue-400/30">
                  ✦ Copilot
                </span>
              </div>
              <span className="text-[9px] text-white/60 font-mono truncate max-w-[95px] leading-tight">
                {getModuleName(activeTab)}
              </span>
            </div>

            {/* Mode Switcher to Minimalist Assistive Orb */}
            <button
              onClick={toggleOrbMode}
              className="no-drag ml-0.5 p-1 rounded-full hover:bg-white/10 text-white/50 hover:text-white transition cursor-pointer"
              title="Switch to compact Apple Orb mode"
            >
              <Minus size={11} />
            </button>
          </div>
        ) : (
          /* Apple AssistiveTouch Squircle Orb Mode */
          <div className="relative w-14 h-14 rounded-2xl bg-black/85 dark:bg-[#070b14]/90 backdrop-blur-2xl border border-white/20 text-white shadow-[0_12px_40px_rgba(0,0,0,0.7),inset_0_1px_1px_rgba(255,255,255,0.4)] flex flex-col items-center justify-center gap-1">
            <div className="relative flex items-center justify-center">
              <GeminiSparkleIcon
                size={22}
                className="transition-transform group-hover:rotate-45 duration-500"
              />
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-emerald-400/40 animate-ping" />
            </div>
            {/* Grip dots affordance */}
            <div className="flex items-center gap-0.5 text-white/40 group-hover:text-white/80 transition-colors">
              <span className="w-1 h-1 rounded-full bg-current" />
              <span className="w-1 h-1 rounded-full bg-current" />
              <span className="w-1 h-1 rounded-full bg-current" />
            </div>
            {/* Expand button on hover */}
            <button
              onClick={toggleOrbMode}
              className="no-drag absolute -top-1.5 -right-1.5 p-0.5 rounded-full bg-slate-800 border border-white/20 text-white/70 hover:text-white opacity-0 group-hover:opacity-100 transition cursor-pointer shadow-md"
              title="Expand to Dynamic Pill mode"
            >
              <Maximize2 size={9} />
            </button>
          </div>
        )}
      </div>

      {/* ---------------------------------------------------- */}
      {/* 2. HOVERING DRAGGABLE COPILOT WINDOW (APPLE MACOS)   */}
      {/* ---------------------------------------------------- */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            left: `${dockPos ? dockPos.x : (isSidebarOpen ? 260 : 24)}px`,
            top: `${dockPos ? dockPos.y : 24}px`,
            zIndex: 9998,
            transition: isWindowDragging ? 'none' : 'left 0.3s cubic-bezier(0.16, 1, 0.3, 1), top 0.3s cubic-bezier(0.16, 1, 0.3, 1), width 0.25s ease, height 0.25s ease'
          }}
          className={`flex flex-col rounded-2xl shadow-[0_24px_70px_rgba(0,0,0,0.85),0_0_0_1px_rgba(255,255,255,0.12)] bg-[#0f172a]/95 backdrop-blur-2xl text-slate-100 overflow-hidden ${
            isExpanded
              ? 'w-[95vw] sm:w-[760px] h-[85vh] max-h-[840px]'
              : 'w-[92vw] sm:w-[480px] h-[620px] max-h-[82vh]'
          }`}
        >
          {/* Apple macOS Draggable Window Titlebar */}
          <div
            onPointerDown={handleWindowPointerDown}
            onPointerMove={handleWindowPointerMove}
            onPointerUp={handleWindowPointerUp}
            onPointerCancel={handleWindowPointerUp}
            className={`flex items-center justify-between px-4 py-3 bg-[#11192e]/90 backdrop-blur-md border-b border-slate-700/80 select-none flex-shrink-0 ${
              isWindowDragging ? 'cursor-grabbing' : 'cursor-grab'
            }`}
            title="Drag window anywhere across the screen"
          >
            {/* Apple Traffic Light Controls */}
            <div className="flex items-center gap-2 group/lights">
              {/* Close (Red) */}
              <button
                onClick={() => setIsOpen(false)}
                className="w-3 h-3 rounded-full bg-[#ff5f56] hover:bg-[#e0443e] border border-[#e0443e] flex items-center justify-center transition cursor-pointer"
                title="Close window (Esc)"
              >
                <X size={8} className="text-black/60 opacity-0 group-hover/lights:opacity-100 transition-opacity" />
              </button>
              {/* Minimize (Yellow) */}
              <button
                onClick={() => setIsOpen(false)}
                className="w-3 h-3 rounded-full bg-[#ffbd2e] hover:bg-[#dea123] border border-[#dea123] flex items-center justify-center transition cursor-pointer"
                title="Minimize to floating orb"
              >
                <Minus size={8} className="text-black/60 opacity-0 group-hover/lights:opacity-100 transition-opacity" />
              </button>
              {/* Expand / Maximize (Green) */}
              <button
                onClick={() => setIsExpanded(prev => !prev)}
                className="w-3 h-3 rounded-full bg-[#27c93f] hover:bg-[#1aab29] border border-[#1aab29] flex items-center justify-center transition cursor-pointer"
                title={isExpanded ? 'Shrink' : 'Expand window'}
              >
                {isExpanded ? (
                  <Minimize2 size={8} className="text-black/60 opacity-0 group-hover/lights:opacity-100 transition-opacity" />
                ) : (
                  <Maximize2 size={8} className="text-black/60 opacity-0 group-hover/lights:opacity-100 transition-opacity" />
                )}
              </button>

              <div className="h-4 w-[1px] bg-white/10 ml-1.5" />

              <div className="flex items-center gap-2 ml-1">
                <GeminiSparkleIcon size={16} />
                <span className="text-xs font-bold text-white tracking-wide">
                  STAT6 Copilot
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-medium bg-gradient-to-r from-blue-950/80 via-purple-950/80 to-slate-900 text-blue-300 border border-blue-500/30 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                  Gemini-Class Mesh
                </span>
              </div>
            </div>

            {/* Window Actions */}
            <div className="flex items-center gap-1.5 text-slate-400">
              <span className="hidden sm:flex items-center gap-1 text-[10px] text-slate-400 mr-1 font-mono">
                <Move size={10} className="text-slate-400" />
                Drag window
              </span>
              {/* Maximize to full tab */}
              <button
                onClick={() => {
                  onNavigateTab('ai');
                  setIsOpen(false);
                }}
                className="no-drag p-1.5 rounded-lg hover:bg-slate-700/50 hover:text-white transition cursor-pointer"
                title="Open full AI Tab"
              >
                <ArrowUpRight size={14} />
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
                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'} w-full`}
                  >
                    {msg.sender === 'user' ? (
                      <div className="flex flex-col items-end max-w-[85%] self-end">
                        <div className="text-[10px] text-slate-400 mb-1 px-1">
                          You • {msg.timestamp}
                        </div>
                        <div className="rounded-2xl rounded-tr-xs px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs leading-relaxed shadow-sm">
                          {msg.text}
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-start w-full">
                        {/* Gemini Assistant Header */}
                        <div className="flex items-center gap-2 mb-1 px-1">
                          <GeminiMiniSparkle size={13} />
                          <span className="text-[11px] font-bold text-white flex items-center gap-1.5">
                            STAT6 Copilot
                            <span className="text-[9px] font-sans font-medium px-1.5 py-0.2 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/30">
                              ✦ Gemini Mesh
                            </span>
                          </span>
                          <span className="text-[10px] text-slate-500">• {msg.timestamp}</span>
                          {msg.outputTier === 'TIER_3_RESTRICTED' && (
                            <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
                              <Lock size={9} />
                              Tier 3: In-House Boundary
                            </span>
                          )}
                        </div>

                        {/* Gemini Assistant Card */}
                        <div className="w-full rounded-2xl rounded-tl-xs p-3.5 bg-[#12192b] border border-slate-750/70 text-slate-100 shadow-sm space-y-2.5">
                          {/* Markdown formatted body */}
                          <GeminiMarkdownRenderer content={msg.text} />

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
                                  className="px-2 py-0.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 flex items-center gap-1 transition cursor-pointer"
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

                          {/* Gemini Action Footer */}
                          <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                            <div className="flex items-center gap-2">
                              {msg.sources && msg.sources.length > 0 ? (
                                <span className="font-mono text-[9px] px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-slate-400 flex items-center gap-1">
                                  <span>✦</span> Sources: {msg.sources.join(', ')}
                                </span>
                              ) : (
                                <span className="font-mono text-[9px] text-slate-500">
                                  ✦ Verified Ledger Engine
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-1">
                              <button
                                onClick={() => handleCopyMessage(msg.text, msg.id)}
                                className="px-2 py-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition flex items-center gap-1 cursor-pointer"
                                title="Copy response text"
                              >
                                {copiedMsgId === msg.id ? (
                                  <>
                                    <Check size={11} className="text-emerald-400" />
                                    <span className="text-emerald-400 text-[10px]">Copied</span>
                                  </>
                                ) : (
                                  <>
                                    <Copy size={11} />
                                    <span className="text-[10px]">Copy</span>
                                  </>
                                )}
                              </button>
                              <button
                                onClick={() => setFeedbackGiven(prev => ({ ...prev, [msg.id]: 'up' }))}
                                className={`p-1 rounded hover:bg-slate-800 transition cursor-pointer ${
                                  feedbackGiven[msg.id] === 'up' ? 'text-blue-400' : 'text-slate-500 hover:text-slate-300'
                                }`}
                                title="Helpful response"
                              >
                                <ThumbsUp size={11} />
                              </button>
                              <button
                                onClick={() => setFeedbackGiven(prev => ({ ...prev, [msg.id]: 'down' }))}
                                className={`p-1 rounded hover:bg-slate-800 transition cursor-pointer ${
                                  feedbackGiven[msg.id] === 'down' ? 'text-rose-400' : 'text-slate-500 hover:text-slate-300'
                                }`}
                                title="Improve response"
                              >
                                <ThumbsDown size={11} />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isThinking && (
                  <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
                    <RefreshCw size={14} className="animate-spin text-blue-400" />
                    <span>Executing args_schema verification across mesh...</span>
                  </div>
                )}
              </div>

              {/* Chat Input Bar (Gemini Floating Style) */}
              <div className="p-3 bg-[#0d1424] border-t border-slate-800 flex-shrink-0">
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="space-y-2"
                >
                  <div className="relative rounded-2xl bg-[#12192b] border border-slate-700/80 focus-within:border-blue-500/80 focus-within:ring-2 focus-within:ring-blue-500/20 p-2.5 transition-all shadow-md">
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
                      className="w-full bg-transparent text-slate-100 placeholder-slate-400 text-xs resize-none outline-hidden focus:ring-0 pr-10"
                    />
                    <div className="flex items-center justify-between pt-1.5 border-t border-slate-800/60 mt-1">
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                        <GeminiMiniSparkle size={11} />
                        <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-semibold">
                          Gemini Autonomous Mesh
                        </span>
                      </div>
                      <button
                        type="submit"
                        disabled={!inputValue.trim() || isThinking}
                        className="p-2 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 text-white transition-all transform hover:scale-105 active:scale-95 cursor-pointer shadow-md flex items-center justify-center"
                        title="Send message"
                      >
                        <Send size={13} />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 px-1">
                    <span>Press Enter to send • Shift+Enter for newline</span>
                    <span className="font-mono text-emerald-400 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      12 Live Tools
                    </span>
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
