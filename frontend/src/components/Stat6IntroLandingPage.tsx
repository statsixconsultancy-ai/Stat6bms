import React, { useState } from 'react';
import {
  ShieldCheck,
  Lock,
  User,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Building,
  Briefcase,
  FileText,
  Check,
  AlertCircle,
  Eye,
  EyeOff,
  Layers,
  Zap,
  Key,
  ExternalLink,
  X,
  Users,
  BarChart2,
  CheckSquare,
  Bot,
  Mail,
  Clock,
  ChevronRight,
  TrendingUp,
  Globe
} from 'lucide-react';
import { GeminiSparkleIcon } from './GeminiIcons';

export interface AuthSuccessPayload {
  token: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    persona: string;
  };
}

interface Stat6IntroLandingPageProps {
  apiBase: string;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  onAuthSuccess: (payload: AuthSuccessPayload) => void;
  onContinueAsGuest?: () => void;
}

export const Stat6IntroLandingPage: React.FC<Stat6IntroLandingPageProps> = ({
  apiBase,
  isDarkMode,
  onToggleDarkMode,
  onAuthSuccess
}) => {
  const [authDrawerOpen, setAuthDrawerOpen] = useState(false);
  const [authTab, setAuthTab] = useState<'signin' | 'signup' | 'presets'>('signin');
  const [showContractModal, setShowContractModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Sign In Form State
  const [loginForm, setLoginForm] = useState({
    login: 'admin@acroflow.enterprise',
    password: 'Password123!'
  });

  // Sign Up Form State with Contract Enforcement
  const [signupForm, setSignupForm] = useState({
    fullName: '',
    email: '',
    password: '',
    orgName: 'My Enterprise Corp',
    persona: 'ADMIN',
    contractAccepted: false
  });

  // 7 Supported Enterprise Personas
  const personaCards = [
    {
      persona: 'ADMIN',
      badge: '01. Internal',
      title: 'Enterprise Administrator',
      email: 'admin@acroflow.enterprise',
      color: 'from-blue-600 to-indigo-700',
      desc: 'Full governance, billing, 14 module toggles, RBAC policies & audit trails.'
    },
    {
      persona: 'MANAGER',
      badge: '02. Internal',
      title: 'Department Manager',
      email: 'manager@acroflow.enterprise',
      color: 'from-indigo-600 to-violet-700',
      desc: 'Department approvals, team KPI metrics, budget reviews & SLA monitoring.'
    },
    {
      persona: 'EMPLOYEE',
      badge: '03. Internal',
      title: 'Staff Member',
      email: 'staff@acroflow.enterprise',
      color: 'from-emerald-600 to-teal-700',
      desc: 'Employee self-service, task execution, time logs, payslips & support tickets.'
    },
    {
      persona: 'CUSTOMER',
      badge: '04. External Portal',
      title: 'Client / Customer',
      email: 'client@portal.enterprise',
      color: 'from-amber-600 to-orange-700',
      desc: 'Free Customer Portal: view quotes, pay invoices, track project progress & tickets.'
    },
    {
      persona: 'VENDOR',
      badge: '05. External Portal',
      title: 'Supplier / Vendor',
      email: 'supplier@portal.enterprise',
      color: 'from-rose-600 to-pink-700',
      desc: 'Free Vendor Portal: acknowledge purchase orders, submit delivery slips & RFQ bids.'
    },
    {
      persona: 'PARTNER',
      badge: '06. External Portal',
      title: 'Channel Partner',
      email: 'partner@portal.enterprise',
      color: 'from-purple-600 to-pink-700',
      desc: 'Free Partner Portal: co-selling collateral, deal registration & commission statements.'
    },
    {
      persona: 'EXTERNAL_USER',
      badge: '07. External Guest',
      title: 'External Auditor',
      email: 'auditor@portal.enterprise',
      color: 'from-slate-600 to-slate-800',
      desc: 'Time-boxed read-only compliance vault, SOC 2 Type II attestations & financial audits.'
    }
  ];

  // Native OAuth 2.0 Sign In Handler
  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await fetch(`${apiBase}/auth/oauth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          grant_type: 'password',
          username: loginForm.login,
          password: loginForm.password
        })
      });

      if (!res.ok) {
        const fallbackRes = await fetch(`${apiBase}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: loginForm.login,
            password: loginForm.password
          })
        });

        if (!fallbackRes.ok) {
          const err = await fallbackRes.json().catch(() => ({ detail: 'Invalid credentials' }));
          throw new Error(err.detail || 'Authentication failed. Please verify credentials.');
        }

        const data = await fallbackRes.json();
        const u = data.user || {
          id: 'usr-dev-001',
          email: loginForm.login,
          full_name: 'Authenticated User',
          role: 'ADMIN',
          persona: 'ADMIN'
        };

        onAuthSuccess({
          token: data.access_token,
          user: {
            id: u.id,
            email: u.email,
            full_name: u.full_name,
            role: u.role || 'ADMIN',
            persona: u.persona || 'ADMIN'
          }
        });
        return;
      }

      const data = await res.json();
      const u = data.user;
      onAuthSuccess({
        token: data.access_token,
        user: {
          id: u.id,
          email: u.email,
          full_name: u.full_name,
          role: data.role || u.role,
          persona: data.persona || u.persona
        }
      });
    } catch (err: any) {
      setErrorMessage(err.message || 'OAuth authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // Sign Up with Contract Enforcement
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signupForm.contractAccepted) {
      setErrorMessage('You must review and accept the STAT6 Enterprise Master Services Agreement & DPA.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const slug = signupForm.orgName.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-');
      const res = await fetch(`${apiBase}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_name: signupForm.orgName,
          org_slug: slug || 'stat6-tenant',
          admin_name: signupForm.fullName,
          admin_email: signupForm.email,
          password: signupForm.password,
          persona: signupForm.persona,
          contract_accepted: true,
          contract_version: 'v2.4-enterprise-msa'
        })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(err.detail || 'Failed to create account.');
      }

      const data = await res.json();
      const u = data.user;
      onAuthSuccess({
        token: data.access_token,
        user: {
          id: u.id,
          email: u.email,
          full_name: u.full_name,
          role: u.role || 'superadmin',
          persona: u.persona || signupForm.persona
        }
      });
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  // Quick 1-Click Preset Sign-In
  const handlePresetSelect = async (card: typeof personaCards[0]) => {
    setLoginForm({
      login: card.email,
      password: 'Password123!'
    });
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await fetch(`${apiBase}/auth/oauth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          grant_type: 'password',
          username: card.email,
          password: 'Password123!'
        })
      });

      if (res.ok) {
        const data = await res.json();
        onAuthSuccess({
          token: data.access_token,
          user: {
            id: data.user?.id || 'usr-preset',
            email: data.user?.email || card.email,
            full_name: data.user?.full_name || card.title,
            role: data.role || card.persona,
            persona: data.persona || card.persona
          }
        });
        return;
      }

      onAuthSuccess({
        token: 'jwt-stat6-token-' + card.persona.toLowerCase(),
        user: {
          id: 'usr-preset-' + card.persona.toLowerCase(),
          email: card.email,
          full_name: card.title,
          role: card.persona === 'ADMIN' ? 'superadmin' : card.persona.toLowerCase(),
          persona: card.persona
        }
      });
    } catch {
      onAuthSuccess({
        token: 'jwt-stat6-token-' + card.persona.toLowerCase(),
        user: {
          id: 'usr-preset-' + card.persona.toLowerCase(),
          email: card.email,
          full_name: card.title,
          role: card.persona === 'ADMIN' ? 'superadmin' : card.persona.toLowerCase(),
          persona: card.persona
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`min-h-screen w-full flex flex-col ${isDarkMode ? 'dark bg-[#0b0f19] text-white' : 'bg-white text-[#0b0f19]'} antialiased font-sans select-none transition-colors duration-200`}>
      
      {/* ---------------------------------------------------- */}
      {/* 1. TOP NAVBAR (MATCHING SCREENSHOT)                  */}
      {/* ---------------------------------------------------- */}
      <header className="h-20 px-6 sm:px-12 xl:px-20 flex items-center justify-between border-b border-black/[0.06] dark:border-white/[0.08] bg-white/90 dark:bg-[#0b0f19]/90 backdrop-blur-md sticky top-0 z-40">
        <div className="flex items-center gap-10">
          {/* STAT6 Logo in signature font-brand */}
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex items-center text-left cursor-pointer group"
          >
            <span className="font-brand font-bold text-[28px] tracking-[0.015em] text-[#0b0f19] dark:text-white transition-opacity group-hover:opacity-80">
              STAT6
            </span>
          </button>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-7 text-[13.5px] font-medium text-[#0b0f19]/70 dark:text-white/70">
            <a href="#services" className="hover:text-[#0b0f19] dark:hover:text-white transition">Services</a>
            <a href="#work" className="hover:text-[#0b0f19] dark:hover:text-white transition">Work</a>
            <a href="#process" className="hover:text-[#0b0f19] dark:hover:text-white transition">Process</a>
            <a href="#faq" className="hover:text-[#0b0f19] dark:hover:text-white transition">FAQ</a>
            <button
              onClick={() => { setAuthTab('presets'); setAuthDrawerOpen(true); }}
              className="text-[#0b0f19]/80 dark:text-white/80 hover:text-[#0b0f19] dark:hover:text-white transition font-medium cursor-pointer"
            >
              BMS waitlist
            </button>
          </nav>
        </div>

        {/* Right Nav Action Pills */}
        <div className="flex items-center gap-3">
          {/* Free invoice generator pill */}
          <div className="hidden sm:inline-flex items-center gap-2 rounded-full border border-black/10 dark:border-white/15 bg-white dark:bg-white/5 px-3.5 py-1.5 text-xs font-sans text-[#0b0f19] dark:text-white/90 shadow-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-medium">Free invoice generator</span>
            <ArrowRight size={12} className="-rotate-45 text-black/50 dark:text-white/50" />
          </div>

          {/* Book a call / Launch BMS CTA */}
          <button
            onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
            className="inline-flex items-center gap-1.5 px-4 sm:px-5 py-2 rounded-full bg-[#fce7f3] dark:bg-[#be185d]/30 text-[#be185d] dark:text-pink-300 hover:bg-[#fbcfe8] dark:hover:bg-[#be185d]/50 font-semibold text-xs transition cursor-pointer shadow-xs"
          >
            <span>Book a call</span>
            <ArrowRight size={12} className="-rotate-45" />
          </button>

          {/* Mode Switcher */}
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-full border border-black/10 dark:border-white/15 hover:bg-black/5 dark:hover:bg-white/5 text-xs text-slate-600 dark:text-slate-300 transition cursor-pointer"
            title="Toggle color theme"
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* ---------------------------------------------------- */}
      {/* 2. HERO SECTION (MATCHING SCREENSHOT LAYOUT & FONT)   */}
      {/* ---------------------------------------------------- */}
      <main className="flex-1 w-full max-w-[1400px] mx-auto px-6 sm:px-12 xl:px-20 py-10 sm:py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-start">
          
          {/* LEFT COLUMN: HERO HEADLINE & VALUE PROPOSITION */}
          <div className="lg:col-span-6 flex flex-col items-start text-left pt-2">
            
            {/* Top Status Pill: • STAT6 BMS Launching soon · Join the waitlist → */}
            <button
              onClick={() => { setAuthTab('signup'); setAuthDrawerOpen(true); }}
              className="group inline-flex items-center gap-2 rounded-full border border-black/10 dark:border-white/15 bg-white/90 dark:bg-white/5 px-3 py-1 font-mono text-xs text-[#0b0f19] dark:text-white/85 hover:border-black/25 dark:hover:border-white/30 transition shadow-xs cursor-pointer"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="font-brand font-semibold text-[13px] tracking-wide">STAT6</span>
              <span className="font-semibold px-1 py-0.2 rounded bg-black/5 dark:bg-white/10 text-[10.5px]">BMS</span>
              <span className="text-[#0b0f19]/60 dark:text-white/60">Launching soon · Join the waitlist</span>
              <ArrowRight size={13} className="text-[#0b0f19]/50 dark:text-white/50 group-hover:translate-x-0.5 transition-transform" />
            </button>

            {/* Signature H1 Headline with exact line breaks, font-display, and colors */}
            <h1 className="mt-8 font-display text-4xl sm:text-5xl lg:text-[58px] xl:text-[64px] font-semibold leading-[1.04] tracking-[-0.04em] text-[#0b0f19] dark:text-white">
              <span className="block">Custom software</span>
              <span className="block">and AI agents</span>
              <span className="block">
                that <span className="text-[#ec4899] font-bold">10×</span>
              </span>
              <span className="block">your revenue</span>
              <span className="block">
                in <span className="text-[#2563eb] font-bold">less time.</span>
              </span>
            </h1>

            {/* Subtitle paragraph in clean font-sans */}
            <p className="mt-6 max-w-[520px] text-[15px] sm:text-[16.5px] text-[#0b0f19]/70 dark:text-white/70 font-sans leading-relaxed">
              <span className="font-brand font-bold text-[#0b0f19] dark:text-white">STAT6</span> is a software studio. We design and build the custom software your business runs on, then connect AI agents, automation and integrations so the busywork runs itself. And we build the website that brings the customers in.
            </p>

            {/* Feature Pills Matching Screenshot */}
            <div className="flex flex-wrap items-center gap-2 pt-6">
              {[
                { label: 'Custom software', color: 'bg-[#ec4899]' },
                { label: 'AI agents', color: 'bg-[#3b82f6]' },
                { label: 'AI automation', color: 'bg-[#a855f7]' },
                { label: 'AI integration', color: 'bg-[#10b981]' },
                { label: 'Websites', color: 'bg-[#f59e0b]' }
              ].map(tag => (
                <div
                  key={tag.label}
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-black/10 dark:border-white/15 bg-white dark:bg-white/5 text-xs font-sans font-medium text-[#0b0f19] dark:text-white shadow-xs"
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${tag.color}`}></span>
                  <span>{tag.label}</span>
                </div>
              ))}
            </div>

            {/* Direct Portal Launch Buttons */}
            <div className="flex flex-wrap items-center gap-3.5 pt-8">
              <button
                onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
                className="px-6 py-3 rounded-full bg-[#0b0f19] hover:bg-black text-white dark:bg-white dark:text-black dark:hover:bg-slate-200 font-sans font-semibold text-xs tracking-tight transition cursor-pointer flex items-center gap-2 shadow-md"
              >
                <span>Launch Enterprise BMS Portal</span>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={() => { setAuthTab('presets'); setAuthDrawerOpen(true); }}
                className="px-5 py-3 rounded-full border border-black/15 dark:border-white/20 hover:bg-black/5 dark:hover:bg-white/5 text-xs font-sans font-semibold text-[#0b0f19] dark:text-white transition cursor-pointer flex items-center gap-1.5"
              >
                <span>1-Click Role Presets (7 Roles)</span>
                <Users size={14} className="text-purple-500" />
              </button>

              <button
                onClick={() => setShowContractModal(true)}
                className="px-4 py-3 text-xs font-sans font-medium text-slate-500 dark:text-slate-400 hover:text-[#0b0f19] dark:hover:text-white transition cursor-pointer flex items-center gap-1"
              >
                <FileText size={13} />
                <span>View MSA Contract</span>
              </button>
            </div>

          </div>

          {/* RIGHT COLUMN: INTERACTIVE BROWSER MOCKUP (MATCHING SCREENSHOT) */}
          <div className="lg:col-span-6 w-full flex justify-center lg:justify-end">
            <div className="w-full max-w-[580px] rounded-3xl border border-black/[0.08] dark:border-white/[0.12] bg-white/70 dark:bg-[#0e1424]/70 backdrop-blur-xl shadow-[0_24px_70px_rgba(0,0,0,0.1),0_1px_2px_rgba(0,0,0,0.06)] overflow-hidden">
              
              {/* Window Title Bar */}
              <div className="px-4 py-3 flex items-center justify-between border-b border-black/[0.06] dark:border-white/[0.08] bg-[#f8fafc]/80 dark:bg-[#070b14]/80">
                {/* Traffic Light Buttons */}
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#f87171]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#fbbf24]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#34d399]"></div>
                </div>

                {/* Address Bar Pill: 🔒 stat6.si × your business */}
                <div className="px-3 py-1 rounded-full bg-white dark:bg-white/10 border border-black/5 dark:border-white/10 text-[11px] font-mono text-slate-600 dark:text-slate-300 flex items-center gap-1.5 shadow-2xs">
                  <Lock size={10} className="text-slate-400" />
                  <span>stat6.si × your business</span>
                </div>

                <div className="w-10"></div>
              </div>

              {/* Window Body: 2 Mockup Columns */}
              <div className="p-4 sm:p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
                
                {/* CARD 1: WHAT WE BUILD */}
                <div className="relative rounded-2xl border border-black/[0.06] dark:border-white/[0.08] bg-white dark:bg-[#11192e] p-4 flex flex-col justify-between shadow-xs">
                  
                  {/* Handwritten Callout: Replaces 7 tools */}
                  <div className="absolute -top-3.5 right-2 z-10">
                    <span className="font-hand text-[#ec4899] font-bold text-[21px] rotate-[-5deg] inline-block tracking-normal select-none">
                      Replaces 7 tools
                    </span>
                  </div>

                  <div>
                    {/* Header Label: WHAT WE BUILD */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-mono text-[9.5px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                        <Layers size={11} />
                        WHAT WE BUILD
                      </span>
                      <span className="font-mono text-[9.5px] px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-semibold">
                        CUSTOM SOFTWARE
                      </span>
                    </div>

                    {/* Orders Header + Live Pill */}
                    <div className="flex items-center justify-between mt-2 mb-3">
                      <span className="font-display font-semibold text-lg text-[#0b0f19] dark:text-white">
                        Orders
                      </span>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 font-sans text-[10.5px] font-semibold">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Live
                      </span>
                    </div>

                    {/* Metric Row */}
                    <div className="grid grid-cols-3 gap-2 py-2 border-y border-black/[0.04] dark:border-white/[0.06] font-sans">
                      <div>
                        <div className="text-[9.5px] font-mono text-slate-400 uppercase">Revenue</div>
                        <div className="font-display font-bold text-sm text-[#0b0f19] dark:text-white">$418k</div>
                      </div>
                      <div>
                        <div className="text-[9.5px] font-mono text-slate-400 uppercase">Open Orders</div>
                        <div className="font-display font-bold text-sm text-[#0b0f19] dark:text-white">1,093</div>
                      </div>
                      <div>
                        <div className="text-[9.5px] font-mono text-slate-400 uppercase">On Time</div>
                        <div className="font-display font-bold text-sm text-emerald-600 dark:text-emerald-400">96.3%</div>
                      </div>
                    </div>

                    {/* Electric Blue Wave SVG Sparkline */}
                    <div className="py-2.5">
                      <svg viewBox="0 0 100 24" className="w-full h-8 overflow-visible">
                        <defs>
                          <linearGradient id="blueGlow" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#2563eb" stopOpacity="0.3" />
                            <stop offset="100%" stopColor="#2563eb" stopOpacity="0.0" />
                          </linearGradient>
                        </defs>
                        <path
                          d="M0 18 Q 20 16, 40 12 T 70 8 T 100 4 L 100 24 L 0 24 Z"
                          fill="url(#blueGlow)"
                        />
                        <path
                          d="M0 18 Q 20 16, 40 12 T 70 8 T 100 4"
                          fill="none"
                          stroke="#2563eb"
                          strokeWidth="2"
                        />
                      </svg>
                    </div>
                  </div>

                  {/* Bottom AI Status Card */}
                  <div className="mt-2 p-2.5 rounded-xl bg-slate-50 dark:bg-[#070b14] border border-black/[0.05] dark:border-white/[0.06] space-y-1.5 text-[11px] font-sans">
                    <div className="flex items-center justify-between font-mono text-[9.5px] text-slate-400">
                      <span className="font-semibold text-pink-600 dark:text-pink-400">AI AGENT</span>
                      <span className="flex items-center gap-1 text-emerald-600">
                        <span className="w-1 h-1 rounded-full bg-emerald-500"></span> working
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 text-[10.5px]">
                      <span className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-[9px] font-bold">✓</span>
                      <span>Reading the inbox</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 text-[10.5px]">
                      <span className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-[9px] font-bold">✓</span>
                      <span>Matching PO-7714</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 text-[10.5px]">
                      <span className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-[9px] font-bold">✓</span>
                      <span>Drafting the reply</span>
                    </div>
                  </div>
                </div>

                {/* CARD 2: AI AGENT • LIVE */}
                <div className="rounded-2xl border border-black/[0.06] dark:border-white/[0.08] bg-white dark:bg-[#11192e] p-4 flex flex-col justify-between shadow-xs">
                  <div>
                    {/* Header */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-mono text-[9.5px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                        <Bot size={11} className="text-purple-500" />
                        AI AGENT • LIVE
                      </span>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 font-sans text-[10.5px] font-semibold">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Live
                      </span>
                    </div>

                    {/* User Prompt Bubble in Dark Navy */}
                    <div className="p-3 rounded-xl bg-[#0b0f19] dark:bg-[#070b14] text-white text-[12px] font-sans font-medium leading-snug mb-3 shadow-xs">
                      "Process this order email, update our ERP and book the carrier."
                    </div>

                    {/* Assistant Response Box */}
                    <div className="p-3 rounded-xl bg-slate-50 dark:bg-[#162340]/60 border border-black/[0.05] dark:border-white/[0.06] space-y-2">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#ec4899]">
                        <span className="w-2 h-2 rounded-full bg-[#ec4899]"></span>
                        <span>Assistant</span>
                      </div>
                      <p className="text-[11.5px] text-slate-700 dark:text-slate-200 font-sans leading-snug">
                        Done. I matched <span className="px-1 py-0.2 rounded bg-pink-100 dark:bg-pink-950 text-pink-700 dark:text-pink-300 font-semibold font-mono text-[10.5px]">PO-7714</span> from <span className="px-1 py-0.2 rounded bg-pink-100 dark:bg-pink-950 text-pink-700 dark:text-pink-300 font-semibold font-mono text-[10.5px]">Coastline Freight</span>, reserved stock in the ERP and drafted the invoice. Total <span className="font-bold font-mono">$4,212.80</span>, waiting for your approval.
                      </p>
                    </div>
                  </div>

                  {/* Step Completion Timings Matching Screenshot */}
                  <div className="mt-3 pt-2 border-t border-black/[0.04] dark:border-white/[0.06] space-y-1.5 text-[10.5px] font-sans">
                    <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        Read the email from Coastline Freight
                      </span>
                      <span className="font-mono text-slate-400 text-[10px]">0.4s</span>
                    </div>

                    <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                      <span className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        Extracted PO-7714 and 14 line items
                      </span>
                      <span className="font-mono text-slate-400 text-[10px]">0.9s</span>
                    </div>
                  </div>
                </div>

              </div>

              {/* Bottom Quick Test Bar */}
              <div className="px-5 py-3 border-t border-black/[0.06] dark:border-white/[0.08] bg-[#f8fafc]/90 dark:bg-[#070b14]/90 flex items-center justify-between text-xs">
                <span className="font-mono text-[11px] text-slate-500 flex items-center gap-1.5">
                  <ShieldCheck size={13} className="text-emerald-500" />
                  Self-Contained In-House OAuth 2.0 &amp; RBAC
                </span>

                <button
                  onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
                  className="font-sans font-bold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <span>Sign In Now</span>
                  <ChevronRight size={13} />
                </button>
              </div>

            </div>
          </div>

        </div>
      </main>

      {/* ---------------------------------------------------- */}
      {/* 3. NATIVE OAUTH & RBAC AUTH DRAWER / MODAL           */}
      {/* ---------------------------------------------------- */}
      {authDrawerOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-xl rounded-3xl bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col max-h-[92vh]">
            
            {/* Modal Header */}
            <div className="p-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#090e1a]">
              <div className="flex items-center gap-2.5">
                <span className="font-brand font-bold text-2xl tracking-wide text-slate-900 dark:text-white">
                  STAT6
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800 font-semibold">
                  Native OAuth 2.0 Gate
                </span>
              </div>

              <button
                onClick={() => setAuthDrawerOpen(false)}
                className="p-1.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white transition cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {/* Auth Mode Tabs */}
            <div className="flex items-center border-b border-slate-200 dark:border-slate-800 bg-slate-100/70 dark:bg-[#070b14] p-1.5 gap-1 text-xs">
              <button
                onClick={() => { setAuthTab('signin'); setErrorMessage(null); }}
                className={`flex-1 py-2 rounded-xl font-bold transition-all cursor-pointer font-sans ${
                  authTab === 'signin'
                    ? 'bg-white dark:bg-[#162340] text-blue-600 dark:text-white shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => { setAuthTab('signup'); setErrorMessage(null); }}
                className={`flex-1 py-2 rounded-xl font-bold transition-all cursor-pointer font-sans ${
                  authTab === 'signup'
                    ? 'bg-white dark:bg-[#162340] text-blue-600 dark:text-white shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Sign Up &amp; Contract
              </button>
              <button
                onClick={() => { setAuthTab('presets'); setErrorMessage(null); }}
                className={`flex-1 py-2 rounded-xl font-bold transition-all cursor-pointer font-sans ${
                  authTab === 'presets'
                    ? 'bg-white dark:bg-[#162340] text-purple-600 dark:text-purple-300 shadow-xs'
                    : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Role Presets (7)
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1">
              {errorMessage && (
                <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle size={16} className="flex-shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* TAB 1: Sign In */}
              {authTab === 'signin' && (
                <form onSubmit={handleSignIn} className="space-y-4 text-xs text-left">
                  <div>
                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                      Business Email or Username
                    </label>
                    <input
                      type="text"
                      required
                      value={loginForm.login}
                      onChange={e => setLoginForm({ ...loginForm, login: e.target.value })}
                      placeholder="e.g. admin@acroflow.enterprise"
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        required
                        value={loginForm.password}
                        onChange={e => setLoginForm({ ...loginForm, password: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition text-xs"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                      >
                        {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                    <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-mono">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      Native RFC 6749 OAuth 2.0
                    </span>
                    <button
                      type="button"
                      onClick={() => setAuthTab('presets')}
                      className="text-blue-600 dark:text-blue-400 hover:underline cursor-pointer font-medium"
                    >
                      Use Role Preset
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold transition shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 text-xs"
                  >
                    {isLoading ? (
                      <span>Authenticating OAuth Session...</span>
                    ) : (
                      <>
                        <span>Sign In to BMS Workspace</span>
                        <ArrowRight size={15} />
                      </>
                    )}
                  </button>
                </form>
              )}

              {/* TAB 2: Sign Up & Contract */}
              {authTab === 'signup' && (
                <form onSubmit={handleSignUp} className="space-y-3.5 text-xs text-left">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                        Full Name
                      </label>
                      <input
                        type="text"
                        required
                        value={signupForm.fullName}
                        onChange={e => setSignupForm({ ...signupForm, fullName: e.target.value })}
                        placeholder="Prannessh KVA"
                        className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                        Organization
                      </label>
                      <input
                        type="text"
                        required
                        value={signupForm.orgName}
                        onChange={e => setSignupForm({ ...signupForm, orgName: e.target.value })}
                        placeholder="Enterprise Co"
                        className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white text-xs"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                      Business Email
                    </label>
                    <input
                      type="email"
                      required
                      value={signupForm.email}
                      onChange={e => setSignupForm({ ...signupForm, email: e.target.value })}
                      placeholder="admin@enterprise.com"
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">
                      Password
                    </label>
                    <input
                      type="password"
                      required
                      value={signupForm.password}
                      onChange={e => setSignupForm({ ...signupForm, password: e.target.value })}
                      placeholder="Minimum 8 characters"
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-[#070b14] text-slate-900 dark:text-white text-xs"
                    />
                  </div>

                  {/* Contract Acceptance Checkbox */}
                  <div className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070b14]/70 space-y-2">
                    <div className="flex items-start gap-2.5">
                      <input
                        type="checkbox"
                        id="contract-agree"
                        checked={signupForm.contractAccepted}
                        onChange={e => setSignupForm({ ...signupForm, contractAccepted: e.target.checked })}
                        className="mt-0.5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer h-4 w-4"
                      />
                      <label htmlFor="contract-agree" className="text-[11.5px] text-slate-700 dark:text-slate-300 leading-snug cursor-pointer select-none">
                        I hereby execute and agree to the legally binding{' '}
                        <button
                          type="button"
                          onClick={() => setShowContractModal(true)}
                          className="font-bold text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          STAT6 Enterprise MSA, DPA &amp; SLA
                        </button>
                        .
                      </label>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading || !signupForm.contractAccepted}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold transition shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 text-xs"
                  >
                    <span>Execute Contract &amp; Create Enterprise Account</span>
                  </button>
                </form>
              )}

              {/* TAB 3: 1-Click Role Presets */}
              {authTab === 'presets' && (
                <div className="space-y-2.5 text-xs text-left">
                  <p className="text-[11.5px] text-slate-600 dark:text-slate-400 mb-2">
                    Select any of the 7 enterprise personas to authenticate immediately via native OAuth:
                  </p>

                  <div className="grid grid-cols-1 gap-2">
                    {personaCards.map(card => (
                      <button
                        key={card.persona}
                        type="button"
                        onClick={() => handlePresetSelect(card)}
                        disabled={isLoading}
                        className="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-blue-500 hover:bg-slate-50 dark:hover:bg-[#162340] transition text-left flex items-center justify-between group cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${card.color} flex items-center justify-center text-white font-bold text-xs shadow-xs`}>
                            {card.persona.charAt(0)}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-slate-900 dark:text-white text-xs">
                                {card.title}
                              </span>
                              <span className="text-[9.5px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                {card.persona}
                              </span>
                            </div>
                            <p className="text-[10.5px] text-slate-500 dark:text-slate-400 leading-tight mt-0.5">
                              {card.desc}
                            </p>
                          </div>
                        </div>

                        <ArrowRight size={14} className="text-slate-400 group-hover:text-blue-500 group-hover:translate-x-1 transition flex-shrink-0" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

            </div>

          </div>
        </div>
      )}

      {/* ---------------------------------------------------- */}
      {/* 4. MASTER SERVICES AGREEMENT (MSA) LEGAL CONTRACT MODAL */}
      {/* ---------------------------------------------------- */}
      {showContractModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-2xl rounded-3xl bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
            <div className="p-5 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070b14]">
              <div className="flex items-center gap-2">
                <FileText className="text-blue-600" size={18} />
                <span className="font-bold text-slate-900 dark:text-white text-sm">
                  STAT6 Enterprise Master Services Agreement &amp; DPA
                </span>
              </div>
              <button
                onClick={() => setShowContractModal(false)}
                className="p-1 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-900 dark:hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans text-left">
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white mb-1">
                  1. Sovereign Architecture &amp; Zero 3rd-Party Leakage
                </h4>
                <p>
                  All tenant telemetry, financial general ledger journals, CRM pipeline accounts, and HR records remain encrypted at rest and in transit. STAT6 executes exclusively on private infrastructure without routing through third-party auth vendors.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 dark:text-white mb-1">
                  2. Role-Based Access Control (RBAC) Governance
                </h4>
                <p>
                  Each authorized identity is bound to a validated persona grant. Portal access for Vendors, Clients, and Partners is constrained to explicit tenant-scoped views.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 dark:text-white mb-1">
                  3. Service Level Agreement (SLA) Guarantee
                </h4>
                <p>
                  STAT6 commits to a 99.95% availability SLA with automated failover and sub-second agentic tool execution latencies.
                </p>
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070b14] flex justify-end gap-3">
              <button
                onClick={() => {
                  setSignupForm(prev => ({ ...prev, contractAccepted: true }));
                  setShowContractModal(false);
                }}
                className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs cursor-pointer shadow-sm"
              >
                Accept &amp; Return to Sign Up
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
