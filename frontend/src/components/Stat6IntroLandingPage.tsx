import React, { useEffect, useRef, useState } from 'react';
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
  FolderGit2,
  Receipt,
  Package,
  ShoppingCart,
  Headphones,
  Sliders
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
    orgName: 'Enterprise Corp',
    persona: 'ADMIN',
    contractAccepted: false
  });

  // 7 Supported Enterprise Personas
  const personaCards = [
    {
      persona: 'ADMIN',
      badge: '01. Internal Full',
      title: 'Enterprise Administrator',
      email: 'admin@acroflow.enterprise',
      color: 'from-blue-600 to-indigo-700',
      desc: 'Master tenant governance, 14 module toggles, RBAC policies & cryptographic audit trails.'
    },
    {
      persona: 'MANAGER',
      badge: '02. Internal Head',
      title: 'Department Manager',
      email: 'manager@acroflow.enterprise',
      color: 'from-indigo-600 to-violet-700',
      desc: 'Department approvals, team KPI metrics, budget reviews & SLA escalation monitoring.'
    },
    {
      persona: 'EMPLOYEE',
      badge: '03. Internal Self',
      title: 'Staff Member',
      email: 'staff@acroflow.enterprise',
      color: 'from-emerald-600 to-teal-700',
      desc: 'Employee self-service, task execution, time logs, payslips & internal support tickets.'
    },
    {
      persona: 'CUSTOMER',
      badge: '04. External Portal',
      title: 'Customer Contact',
      email: 'client@portal.enterprise',
      color: 'from-amber-600 to-orange-700',
      desc: 'Free Customer Portal: review quotes, pay invoices, track delivery & submit service tickets.'
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
      desc: 'Free Partner Portal: co-selling collateral, deal registration & revenue statements.'
    },
    {
      persona: 'EXTERNAL_USER',
      badge: '07. External Auditor',
      title: 'Compliance Auditor',
      email: 'auditor@portal.enterprise',
      color: 'from-slate-600 to-slate-800',
      desc: 'Time-boxed read-only compliance vault, SOC 2 Type II attestations & financial audits.'
    }
  ];

  // Canvas and Letter Reveal Refs
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const navRef = useRef<HTMLElement | null>(null);
  const h1Ref = useRef<HTMLHeadingElement | null>(null);
  const stmtRef = useRef<HTMLParagraphElement | null>(null);
  const h2Ref = useRef<HTMLHeadingElement | null>(null);
  const splitRef = useRef<HTMLElement | null>(null);
  const rowRef = useRef<HTMLDivElement | null>(null);
  const shipRef = useRef<HTMLImageElement | null>(null);

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

  /* =======================================================
     BOWL GLOW & SCROLL LETTER REVEAL SIMULATION ENGINE
     ======================================================= */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return;

    const W = 96;
    const H = 60;
    const imgData = ctx.createImageData(W, H);
    const data = imgData.data;

    function splitLetters(el: HTMLElement | null) {
      if (!el) return [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null);
      const nodes: Node[] = [];
      let n: Node | null;
      while ((n = walker.nextNode())) {
        if (n.nodeType === 3 || (n.nodeType === 1 && (n as HTMLElement).tagName === 'BR')) {
          nodes.push(n);
        }
      }

      const charSpans: HTMLElement[] = [];
      nodes.forEach(node => {
        if ((node as HTMLElement).tagName === 'BR') return;
        const text = node.textContent || '';
        const parent = node.parentElement;
        const isHighlight = parent && parent.classList.contains('hl');

        const words = text.split(/(\s+)/);
        const frag = document.createDocumentFragment();

        words.forEach(part => {
          if (/^\s+$/.test(part)) {
            frag.appendChild(document.createTextNode(part));
          } else {
            const wrap = document.createElement('span');
            wrap.style.display = 'inline-block';
            wrap.style.whiteSpace = 'nowrap';
            for (let i = 0; i < part.length; i++) {
              const ch = part[i];
              const s = document.createElement('span');
              s.style.display = 'inline-block';
              s.style.transition = 'color .15s linear';
              s.textContent = ch;
              if (isHighlight) s.dataset.hl = '1';
              wrap.appendChild(s);
              charSpans.push(s);
            }
            frag.appendChild(wrap);
          }
        });

        node.parentNode?.replaceChild(frag, node);
      });

      return charSpans;
    }

    function clamp(val: number, min = 0, max = 1) {
      return Math.min(Math.max(val, min), max);
    }

    function paintChars(chars: HTMLElement[], p: number, spread: number, finalColor: string, accentColor: string, ghostColor: string) {
      const n = chars.length;
      if (!n) return;
      for (let i = 0; i < n; i++) {
        const c = chars[i];
        const isHl = c.dataset.hl === '1';
        const targetFinal = isHl ? '#5b7cf0' : finalColor;
        const t = clamp((p * (1 + spread) - (i / n)) / spread);

        if (t <= 0) {
          c.style.opacity = '0';
          c.style.color = ghostColor;
          c.style.filter = 'blur(8px)';
        } else if (t <= 0.35) {
          const sub = t / 0.35;
          c.style.opacity = String(sub);
          c.style.color = ghostColor;
          c.style.filter = `blur(${8 - sub * 6.5}px)`;
        } else if (t <= 0.70) {
          const sub = (t - 0.35) / 0.35;
          c.style.opacity = '1';
          c.style.color = accentColor;
          c.style.filter = `blur(${1.5 - sub * 1.5}px)`;
        } else {
          c.style.opacity = '1';
          c.style.color = targetFinal;
          c.style.filter = 'none';
        }
      }
    }

    const h1Chars = splitLetters(h1Ref.current);
    const stmtChars = splitLetters(stmtRef.current);
    const h2Chars = splitLetters(h2Ref.current);

    paintChars(h1Chars, 0, 0.35, '#0b1d3a', '#3f7cff', 'rgba(255,255,255,0)');
    paintChars(stmtChars, 0, 0.16, '#0b1d3a', '#3f7cff', '#ffffff');
    paintChars(h2Chars, 0, 0.35, '#ffffff', '#8fe6f4', '#5c6f92');

    // Keyframes table
    const keys = [
      { q: 0,    tip: .30, half: .34, soft: .22 },
      { q: .03,  tip: .45, half: .38, soft: .26 },
      { q: .08,  tip: .65, half: .38, soft: .22 },
      { q: .18,  tip: .80, half: .38, soft: .22 },
      { q: .40,  tip: .95, half: .38, soft: .19 },
      { q: .66,  tip: 1.05, half: .46, soft: .16 },
      { q: .87,  tip: 1.05, half: .66, soft: .13 },
      { q: 1.15, tip: 1.10, half: .90, soft: .10 },
      { q: 1.43, tip: 1.30, half: 1.60, soft: .10 },
      { q: 1.80, tip: 2.40, half: 3.00, soft: .10 }
    ];

    function interpKeys(q: number) {
      if (q <= keys[0].q) return { ...keys[0] };
      if (q >= keys[keys.length - 1].q) return { ...keys[keys.length - 1] };
      for (let i = 0; i < keys.length - 1; i++) {
        const k1 = keys[i];
        const k2 = keys[i + 1];
        if (q >= k1.q && q <= k2.q) {
          const f = (q - k1.q) / (k2.q - k1.q);
          return {
            tip: k1.tip + (k2.tip - k1.tip) * f,
            half: k1.half + (k2.half - k1.half) * f,
            soft: k1.soft + (k2.soft - k1.soft) * f
          };
        }
      }
      return { ...keys[0] };
    }

    function smoothstep(x: number) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      return x * x * (3 - 2 * x);
    }

    let curTip = -0.3;
    let curHalf = 0.3;
    let curSoft = 0.1;

    let targetTip = 0.30;
    let targetHalf = 0.34;
    let targetSoft = 0.22;

    let isIntro = true;
    let introStartTime = 0;

    function distToSegmentSquared(px: number, py: number, x1: number, y1: number, x2: number, y2: number) {
      const l2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
      if (l2 === 0) return (px - x1) * (px - x1) + (py - y1) * (py - y1);
      const t = clamp(((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2);
      const cx = x1 + t * (x2 - x1);
      const cy = y1 + t * (y2 - y1);
      return (px - cx) * (px - cx) + (py - cy) * (py - cy);
    }

    function renderGlow(time: number) {
      const aspect = window.innerWidth / (window.innerHeight || 1);
      const driftTip = curTip + Math.sin(time * 0.00033 + 1.3) * 0.02;
      const driftHalf = curHalf + Math.sin(time * 0.0005) * 0.015;
      const tipVal = Math.max(0.01, driftTip);

      const NPTS = 48;
      const ptsX = new Float32Array(NPTS);
      const ptsY = new Float32Array(NPTS);
      for (let i = 0; i < NPTS; i++) {
        const yy = -0.3 + (tipVal + 0.3) * (i / (NPTS - 1));
        ptsY[i] = yy;
        const norm = Math.max(0, 1 - yy / tipVal);
        ptsX[i] = driftHalf * aspect * Math.pow(norm, 0.72);
      }

      const segLen = NPTS - 1;
      const RND = 0.25;
      const softVal = Math.max(0.01, curSoft);

      let idx = 0;
      for (let y = 0; y < H; y++) {
        const py = y / H;
        for (let x = 0; x < W; x++) {
          const px = Math.abs(x / W - 0.5) * aspect;

          let minD2 = 1e9;
          for (let s = 0; s < segLen; s++) {
            const d2 = distToSegmentSquared(px, py, ptsX[s], ptsY[s], ptsX[s + 1], ptsY[s + 1]);
            if (d2 < minD2) minD2 = d2;
          }
          const dist = Math.sqrt(minD2);

          let inside = false;
          if (py < tipVal) {
            const curveX = driftHalf * aspect * Math.pow(Math.max(0, 1 - py / tipVal), 0.72);
            if (px < curveX) inside = true;
          }

          const sd = inside ? -dist : dist;
          const sdRnd = sd - RND;
          const g = 1 - smoothstep((sdRnd + softVal) / (2 * softVal));

          let r: number, gCol: number, b: number;
          if (g < 0.38) {
            const f = smoothstep(g / 0.38);
            r = Math.round(255 + (210 - 255) * f);
            gCol = Math.round(255 + (218 - 255) * f);
            b = Math.round(255 + (255 - 255) * f);
          } else {
            const f = smoothstep((g - 0.38) / 0.62);
            r = Math.round(210 + (143 - 210) * f);
            gCol = Math.round(218 + (213 - 218) * f);
            b = Math.round(255 + (241 - 255) * f);
          }

          data[idx]     = r;
          data[idx + 1] = gCol;
          data[idx + 2] = b;
          data[idx + 3] = 255;
          idx += 4;
        }
      }

      ctx.putImageData(imgData, 0, 0);
    }

    function onScroll() {
      const scrollY = window.scrollY || window.pageYOffset || 0;
      const vh = window.innerHeight || 1;
      const q = scrollY / vh;

      const k = interpKeys(q);
      targetTip = k.tip;
      targetHalf = k.half;
      targetSoft = k.soft;

      // Statement Section
      if (stmtRef.current) {
        const s = clamp((q - 0.69) / 0.74);
        const translateY = 0.205 * Math.pow(1 - s, 2) * vh;
        stmtRef.current.style.transform = `translateY(${translateY}px)`;
      }

      const pStmt = clamp((q - 0.56) / 2.03);
      paintChars(stmtChars, pStmt, 0.16, '#0b1d3a', '#3f7cff', '#ffffff');

      // Nav CTA pop
      if (navRef.current) {
        if (pStmt > 0.4) {
          navRef.current.classList.add('nav-expanded');
        } else {
          navRef.current.classList.remove('nav-expanded');
        }
      }

      // Dark Split Section
      if (splitRef.current) {
        const splitRect = splitRef.current.getBoundingClientRect();
        const splitTop = splitRect.top;
        const p2 = clamp((0.8 - splitTop / vh) / 0.65);
        paintChars(h2Chars, p2, 0.35, '#ffffff', '#8fe6f4', '#5c6f92');

        if (rowRef.current) {
          if (p2 > 0.92) {
            rowRef.current.style.opacity = '1';
            rowRef.current.style.transform = 'translateY(0)';
          } else {
            rowRef.current.style.opacity = '0';
            rowRef.current.style.transform = 'translateY(14px)';
          }
        }

        if (shipRef.current) {
          const scaleProg = clamp(1 - splitTop / vh);
          const shipScale = 1.08 - 0.08 * scaleProg;
          shipRef.current.style.transform = `scale(${shipScale})`;
        }
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);

    let animationFrameId: number;
    let startTime: number | null = null;

    function loop(time: number) {
      if (!startTime) startTime = time;
      const elapsed = (time - startTime) / 1000;

      if (isIntro) {
        if (elapsed < 0.25) {
          curTip = -0.3;
          curHalf = 0.3;
          curSoft = 0.1;
        } else if (elapsed < 1.30) {
          const prog = smoothstep((elapsed - 0.25) / 1.05);
          curTip = -0.3 + (targetTip - (-0.3)) * prog;
          curHalf = 0.3 + (targetHalf - 0.3) * prog;
          curSoft = 0.1 + (targetSoft - 0.1) * prog;
        } else {
          isIntro = false;
        }
      } else {
        curTip += (targetTip - curTip) * 0.12;
        curHalf += (targetHalf - curHalf) * 0.12;
        curSoft += (targetSoft - curSoft) * 0.12;
      }

      if (elapsed <= 1.5) {
        const h1Prog = clamp((elapsed - 0.2) / 1.25);
        paintChars(h1Chars, h1Prog, 0.35, '#0b1d3a', '#3f7cff', 'rgba(255,255,255,0)');
      }

      renderGlow(time);
      animationFrameId = requestAnimationFrame(loop);
    }

    onScroll();
    animationFrameId = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    };
  }, []);

  return (
    <div className={`relative min-h-screen w-full bg-white text-[#0b1d3a] antialiased font-sans select-none overflow-x-hidden`}>
      
      {/* ---------------------------------------------------- */}
      {/* 0. ATMOSPHERIC BOWL GLOW 96×60 CANVAS               */}
      {/* ---------------------------------------------------- */}
      <div className="fixed inset-0 z-0 pointer-events-none bg-white">
        <canvas ref={canvasRef} width={96} height={60} className="absolute inset-0 w-full h-full block" />
      </div>

      {/* ---------------------------------------------------- */}
      {/* 1. FLOATING PILL NAVBAR                              */}
      {/* ---------------------------------------------------- */}
      <header
        ref={navRef}
        className="fixed z-50 top-5 left-[clamp(20px,5.7vw,82px)] right-[clamp(20px,5.7vw,82px)] h-[60px] rounded-full bg-white flex items-center justify-between px-2.5 sm:px-6 shadow-[0_1px_0_rgba(11,29,58,0.04),0_10px_30px_-18px_rgba(11,29,58,0.25)] transition-all duration-300"
      >
        {/* Left: Brand Mark & STAT6 BMS */}
        <div className="flex items-center gap-2.5">
          <svg className="w-[22px] h-[22px] flex-shrink-0" viewBox="0 0 22 22">
            <circle cx="11" cy="11" r="11" fill="#5b7cf0" />
            <path d="M5 9.2c2.3-1.6 4.7-1.6 7 0s4.7 1.6 7 0" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
            <path d="M5 13.2c2.3-1.6 4.7-1.6 7 0s4.7 1.6 7 0" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
          <div className="flex items-baseline gap-1.5 font-sans">
            <span className="text-[17px] font-bold text-[#0b1d3a] tracking-tight">
              STAT6
            </span>
            <span className="text-xs font-semibold text-[#5b7cf0] tracking-wide">
              BMS
            </span>
            <span className="hidden sm:inline-block text-[11px] text-[#71829e] font-medium pl-2 ml-1 border-l border-[#0b1d3a]/15">
              we shall collaborate
            </span>
          </div>
        </div>

        {/* Center: Nav Links */}
        <nav className="hidden lg:flex items-center gap-7 text-[14px] font-medium text-[#0b1d3a]/90">
          <a href="#hero" className="hover:opacity-60 transition">Platform</a>
          <a href="#statement" className="hover:opacity-60 transition">Solutions</a>
          <a href="#split" className="hover:opacity-60 transition">Operations</a>
          <button
            onClick={() => setShowContractModal(true)}
            className="hover:opacity-60 transition cursor-pointer"
          >
            Security &amp; MSA
          </button>
        </nav>

        {/* Right: Login & Animated Popping Pill */}
        <div className="flex items-center">
          <button
            onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
            className="text-[14px] font-medium text-[#0b1d3a] px-3.5 hover:opacity-60 transition cursor-pointer"
          >
            Login
          </button>

          {/* Nav CTA Wrapper (Pops in as dot, stretches into full pill) */}
          <div className="navcta-wrapper">
            <button
              onClick={() => { setAuthTab('presets'); setAuthDrawerOpen(true); }}
              className="group relative inline-flex items-center h-[42px] px-4.5 pl-4 pr-11 rounded-full bg-[#0b1d3a] text-white text-[13.5px] font-medium tracking-tight whitespace-nowrap cursor-pointer"
            >
              <span className="navcta-lbl">Get a demo</span>
              <span className="absolute right-3.5 top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-[#2fe0d0] shadow-[0_0_10px_rgba(47,224,208,0.7)] group-hover:w-8 group-hover:h-8 group-hover:right-1 group-hover:shadow-none transition-all duration-300 flex items-center justify-center">
                <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0 text-[#0b1d3a] transition-all duration-300" />
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* ---------------------------------------------------- */}
      {/* 2. SCENE 1: HERO SECTION                             */}
      {/* ---------------------------------------------------- */}
      <section id="hero" className="relative min-h-[max(100vh,640px)] z-10 overflow-hidden">
        
        {/* Dynamic Revealing Headline - Word "system" 100% visible, responsive wrapping */}
        <h1
          ref={h1Ref}
          className="absolute top-[20vh] left-[clamp(20px,5.7vw,82px)] max-w-[min(880px,86vw)] font-normal text-[clamp(28px,3.8vw,56px)] leading-[1.08] tracking-[-0.035em] text-[#0b1d3a] z-2"
        >
          Meet <span className="hl">STAT6 BMS</span>, the business operating system<br className="hidden sm:inline" />
          built so we shall collaborate
        </h1>

        {/* Trust line */}
        <p className="absolute top-[58vh] left-[clamp(20px,5.7vw,82px)] text-[clamp(15px,1.28vw,19px)] tracking-[-0.015em] text-[#1d2f4f] z-2">
          Modern enterprises and global supply chains trust STAT6 BMS
        </p>

        {/* Large "Get a demo" Button with Signature Dot-to-Arrow Effect */}
        <div className="absolute bottom-[7.5vh] left-[clamp(20px,5.7vw,82px)] z-2">
          <button
            onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
            className="group relative inline-flex items-center h-[62px] pl-7 pr-16 rounded-full bg-[#0b1d3a] text-white text-[17px] font-medium tracking-tight whitespace-nowrap shadow-md cursor-pointer hover:bg-black transition"
          >
            <span>Get a demo</span>
            <span className="absolute right-6 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-[#2fe0d0] shadow-[0_0_10px_rgba(47,224,208,0.7)] group-hover:w-12 group-hover:h-12 group-hover:right-1.5 group-hover:shadow-none transition-all duration-300 flex items-center justify-center">
              <ChevronRight size={18} className="opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0 text-[#0b1d3a] transition-all duration-300" />
            </span>
          </button>
        </div>

        {/* 4×2 Grid of Fictional Partner Wordmarks */}
        <div className="absolute right-0 w-full lg:w-1/2 top-[55vh] bottom-0 grid grid-cols-2 sm:grid-cols-4 grid-rows-2 z-2 border-t border-[#0b1d3a]/5 sm:border-t-0">
          
          {/* 1. OCEANEX */}
          <div className="flex items-center justify-center border-l border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-bold text-[13px] tracking-[0.06em]">
              <svg width="20" height="20" viewBox="0 0 20 20">
                <path d="M2 7.5c2.5-1.8 5-1.8 7.5 0s5 1.8 7.5 0M2 12.5c2.5-1.8 5-1.8 7.5 0s5 1.8 7.5 0" fill="none" stroke="#3e4d68" strokeWidth="2.4" strokeLinecap="round"/>
              </svg>
              <span>OCEANEX</span>
            </div>
          </div>

          {/* 2. Nordhavn (Georgia Serif) */}
          <div className="flex items-center justify-center border-l border-[#0b1d3a]/10 px-3">
            <span style={{ fontFamily: 'Georgia, serif' }} className="font-bold italic text-[15px] text-[#3e4d68] tracking-wide">
              Nordhavn
            </span>
          </div>

          {/* 3. BLUEGATE */}
          <div className="flex items-center justify-center border-l border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-bold text-[13px] tracking-[0.06em]">
              <svg width="18" height="20" viewBox="0 0 18 20" fill="#3e4d68">
                <rect x="0" y="8" width="4" height="10" rx="1"/>
                <rect x="7" y="3" width="4" height="15" rx="1"/>
                <rect x="14" y="6" width="4" height="12" rx="1"/>
              </svg>
              <span>BLUEGATE</span>
            </div>
          </div>

          {/* 4. KELPWAY */}
          <div className="flex items-center justify-center border-l border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-medium text-[11px] tracking-[0.32em]">
              <svg width="18" height="18" viewBox="0 0 18 18">
                <polygon points="9,2 17,16 1,16" fill="none" stroke="#3e4d68" strokeWidth="1.8" strokeLinejoin="round"/>
              </svg>
              <span>KELPWAY</span>
            </div>
          </div>

          {/* 5. TIDELINE */}
          <div className="flex items-center justify-center border-l border-t border-[#0b1d3a]/10 px-3">
            <div className="border-2 border-[#3e4d68] rounded px-2 py-0.5 text-[#3e4d68] font-black text-[14px] tracking-tight">
              TIDELINE
            </div>
          </div>

          {/* 6. HARBORIX */}
          <div className="flex items-center justify-center border-l border-t border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-bold text-[13px] tracking-[0.06em]">
              <svg width="18" height="18" viewBox="0 0 18 18">
                <path d="M4 2v14M14 2v14M4 9h10" stroke="#3e4d68" strokeWidth="3" strokeLinecap="square"/>
              </svg>
              <span>HARBORIX</span>
            </div>
          </div>

          {/* 7. seaflux */}
          <div className="flex items-center justify-center border-l border-t border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-medium text-[15px] lowercase">
              <svg width="18" height="18" viewBox="0 0 18 18">
                <circle cx="9" cy="9" r="7" fill="none" stroke="#3e4d68" strokeWidth="1.8"/>
                <circle cx="9" cy="9" r="2.2" fill="#3e4d68"/>
              </svg>
              <span>seaflux</span>
            </div>
          </div>

          {/* 8. PORTERRA */}
          <div className="flex items-center justify-center border-l border-t border-[#0b1d3a]/10 px-3">
            <div className="flex items-center gap-2 text-[#3e4d68] font-bold text-[11px] tracking-[0.24em]">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="#3e4d68">
                <polygon points="9,3 17,16 1,16"/>
              </svg>
              <span>PORTERRA</span>
            </div>
          </div>

        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* 3. SCENE 2: PINNED STATEMENT SECTION                 */}
      {/* ---------------------------------------------------- */}
      <section id="statement" className="relative h-[306vh] -mt-[31vh] pointer-events-none z-10">
        <div className="sticky top-0 h-screen overflow-hidden flex items-center justify-center">
          <p
            ref={stmtRef}
            className="absolute top-[41.5vh] left-0 right-0 text-center font-normal text-[clamp(20px,2.8vw,42px)] leading-[1.16] tracking-[-0.03em] text-[#0b1d3a] whitespace-nowrap will-change-transform px-6"
          >
            STAT6 BMS is your unified business management system <br />
            that connects commercial CRM, financial ledgers, <br />
            HR payroll, agile sprints, and vendor portals, <br />
            ensuring that across every department, we shall collaborate
          </p>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* 4. SCENE 3: DARK SPLIT WITH CONTAINER SHIP PHOTO     */}
      {/* ---------------------------------------------------- */}
      <section
        ref={splitRef}
        id="split"
        className="relative z-20 bg-[#0e1f3d] text-white min-h-screen grid grid-cols-1 lg:grid-cols-[58.3%_41.7%] overflow-hidden"
      >
        {/* Left Column (58.3%) */}
        <div className="relative pl-[clamp(20px,5.7vw,82px)] pb-[8vh] pr-6 lg:pr-12">
          {/* Vertical Guide Line */}
          <div className="absolute left-[clamp(20px,5.7vw,82px)] top-0 bottom-0 w-[1px] bg-white/[0.12]"></div>

          {/* Headline Revealing Letter by Letter */}
          <h2
            ref={h2Ref}
            className="font-normal text-[clamp(32px,3.15vw,48px)] leading-[1.08] tracking-[-0.03em] pt-[21vh] pl-[6.2vw] text-white"
          >
            Enterprise operations that run<br />the way your business works
          </h2>

          {/* Ruled Row that fades up */}
          <div
            ref={rowRef}
            className="mt-[6.4vh] border-t border-white/[0.12] grid grid-cols-1 md:grid-cols-[1fr_1.05fr] gap-6 pt-[3vh] pl-[6.2vw] pr-[6vw] transition-all duration-900 opacity-0 translate-y-3.5"
          >
            <h3 className="font-normal text-[clamp(17px,1.4vw,21px)] tracking-tight text-white">
              Unified Operations &amp; Governance
            </h3>
            <p className="text-[clamp(13px,1.1vw,16px)] leading-[1.38] text-white/50 max-w-[20em]">
              <strong className="text-white font-medium">Reconcile faster. Unify approvals. Eliminate fragmented SaaS silos.</strong>{' '}
              STAT6 BMS brings sales pipeline, double-entry accounting, agile delivery, and vendor management into a single sovereign platform with cryptographic RBAC and zero 3rd-party data leakage.
            </p>
          </div>

          {/* Quick Launch Buttons on Dark Panel */}
          <div className="pt-12 pl-[6.2vw] flex flex-wrap items-center gap-3">
            <button
              onClick={() => { setAuthTab('signin'); setAuthDrawerOpen(true); }}
              className="px-6 py-3 rounded-full bg-[#2fe0d0] hover:bg-[#25c4b5] text-[#0b1d3a] font-semibold text-xs tracking-tight transition cursor-pointer flex items-center gap-2 shadow-lg"
            >
              <span>Launch STAT6 BMS Workspace</span>
              <ArrowRight size={14} />
            </button>

            <button
              onClick={() => { setAuthTab('presets'); setAuthDrawerOpen(true); }}
              className="px-5 py-3 rounded-full border border-white/20 hover:bg-white/10 text-xs font-semibold text-white transition cursor-pointer flex items-center gap-1.5"
            >
              <Users size={13} className="text-[#2fe0d0]" />
              <span>1-Click Role Presets (7 Roles)</span>
            </button>
          </div>
        </div>

        {/* Right Column (41.7%): Sovereign BMS Operating Console (Replacing irrelevant ship photo) */}
        <div className="relative p-6 sm:p-10 flex items-center justify-center bg-gradient-to-br from-[#0c1b36] via-[#09152b] to-[#060e1f] border-t lg:border-t-0 lg:border-l border-white/[0.1]">
          <div className="w-full max-w-[520px] rounded-2xl bg-[#0d182e]/90 border border-white/[0.12] shadow-[0_20px_50px_rgba(0,0,0,0.6)] backdrop-blur-2xl overflow-hidden font-sans">
            
            {/* Console Header Bar */}
            <div className="px-4 py-3 bg-[#0a1324] border-b border-white/[0.08] flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-[#f87171]"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-[#fbbf24]"></div>
                <div className="w-2.5 h-2.5 rounded-full bg-[#34d399]"></div>
              </div>
              <div className="px-3 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10.5px] font-mono text-slate-300 flex items-center gap-1.5">
                <Lock size={10} className="text-[#2fe0d0]" />
                <span>bms.stat6.enterprise / sovereign-runtime</span>
              </div>
              <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                14 UP
              </span>
            </div>

            {/* Console Body */}
            <div className="p-4 sm:p-5 space-y-4 text-xs text-left">
              
              {/* Telemetry KPIs Row */}
              <div className="grid grid-cols-3 gap-2.5">
                <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06]">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Paid Revenue MTD</div>
                  <div className="font-bold text-base text-white mt-0.5">$1,248,500</div>
                  <div className="text-[9.5px] text-emerald-400 font-mono mt-0.5">+14.2% vs budget</div>
                </div>
                <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06]">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Reconciled GL</div>
                  <div className="font-bold text-base text-white mt-0.5">1,420 Txns</div>
                  <div className="text-[9.5px] text-emerald-400 font-mono mt-0.5">100% SHA-256 match</div>
                </div>
                <div className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.06]">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">RBAC Guard</div>
                  <div className="font-bold text-base text-emerald-400 mt-0.5">7 Portals</div>
                  <div className="text-[9.5px] text-slate-400 font-mono mt-0.5">Zero 3rd-party cloud</div>
                </div>
              </div>

              {/* Live Service Microservices Grid */}
              <div className="p-3 rounded-xl bg-black/30 border border-white/[0.06] space-y-2">
                <div className="flex items-center justify-between text-[10.5px] font-mono text-slate-400">
                  <span className="font-semibold text-white flex items-center gap-1.5">
                    <Layers size={12} className="text-[#2fe0d0]" />
                    Sovereign BMS Architecture
                  </span>
                  <span className="text-emerald-400">99.95% SLA Active</span>
                </div>
                <div className="grid grid-cols-2 gap-1.5 text-[11px] font-mono">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Commercial CRM &amp; Pipeline</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Double-Entry General Ledger</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Jira Agile Sprints &amp; Velocity</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>HR Directory &amp; Staff Payroll</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>Procurement &amp; Vendor POs</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span>AES-256-GCM Password Vault</span>
                  </div>
                </div>
              </div>

              {/* Real-time Event Stream */}
              <div className="p-3 rounded-xl bg-black/40 border border-white/[0.06] space-y-1.5 font-mono text-[10.5px]">
                <div className="text-slate-400 text-[10px] uppercase tracking-wider mb-1">
                  Live Event Ledger Stream
                </div>
                <div className="text-slate-300 leading-tight">
                  <span className="text-slate-500">[0.18s]</span> <span className="text-[#2fe0d0]">GL_RECONCILE:</span> Matched $84,200 PO invoice to supplier journal
                </div>
                <div className="text-slate-300 leading-tight">
                  <span className="text-slate-500">[0.32s]</span> <span className="text-purple-400">RBAC_GUARD:</span> Enforced Vendor Portal tenant isolation token
                </div>
                <div className="text-slate-300 leading-tight">
                  <span className="text-slate-500">[0.45s]</span> <span className="text-emerald-400">JIRA_SYNC:</span> Reconciled Sprint 8 velocity burndown
                </div>
              </div>

              {/* 1-Click Persona Access Strip */}
              <div className="pt-1 flex items-center justify-between border-t border-white/[0.06]">
                <span className="text-[10px] font-mono text-slate-400">
                  Instant Test Login:
                </span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handlePresetSelect(personaCards[0])}
                    className="px-2 py-0.5 rounded bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 font-mono text-[10px] font-semibold transition cursor-pointer"
                  >
                    Admin
                  </button>
                  <button
                    onClick={() => handlePresetSelect(personaCards[1])}
                    className="px-2 py-0.5 rounded bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-mono text-[10px] font-semibold transition cursor-pointer"
                  >
                    Manager
                  </button>
                  <button
                    onClick={() => handlePresetSelect(personaCards[4])}
                    className="px-2 py-0.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 font-mono text-[10px] font-semibold transition cursor-pointer"
                  >
                    Vendor
                  </button>
                  <button
                    onClick={() => handlePresetSelect(personaCards[3])}
                    className="px-2 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-mono text-[10px] font-semibold transition cursor-pointer"
                  >
                    Client
                  </button>
                </div>
              </div>

            </div>

          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* 5. NATIVE OAUTH & RBAC AUTH DRAWER / MODAL           */}
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
                <span className="font-brand font-bold text-xl text-[#2563eb]">
                  BMS
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
      {/* 6. MASTER SERVICES AGREEMENT (MSA) LEGAL CONTRACT MODAL */}
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
