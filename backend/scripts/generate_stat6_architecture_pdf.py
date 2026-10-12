import os
import subprocess
import shutil

def generate_architecture_pdf_and_ui_assets():
    downloads_dir = os.path.expanduser(r"~\Downloads")
    if not os.path.exists(downloads_dir):
        downloads_dir = r"C:\Users\prann\Downloads"

    repo_stage_dir = r"C:\Users\prann\.gemini\antigravity\scratch\stat6-architecture-repo"
    os.makedirs(repo_stage_dir, exist_ok=True)
    ui_dir = os.path.join(repo_stage_dir, "ui-showcase")
    os.makedirs(ui_dir, exist_ok=True)

    output_pdf_downloads = os.path.join(downloads_dir, "STAT6_BMS_Architecture_and_UI.pdf")
    output_pdf_repo = os.path.join(repo_stage_dir, "STAT6_BMS_Architecture_and_UI.pdf")
    html_file = os.path.join(downloads_dir, "stat6_arch_master_temp.html")

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>STAT6 — Business Management System (BMS) | Product, Technical & UI Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4;
      margin: 11mm 12mm 12mm 12mm;
      @bottom-right {
        content: "STAT6 BMS Architecture v2.4  |  Page " counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 7.5pt;
        color: #64748b;
      }
    }

    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    body {
      font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #0f172a;
      background-color: #ffffff;
      line-height: 1.38;
      font-size: 8.3pt;
      margin: 0;
      padding: 0;
    }

    h1, h2, h3, h4 {
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #090d16;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-top: 0;
    }

    h2 {
      font-size: 11.8pt;
      border-bottom: 1.5px solid #e2e8f0;
      padding-bottom: 3px;
      margin-top: 10px;
      margin-bottom: 6px;
      color: #0f172a;
      display: flex;
      align-items: center;
      justify-content: space-between;
      page-break-after: avoid;
    }

    h2 .sec-tag {
      font-size: 7.2pt;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: #2563eb;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      padding: 2px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    h3 {
      font-size: 9.2pt;
      margin-top: 8px;
      margin-bottom: 4px;
      color: #1e3a8a;
      font-weight: 700;
      page-break-after: avoid;
    }

    p {
      margin-top: 0;
      margin-bottom: 5px;
      color: #1e293b;
    }

    ul {
      margin: 2px 0 4px 0;
      padding-left: 14px;
    }

    li {
      margin-bottom: 1.8px;
      color: #1e293b;
    }

    code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.3pt;
      background: #f1f5f9;
      padding: 0.5px 3.5px;
      border-radius: 3px;
      color: #0f172a;
      border: 1px solid #e2e8f0;
    }

    .page-break {
      page-break-before: always;
    }

    /* COVER HERO */
    .cover-hero {
      background: linear-gradient(135deg, #162340 0%, #0b1324 100%);
      color: #ffffff;
      padding: 18px 20px;
      border-radius: 10px;
      margin-bottom: 12px;
      border: 1px solid #1e293b;
      position: relative;
    }

    .cover-brand-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }

    .cover-logo-lockup {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .cover-logo-box {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      background: #2563eb;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 6px rgba(37,99,235,0.45);
    }

    .cover-logo-text {
      font-size: 16pt;
      font-weight: 800;
      letter-spacing: 0.06em;
      color: #ffffff;
    }

    .cover-pill {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.45);
      color: #34d399;
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.2pt;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 999px;
    }

    .cover-title {
      font-size: 18pt;
      font-weight: 800;
      color: #ffffff;
      margin: 0 0 4px 0;
      letter-spacing: -0.025em;
      line-height: 1.15;
    }

    .cover-subtitle {
      font-size: 9.2pt;
      color: #cbd5e1;
      margin: 0 0 12px 0;
      font-weight: 400;
    }

    .cover-spec-table {
      width: 100%;
      border-collapse: collapse;
      margin: 0;
      font-size: 7.6pt;
      background: rgba(15, 23, 42, 0.65);
      border-radius: 7px;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.12);
    }

    .cover-spec-table td {
      padding: 4.5px 9px;
      border: 1px solid rgba(255,255,255,0.1);
      color: #f8fafc;
      background: transparent !important;
    }

    .cover-spec-table td.spec-key {
      width: 24%;
      font-weight: 700;
      color: #93c5fd;
      text-transform: uppercase;
      font-size: 7pt;
      letter-spacing: 0.04em;
      background: rgba(37, 99, 235, 0.12) !important;
    }

    /* TABLES */
    table.arch-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 4px;
      margin-bottom: 8px;
      font-size: 7.6pt;
      page-break-inside: avoid;
    }

    table.arch-table th, table.arch-table td {
      padding: 4.5px 6.5px;
      text-align: left;
      border: 1px solid #cbd5e1;
      vertical-align: top;
    }

    table.arch-table th {
      background-color: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
      font-size: 7.1pt;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    table.arch-table td {
      color: #000000;
      font-weight: 400;
    }

    table.arch-table tr:nth-child(even) td {
      background-color: #f8fafc;
    }

    /* GRIDS & CARDS */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5.5px;
      margin-bottom: 6px;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 6px;
      margin-bottom: 6px;
    }

    .grid-4 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      margin-bottom: 6px;
    }

    .card {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 5px 8px;
      font-size: 7.25pt;
      line-height: 1.3;
      page-break-inside: avoid;
    }

    .card-header {
      font-size: 7.9pt;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 2px;
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 2px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .port-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 7pt;
      font-weight: 600;
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      padding: 1px 5px;
      border-radius: 4px;
    }

    .status-pass {
      font-family: 'JetBrains Mono', monospace;
      font-size: 7pt;
      font-weight: 700;
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      padding: 1px 5px;
      border-radius: 4px;
    }

    /* FLOW PIPELINE */
    .flow-chain {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 4px;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      padding: 8px 10px;
      border-radius: 8px;
      margin: 6px 0 10px 0;
      page-break-inside: avoid;
    }

    .flow-step {
      background: #162340;
      color: #ffffff;
      font-size: 7.3pt;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 5px;
      letter-spacing: 0.01em;
    }

    .flow-step.highlight {
      background: #2563eb;
    }

    .flow-arrow {
      color: #2563eb;
      font-weight: 800;
      font-size: 9pt;
    }

    /* UI MOCKUP FRAME */
    .ui-frame {
      border: 1.5px solid #94a3b8;
      border-radius: 10px;
      overflow: hidden;
      background: #f0f2f8;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
      margin-bottom: 12px;
      page-break-inside: avoid;
    }

    .ui-browser-bar {
      background: #0f172a;
      color: #cbd5e1;
      padding: 5px 12px;
      font-size: 7.2pt;
      font-family: 'JetBrains Mono', monospace;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #1e293b;
    }

    .ui-dots {
      display: flex;
      gap: 5px;
    }

    .ui-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .ui-app-shell {
      display: flex;
      min-height: 310px;
    }

    .ui-sidebar {
      width: 165px;
      background: #162340;
      color: #e2e8f0;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border-right: 1px solid #1e293b;
      flex-shrink: 0;
      font-size: 7.5pt;
    }

    .ui-sb-brand {
      padding: 8px 10px;
      border-bottom: 1px solid rgba(148,163,184,0.2);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .ui-sb-logo {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 700;
      font-size: 9.5pt;
      color: #ffffff;
      letter-spacing: 0.04em;
    }

    .ui-sb-logo-icon {
      width: 19px;
      height: 19px;
      border-radius: 5px;
      background: #2563eb;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 7pt;
      font-weight: 800;
    }

    .ui-sb-v {
      font-family: 'JetBrains Mono', monospace;
      font-size: 6.5pt;
      background: #1e293b;
      color: #cbd5e1;
      padding: 1px 4px;
      border-radius: 3px;
      border: 1px solid #334155;
    }

    .ui-sb-nav {
      padding: 6px 7px;
    }

    .ui-sb-item {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 3.5px 7px;
      border-radius: 5px;
      color: #cbd5e1;
      margin-bottom: 1.5px;
    }

    .ui-sb-item.active {
      background: #243964;
      color: #ffffff;
    }

    .ui-sb-dot {
      width: 7px;
      height: 7px;
      border-radius: 2px;
      flex-shrink: 0;
    }

    .ui-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #f0f2f8;
    }

    .ui-topbar {
      height: 28px;
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 7.5pt;
    }

    .ui-canvas {
      padding: 10px 12px;
      flex: 1;
    }

    .ui-table-card {
      background: #ffffff;
      border-radius: 10px;
      border: 1px solid #e2e8f0;
      overflow: hidden;
    }

    .ui-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 7.4pt;
    }

    .ui-table th {
      background: #ffffff;
      color: #000000;
      font-weight: 700;
      padding: 6px 8px;
      border-bottom: 1px solid #e2e8f0;
      border-right: 1px solid #e2e8f0;
      text-align: left;
    }

    .ui-table td {
      padding: 6px 8px;
      border-bottom: 1px solid #f1f5f9;
      color: #000000;
      font-weight: 400;
      background: #ffffff !important;
    }

    .ui-avatar {
      display: inline-flex;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      align-items: center;
      justify-content: center;
      font-size: 6.5pt;
      font-weight: 700;
      color: #ffffff;
      margin-right: 6px;
      vertical-align: middle;
    }

    /* MINDMAP TREE */
    .mindmap-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      page-break-inside: avoid;
    }

    .mm-branch {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      background: #f8fafc;
      padding: 7px 9px;
      page-break-inside: avoid;
    }

    .mm-title {
      font-weight: 800;
      font-size: 8pt;
      color: #162340;
      border-bottom: 1.5px solid #2563eb;
      padding-bottom: 2px;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .mm-list {
      list-style: none;
      margin: 0;
      padding: 0;
      font-size: 7.4pt;
    }

    .mm-list li {
      position: relative;
      padding-left: 11px;
      margin-bottom: 2px;
      color: #0f172a;
    }

    .mm-list li::before {
      content: "├─";
      position: absolute;
      left: 0;
      color: #2563eb;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
    }

    .mm-list li:last-child::before {
      content: "└─";
    }
  </style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PAGE 1: COVER, EXECUTIVE SUMMARY & END-TO-END BUSINESS GRAPH          -->
  <!-- ===================================================================== -->
  <div class="cover-hero">
    <div class="cover-brand-row">
      <div class="cover-logo-lockup">
        <div class="cover-logo-box">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
          </svg>
        </div>
        <span class="cover-logo-text">STAT6</span>
      </div>
      <span class="cover-pill">PRODUCTION VERIFIED • v2.4 ENTERPRISE</span>
    </div>
    <div class="cover-title">STAT6 — BUSINESS MANAGEMENT SYSTEM (BMS)</div>
    <div class="cover-subtitle">Complete Product, Distributed Microservices, Cloud Database &amp; Visual UI Architecture Specification</div>

    <table class="cover-spec-table">
      <tr>
        <td class="spec-key">System Type</td>
        <td>All-in-One Enterprise Business Management System &amp; Autonomous Business Operating System</td>
      </tr>
      <tr>
        <td class="spec-key">Architecture Pattern</td>
        <td>14 Autonomous FastAPI Microservices (Ports <code>8000</code>–<code>8013</code>) + Central API Gateway + Async Webhook Event Bus</td>
      </tr>
      <tr>
        <td class="spec-key">Data Persistence</td>
        <td>Supabase Cloud PostgreSQL 17.6 (EU-Central-1 Supavisor Pooler <code>:6543</code>) — 52 Relational Tenant-Isolated Tables</td>
      </tr>
      <tr>
        <td class="spec-key">Frontend Engine</td>
        <td>React 18.3 + TypeScript + Vite 6 + Tailwind CSS  |  <em>Plus Jakarta Sans</em> &amp; <em>Inter</em>  |  Zero-Emoji Vector Design</td>
      </tr>
      <tr>
        <td class="spec-key">Core Principle</td>
        <td><strong>One Unified Business Graph. Zero Silos. Zero Sync Latency. Total Enterprise Control.</strong></td>
      </tr>
    </table>
  </div>

  <h2>1. Executive Summary &amp; Unified Business Operating Layer <span class="sec-tag">Section 01</span></h2>
  <p>
    <strong>STAT6</strong> is an enterprise-grade Business Management System engineered to unify every critical commercial, operational, financial, workforce, and governance function into a single high-throughput platform. Rather than stitching together disconnected SaaS tools for CRM, sales, marketing, agile projects, HR/payroll, double-entry finance, warehouse inventory, procurement, customer support, team chat, compliance, and AI, STAT6 operates on a <strong>single shared multi-tenant business graph</strong> backed by 14 specialized microservices.
  </p>
  <p>
    Every action in STAT6 propagates instantaneously across domain boundaries via the <strong>Central Event Relay Bus</strong>:
  </p>

  <div class="flow-chain">
    <span class="flow-step">01. Marketing Campaign</span><span class="flow-arrow">→</span>
    <span class="flow-step">02. Lead Capture</span><span class="flow-arrow">→</span>
    <span class="flow-step">03. Qualification</span><span class="flow-arrow">→</span>
    <span class="flow-step">04. Deal Pipeline</span><span class="flow-arrow">→</span>
    <span class="flow-step">05. Quote / Proposal</span><span class="flow-arrow">→</span>
    <span class="flow-step highlight">06. Deal Won (Event)</span><span class="flow-arrow">→</span>
    <span class="flow-step">07. Agile Project &amp; Tasks</span><span class="flow-arrow">→</span>
    <span class="flow-step">08. Net30 Invoice &amp; Ledger</span><span class="flow-arrow">→</span>
    <span class="flow-step">09. Payment Settlement</span><span class="flow-arrow">→</span>
    <span class="flow-step">10. SLA Support Desk</span><span class="flow-arrow">→</span>
    <span class="flow-step highlight">11. BI Telemetry &amp; AI Copilot</span>
  </div>

  <h2>2. Core System Architecture Topology <span class="sec-tag">Section 02</span></h2>
  <p>
    Unlike legacy architectures that start as a monolithic bottleneck, STAT6 implements a production-verified <strong>3-Pillar Distributed Microservices Mesh</strong> fronted by a single API Gateway (`:8000`) and backed by a unified PostgreSQL 17.6 cloud cluster:
  </p>

  <!-- VECTOR SVG SYSTEM TOPOLOGY DIAGRAM -->
  <div style="border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; background: #f8fafc; margin-bottom: 8px; page-break-inside: avoid;">
    <svg width="100%" height="230" viewBox="0 0 860 230" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Plus Jakarta Sans', sans-serif;">
      <!-- Client Layer -->
      <rect x="250" y="6" width="360" height="28" rx="6" fill="#162340" />
      <text x="430" y="24" fill="#ffffff" font-size="10" font-weight="700" text-anchor="middle">STAT6 WEB APP (React 18 + Vite)  |  PUBLIC REST API  |  MOBILE</text>
      <line x1="430" y1="34" x2="430" y2="48" stroke="#2563eb" stroke-width="2" />

      <!-- Gateway Layer -->
      <rect x="140" y="48" width="580" height="32" rx="6" fill="#2563eb" />
      <text x="430" y="68" fill="#ffffff" font-size="10.5" font-weight="800" text-anchor="middle">CENTRAL API GATEWAY (:8000) — Auth Guard • Tenant RLS • Distributed Omnisearch (&lt;15ms)</text>

      <!-- Pillar Connectors -->
      <line x1="150" y1="80" x2="150" y2="96" stroke="#64748b" stroke-width="1.5" />
      <line x1="430" y1="80" x2="430" y2="96" stroke="#64748b" stroke-width="1.5" />
      <line x1="710" y1="80" x2="710" y2="96" stroke="#64748b" stroke-width="1.5" />
      <line x1="150" y1="88" x2="710" y2="88" stroke="#64748b" stroke-width="1.5" />

      <!-- Pillar 1 -->
      <rect x="12" y="96" width="270" height="68" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" />
      <rect x="12" y="96" width="270" height="18" rx="5" fill="#e11d48" />
      <text x="147" y="108" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">PILLAR 1: COMMERCIAL ENGINE</text>
      <text x="22" y="126" fill="#0f172a" font-size="8.2" font-weight="600">• Auth &amp; RBAC (:8001)     • CRM &amp; Sales (:8002)</text>
      <text x="22" y="142" fill="#0f172a" font-size="8.2" font-weight="600">• Marketing ROI (:8003)   • Jira Projects (:8004)</text>
      <text x="22" y="156" fill="#475569" font-size="7.5">Leads, Deals, Quotes, Campaigns, Sprints, Tasks</text>

      <!-- Pillar 2 -->
      <rect x="295" y="96" width="270" height="68" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" />
      <rect x="295" y="96" width="270" height="18" rx="5" fill="#0284c7" />
      <text x="430" y="108" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">PILLAR 2: OPERATIONS &amp; SUPPLY CHAIN</text>
      <text x="305" y="126" fill="#0f172a" font-size="8.2" font-weight="600">• HR &amp; Payroll (:8005)    • Finance Ledger (:8006)</text>
      <text x="305" y="142" fill="#0f172a" font-size="8.2" font-weight="600">• Inventory (:8007)       • Procurement (:8008) • Support (:8009)</text>
      <text x="305" y="156" fill="#475569" font-size="7.5">Double-Entry GL, Net30, SKUs, 3-Way PO Match, SLAs</text>

      <!-- Pillar 3 -->
      <rect x="578" y="96" width="270" height="68" rx="6" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5" />
      <rect x="578" y="96" width="270" height="18" rx="5" fill="#7c3aed" />
      <text x="713" y="108" fill="#ffffff" font-size="8.5" font-weight="700" text-anchor="middle">PILLAR 3: INTELLIGENCE &amp; GOVERNANCE</text>
      <text x="588" y="126" fill="#0f172a" font-size="8.2" font-weight="600">• Collaboration (:8010)   • Compliance (:8011)</text>
      <text x="588" y="142" fill="#0f172a" font-size="8.2" font-weight="600">• WHEN-IF-DO (:8012)      • AI Copilot (:8013)</text>
      <text x="588" y="156" fill="#475569" font-size="7.5">Team Chat, SHA-256 Audit, SOC2/GDPR, NLP Synthesis</text>

      <!-- Event Bus & Cloud DB -->
      <line x1="150" y1="164" x2="150" y2="182" stroke="#64748b" stroke-width="1.5" />
      <line x1="430" y1="164" x2="430" y2="182" stroke="#64748b" stroke-width="1.5" />
      <line x1="710" y1="164" x2="710" y2="182" stroke="#64748b" stroke-width="1.5" />

      <rect x="12" y="182" width="405" height="40" rx="6" fill="#0f172a" />
      <text x="214" y="199" fill="#34d399" font-size="9" font-weight="700" text-anchor="middle">SUPABASE CLOUD POSTGRESQL 17.6 (EU Pooler :6543)</text>
      <text x="214" y="213" fill="#cbd5e1" font-size="7.8" text-anchor="middle">52 Domain-Prefixed Relational Tables • Single-Tenant org_id Isolation</text>

      <rect x="443" y="182" width="405" height="40" rx="6" fill="#1e293b" />
      <text x="645" y="199" fill="#fb923c" font-size="9" font-weight="700" text-anchor="middle">ASYNC WEBHOOK EVENT BUS &amp; WHEN-IF-DO ENGINE</text>
      <text x="645" y="213" fill="#cbd5e1" font-size="7.8" text-anchor="middle">deal.won • lead.captured • stock.low • invoice.paid • ticket.urgent</text>
    </svg>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 2: HOW THE STAT6 UI LOOKS (LIVE VISUAL INTERFACE SHOWCASE)       -->
  <!-- ===================================================================== -->
  <div class="page-break"></div>

  <h2>3. How the STAT6 UI Looks — Visual Interface Architecture <span class="sec-tag">Section 03 • UI Showcase</span></h2>
  <p>
    The STAT6 user interface is engineered for executive clarity and high information density. It strictly enforces <strong>Plus Jakarta Sans</strong> for bold headings, <strong>Inter</strong> for regular-weight solid black (<code>#000000</code>) data cells, <strong>zero emojis</strong> (100% crisp SVG vector outline icons), and vertical column header dividers (<code>border-r border-slate-200</code>).
  </p>

  <h3>3.1 Live UI Screen 1: Sales &amp; CRM — Leads Management Workspace</h3>
  <div class="ui-frame">
    <div class="ui-browser-bar">
      <div class="ui-dots">
        <div class="ui-dot" style="background:#ef4444;"></div>
        <div class="ui-dot" style="background:#f59e0b;"></div>
        <div class="ui-dot" style="background:#10b981;"></div>
      </div>
      <span>https://stat6.app/workspace/leads  —  STAT6 | Enterprise Management Platform</span>
      <span style="color:#34d399;">● Supabase Live</span>
    </div>
    <div class="ui-app-shell">
      <!-- Sidebar -->
      <div class="ui-sidebar">
        <div>
          <div class="ui-sb-brand">
            <div class="ui-sb-logo">
              <div class="ui-sb-logo-icon">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
              </div>
              <span>STAT6</span>
            </div>
            <span class="ui-sb-v">v2.4</span>
          </div>
          <div class="ui-sb-nav">
            <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#38bdf8;"></span>Home</div>
            <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#f43f5e;"></span>Reports</div>
            <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#c084fc;"></span>Analytics</div>
            <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#34d399;"></span>My Requests</div>
            <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#fb923c;"></span>Agents</div>
            <div style="border-top:1px solid rgba(148,163,184,0.2); margin:5px 2px;"></div>
            <div style="display:flex; align-items:center; justify-content:space-between; padding:3px 5px; color:#fff; font-weight:600;">
              <span style="display:flex; align-items:center; gap:5px;">
                <span style="background:#e11d48; color:#fff; width:14px; height:14px; border-radius:3px; display:inline-flex; align-items:center; justify-content:center; font-size:6.5pt; font-weight:800;">S</span>
                Sales ▾
              </span>
              <span style="color:#94a3b8;">•••</span>
            </div>
            <div style="background:#1c2d52; border:1px solid #334155; border-radius:5px; padding:3px 7px; margin:4px 2px 6px 2px; color:#94a3b8; font-size:7pt;">
              ⌕ Search
            </div>
            <div style="padding:2px 5px; color:#e2e8f0; font-weight:600; display:flex; justify-content:space-between;">
              <span>Sales Workspace</span><span>^</span>
            </div>
            <div style="padding-left:6px; margin-top:2px;">
              <div class="ui-sb-item active"><span class="ui-sb-dot" style="background:#60a5fa; border-radius:50%;"></span>Leads</div>
              <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#94a3b8; border-radius:50%;"></span>Contacts</div>
              <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#94a3b8;"></span>Deals Pipeline</div>
            </div>
            <div style="border-top:1px solid rgba(148,163,184,0.2); margin:5px 2px;"></div>
            <div style="padding:2px 5px; color:#e2e8f0; font-weight:600; display:flex; justify-content:space-between;">
              <span>Operations</span><span>^</span>
            </div>
            <div style="padding-left:6px;">
              <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#38bdf8;"></span>Jira Agile Sprints</div>
              <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#c084fc;"></span>Finance &amp; Invoices</div>
              <div class="ui-sb-item"><span class="ui-sb-dot" style="background:#fb923c;"></span>Inventory &amp; SKUs</div>
            </div>
          </div>
        </div>
        <div style="padding:6px 10px; border-top:1px solid rgba(148,163,184,0.2); display:flex; justify-content:space-between; font-size:6.5pt;">
          <span style="color:#34d399; font-family:'JetBrains Mono',monospace;">● Supabase Live</span>
          <span style="color:#fff;">Dark</span>
        </div>
      </div>

      <!-- Main Workspace -->
      <div class="ui-main">
        <div class="ui-topbar">
          <div><strong style="color:#000;">STAT6</strong> <span style="color:#94a3b8;">/</span> <span style="color:#000;">LEADS</span></div>
          <div style="display:flex; gap:6px;">
            <span style="border:1px solid #cbd5e1; border-radius:5px; padding:2px 7px; font-size:7pt;">Search anything... <code style="font-size:6.5pt;">Ctrl+K</code></span>
            <span style="border:1px solid #cbd5e1; border-radius:5px; padding:2px 7px; font-size:7pt;">Refresh</span>
          </div>
        </div>
        <div class="ui-canvas">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:13pt; font-weight:800; color:#000; letter-spacing:-0.02em;">Leads</span>
            <span style="background:#2563eb; color:#fff; padding:4px 10px; border-radius:6px; font-size:7.2pt;">+ Add Lead</span>
          </div>
          <div class="ui-table-card">
            <table class="ui-table">
              <thead>
                <tr>
                  <th>Lead Name &nbsp;<span style="font-weight:400;">All ▾</span></th>
                  <th>Company</th>
                  <th>Lead Source</th>
                  <th>Email</th>
                  <th style="border-right:none;">Lead Owner</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><span class="ui-avatar" style="background:#0284c7;">GH</span>Greg Howard</td>
                  <td>Howard Techno</td>
                  <td>Trade Show</td>
                  <td>greg@howard.com</td>
                  <td><span class="ui-avatar" style="background:#0f766e;">BR</span>Bob Ross</td>
                </tr>
                <tr>
                  <td><span class="ui-avatar" style="background:#4f46e5;">RG</span>Robert Green</td>
                  <td>Hitech Solution</td>
                  <td>Cold Call</td>
                  <td>green.robert@hitech.com</td>
                  <td><span class="ui-avatar" style="background:#b45309;">TR</span>Tim Roberts</td>
                </tr>
                <tr>
                  <td><span class="ui-avatar" style="background:#e11d48;">KM</span>Kris Marrier</td>
                  <td>Brown Horizon LLC</td>
                  <td>Advertisement</td>
                  <td>kris@brownhorizon.com</td>
                  <td><span class="ui-avatar" style="background:#334155;">RM</span>Richard Mc</td>
                </tr>
                <tr>
                  <td><span class="ui-avatar" style="background:#7c3aed;">AB</span>Amelia Burrows</td>
                  <td>GemStone Tech</td>
                  <td>Webinar</td>
                  <td>b.amelia@zylker.com</td>
                  <td><span class="ui-avatar" style="background:#0f766e;">BR</span>Bob Ross</td>
                </tr>
                <tr>
                  <td><span class="ui-avatar" style="background:#059669;">KD</span>Krishna Das</td>
                  <td>Zylker Logistics</td>
                  <td>Email Campaign</td>
                  <td>krishna.das@zylker.com</td>
                  <td><span class="ui-avatar" style="background:#334155;">RM</span>Richard Mc</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <h3>3.2 Live UI Screen 2: Agile Sprint 44 Kanban Board, Slide-Over Inspector &amp; Executive Telemetry</h3>
  <div class="grid-2">
    <!-- Kanban & Inspector Mockup -->
    <div class="ui-frame" style="margin-bottom:0;">
      <div class="ui-browser-bar">
        <span>STAT6 / PROJECTS — Sprint 44 Agile Kanban</span>
        <span style="color:#60a5fa;">FIN-51 Selected</span>
      </div>
      <div style="padding:9px; background:#f0f2f8;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <strong style="font-size:9.5pt; color:#000;">Sprint 44 Execution Board</strong>
          <span style="font-size:6.8pt; background:#fff; border:1px solid #cbd5e1; padding:2px 6px; border-radius:4px;">Connected Workspaces</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:6px; font-size:7pt;">
          <div style="background:#fff; border:1px solid #e2e8f0; border-radius:7px; padding:6px;">
            <div style="font-weight:700; border-bottom:1px solid #e2e8f0; padding-bottom:3px; margin-bottom:5px;">Blocked</div>
            <div style="border:1px solid #cbd5e1; border-radius:5px; padding:5px; background:#fafbfc;">
              <div>Automate Stripe webhook retry</div>
              <div style="display:flex; justify-content:space-between; margin-top:4px; font-family:'JetBrains Mono',monospace; font-size:6.5pt;">
                <span style="color:#0052cc; font-weight:700;">[TASK] FIN-50</span><span>5 pts</span>
              </div>
            </div>
          </div>
          <div style="background:#fff; border:1px solid #2563eb; border-radius:7px; padding:6px;">
            <div style="font-weight:700; border-bottom:1px solid #e2e8f0; padding-bottom:3px; margin-bottom:5px;">In progress</div>
            <div style="border:1px solid #93c5fd; border-radius:5px; padding:5px; background:#eff6ff;">
              <div>Multi-tenant ledger sync</div>
              <div style="display:flex; justify-content:space-between; margin-top:4px; font-family:'JetBrains Mono',monospace; font-size:6.5pt;">
                <span style="color:#00875a; font-weight:700;">[STORY] FIN-51</span><span>8 pts</span>
              </div>
            </div>
          </div>
          <div style="background:#fff; border:1px solid #e2e8f0; border-radius:7px; padding:6px;">
            <div style="font-weight:700; border-bottom:1px solid #e2e8f0; padding-bottom:3px; margin-bottom:5px;">Ready / Done</div>
            <div style="border:1px solid #cbd5e1; border-radius:5px; padding:5px; background:#fafbfc;">
              <div>Enterprise typography system</div>
              <div style="display:flex; justify-content:space-between; margin-top:4px; font-family:'JetBrains Mono',monospace; font-size:6.5pt;">
                <span style="color:#7c3aed; font-weight:700;">[EPIC] FIN-52</span><span>3 pts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Executive Telemetry & AI Copilot Mockup -->
    <div class="ui-frame" style="margin-bottom:0;">
      <div class="ui-browser-bar">
        <span>STAT6 / OVERVIEW &amp; AI COPILOT</span>
        <span style="color:#34d399;">Real-Time BI</span>
      </div>
      <div style="padding:9px; background:#f0f2f8;">
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:6px; margin-bottom:6px; font-size:7pt;">
          <div style="background:#fff; border:1px solid #e2e8f0; border-radius:6px; padding:6px;">
            <div>Paid Revenue</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:10pt; margin-top:2px;">$450,000</div>
            <div style="color:#047857; font-size:6.5pt;">+24.8% vs prior mo</div>
          </div>
          <div style="background:#fff; border:1px solid #e2e8f0; border-radius:6px; padding:6px;">
            <div>Deal Pipeline</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:10pt; margin-top:2px;">$825,000</div>
            <div style="font-size:6.5pt;">6 active contracts</div>
          </div>
          <div style="background:#fff; border:1px solid #e2e8f0; border-radius:6px; padding:6px;">
            <div>SLA Compliance</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:10pt; margin-top:2px;">100.0%</div>
            <div style="font-size:6.5pt;">Avg 14m response</div>
          </div>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:6px; padding:6px; font-size:7pt;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
            <strong>AI Copilot Synthesis: Overdue Invoice INV-2024-002</strong>
            <span style="background:#dbeafe; color:#1e40af; padding:1px 5px; border-radius:3px; font-size:6.3pt;">WHEN-IF-DO Ready</span>
          </div>
          <div style="color:#000; font-size:6.8pt; line-height:1.35;">
            Correlated Net30 invoice ($27,500) with Sprint Task FIN-51 milestone sign-off. Recommended action: Trigger Dunning Sequence #2 upon GitHub PR #88 merge.
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 3: COMPLETE 14-MICROSERVICE & 19-DOMAIN FUNCTIONAL ARCHITECTURE  -->
  <!-- ===================================================================== -->
  <div class="page-break"></div>

  <h2>4. Complete Functional &amp; Microservice Domain Architecture <span class="sec-tag">Sections 04–19</span></h2>
  <p>
    STAT6 implements all 19 enterprise functional domains across 14 autonomous microservices, eliminating external integration tax while maintaining strict service boundaries:
  </p>

  <div class="grid-2">
    <div class="card">
      <div class="card-header"><span>01. Identity, Auth &amp; Multi-Tenant Organization</span><span class="port-badge">auth-service :8001</span></div>
      <ul>
        <li><strong>Authentication</strong>: Email/password, OAuth2/OIDC (Google/Microsoft), JWT issuance &amp; cryptographic token renewal, MFA/OTP readiness, and session revocation.</li>
        <li><strong>Authorization (RBAC)</strong>: Granular permissions (<code>create</code>, <code>read</code>, <code>update</code>, <code>delete</code>, <code>export</code>, <code>approve</code>, <code>assign</code>) scoped at organization, department, team, and record levels.</li>
        <li><strong>Multi-Tenancy</strong>: Every record carries <code>org_id</code>; users can belong to multiple isolated organizations with zero cross-tenant data leakage.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>02. CRM, Sales Pipeline &amp; Quotations</span><span class="port-badge">crm-service :8002</span></div>
      <ul>
        <li><strong>Lead Lifecycle</strong>: Capture, source attribution, automated scoring (0–100), qualification, and atomic 1-click conversion into Contact + Account + Deal.</li>
        <li><strong>Deal Pipeline</strong>: <code>New → Contacted → Qualified → Proposal → Negotiation → Won/Lost</code> with weighted probability revenue forecasting.</li>
        <li><strong>Quotes &amp; Proposals</strong>: Line-item pricing, discount/tax calculation, digital acceptance, and automatic <code>deal.won</code> event emission.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>03. Marketing Campaigns &amp; Attribution</span><span class="port-badge">marketing-service :8003</span></div>
      <ul>
        <li><strong>Omni-Channel Campaigns</strong>: Email, SMS, WhatsApp, Webinar, and Paid Social campaign orchestration with audience segmentation.</li>
        <li><strong>Inbound Capture &amp; UTM</strong>: Embeddable lead capture webhooks (emitting <code>lead.captured</code> to CRM) with full UTM parameter tracking.</li>
        <li><strong>ROI Analytics</strong>: Real-time tracking of budget vs. actual spend, leads generated, CAC, and blended conversion ROI.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>04. Projects, Agile Sprints &amp; Operations</span><span class="port-badge">projects-service :8004</span></div>
      <ul>
        <li><strong>Agile &amp; Waterfall Views</strong>: Interactive Kanban board, Sprint backlog, list view, timeline/Gantt milestones, and project budget burn tracking.</li>
        <li><strong>Task Execution</strong>: Assignments, priorities, story points, dependencies, subtasks, checklists, time worklogs, and billable expense linkage.</li>
        <li><strong>Dev &amp; Design Links</strong>: Native linkage to GitHub PRs, Figma frames, and Honeycomb telemetry traces.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>05. HR, People &amp; Payroll Engine</span><span class="port-badge">hr-service :8005</span></div>
      <ul>
        <li><strong>Workforce Directory &amp; ATS</strong>: Employee profiles, departments, reporting hierarchy, salary structures, and recruitment pipeline (<code>Applied → Screening → Interview → Offer → Hired</code>).</li>
        <li><strong>Time &amp; Performance</strong>: Daily attendance clock-in/out, leave approval workflows, OKRs, and performance reviews.</li>
        <li><strong>Payroll Automation</strong>: Monthly gross-to-net payroll calculation, tax deductions, and <code>payroll.executed</code> ledger sync.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>06. Finance &amp; Double-Entry Accounting</span><span class="port-badge">finance-service :8006</span></div>
      <ul>
        <li><strong>Invoicing &amp; Receivables</strong>: Recurring &amp; Net30 invoices, tax/discount rules, payment links, and automated overdue dunning reminders.</li>
        <li><strong>Double-Entry General Ledger</strong>: Strict GAAP-compliant journal entries and lines enforcing <code>SUM(debit) == SUM(credit)</code> on every transaction.</li>
        <li><strong>Financial Statements</strong>: Real-time Profit &amp; Loss (P&amp;L), Balance Sheet, Cash Flow forecasting, and department budget tracking.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>07. Inventory, Warehouses &amp; Assets</span><span class="port-badge">inventory-service :8007</span></div>
      <ul>
        <li><strong>Multi-Warehouse Stock</strong>: SKU catalog, warehouse locations, stock movements, adjustments, and safety threshold monitoring.</li>
        <li><strong>Low-Stock Sentinel</strong>: Emits <code>stock.low</code> events automatically when SKU quantity drops below reorder threshold.</li>
        <li><strong>Enterprise Asset Lifecycle</strong>: Tracks laptops, vehicles, licenses, and hardware across <code>Purchased → Assigned → In Use → Maintenance → Retired</code>.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>08. Procurement, Vendors &amp; 3-Way Match</span><span class="port-badge">procurement-service :8008</span></div>
      <ul>
        <li><strong>Vendor Management</strong>: Vendor directory, SLA performance ratings, price catalogs, contracts, and payment terms.</li>
        <li><strong>Purchase Lifecycle</strong>: Requisitions, RFQs, automated Purchase Order (PO) drafting from low-stock triggers, and multi-tier approvals.</li>
        <li><strong>Automated 3-Way Matching</strong>: Validates <code>Purchase Order ↔ Goods Received Note (GRN) ↔ Vendor Invoice</code> prior to payment release.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>09. Customer Support &amp; SLA Triage Desk</span><span class="port-badge">support-service :8009</span></div>
      <ul>
        <li><strong>Ticket Lifecycle</strong>: <code>Created → Assigned → Investigation → Resolution → Closed</code> linked directly to CRM customer accounts.</li>
        <li><strong>Dynamic SLA Timers</strong>: Real-time response and resolution countdown clocks with automated breach detection.</li>
        <li><strong>Auto-Escalation</strong>: Emits <code>ticket.urgent</code> events to notify engineering/account owners on high-priority issues.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>10. Communication &amp; Team Collaboration</span><span class="port-badge">collaboration-service :8010</span></div>
      <ul>
        <li><strong>Real-Time Channels</strong>: Topic-based channels (<code>#general</code>, <code>#engineering</code>, <code>#deals</code>), direct messaging, threads, and <code>@mentions</code>.</li>
        <li><strong>Contextual Collaboration</strong>: Record-level comments, shared team calendars, file attachments, and automated system event broadcasts.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>11. Compliance, Documents &amp; Audit Trail</span><span class="port-badge">compliance-service :8011</span></div>
      <ul>
        <li><strong>Document Cloud</strong>: Versioned repository for contracts, proposals, invoices, employee files, and corporate policies with RBAC sharing.</li>
        <li><strong>Cryptographic Audit Log</strong>: Immutable SHA-256 hash-chained ledger recording actor, action, resource, timestamp, and before/after diffs.</li>
        <li><strong>Regulatory Readiness</strong>: SOC 2 Type II control monitoring and automated GDPR Data Subject Access Request (DSAR) exports.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-header"><span>12. Workflow Automation &amp; AI Copilot</span><span class="port-badge">:8012 &amp; :8013</span></div>
      <ul>
        <li><strong>WHEN-IF-DO Engine (:8012)</strong>: Declarative event-driven rule evaluator executing cross-service webhooks, task creation, and notifications.</li>
        <li><strong>Autonomous AI Copilot (:8013)</strong>: Permission-checked natural-language assistant synthesizing CRM, Finance, Jira, and Inventory telemetry with anomaly detection and revenue forecasting.</li>
      </ul>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 4: TECH STACK, 52-TABLE SUPABASE DB, SECURITY & VERIFICATION     -->
  <!-- ===================================================================== -->
  <div class="page-break"></div>

  <h2>5. Technology Stack &amp; Cloud Database Architecture <span class="sec-tag">Sections 20–25</span></h2>

  <table class="arch-table">
    <thead>
      <tr>
        <th style="width: 20%;">Architectural Layer</th>
        <th style="width: 35%;">STAT6 Production Technology</th>
        <th style="width: 45%;">Engineering Rationale &amp; Capabilities</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Frontend SPA</strong></td>
        <td>React 18.3 + TypeScript 5.5 + Vite 6 + Tailwind CSS 3.4</td>
        <td>Sub-second HMR, 2.37s production build, <em>Plus Jakarta Sans</em> + <em>Inter</em>, Lucide vector icons, zero emojis.</td>
      </tr>
      <tr>
        <td><strong>Backend Services</strong></td>
        <td>Python 3.10+ • FastAPI • Pydantic v2 • SQLAlchemy 2.0</td>
        <td>14 independent async-ready microservices with automatic OpenAPI/Swagger specs and strict schema validation.</td>
      </tr>
      <tr>
        <td><strong>Cloud Database</strong></td>
        <td>Supabase Cloud PostgreSQL 17.6 (Supavisor Pooler <code>:6543</code>)</td>
        <td>52 relational tables, ACID transactions, foreign key integrity, IPv4 connection pooling in AWS <code>eu-central-1</code>.</td>
      </tr>
      <tr>
        <td><strong>Event &amp; Queue Layer</strong></td>
        <td>Central API Gateway Event Relay + Idempotent Webhook Bus</td>
        <td>Decoupled pub/sub event fan-out with delivery logging, retry backoff, and declarative <code>WHEN-IF-DO</code> evaluation.</td>
      </tr>
      <tr>
        <td><strong>Security &amp; Auth</strong></td>
        <td>HMAC-SHA256 JWT + Supabase JWKS + SHA-256 Hash Chain</td>
        <td>Stateless token verification, 4-persona RBAC, <code>org_id</code> tenant isolation, and tamper-evident audit trails.</td>
      </tr>
      <tr>
        <td><strong>CI/CD &amp; Hosting</strong></td>
        <td>Vercel Edge CDN (Frontend) + Containerized Service Fleet</td>
        <td>Zero-config <code>vercel.json</code> SPA routing rewrites, global edge caching, and environment-driven API gateway binding.</td>
      </tr>
    </tbody>
  </table>

  <h3>5.1 Complete 52-Table Cloud PostgreSQL Schema Inventory (Supabase Production)</h3>
  <p>
    Every tenant-owned table enforces <code>org_id</code> partitioning and is live-provisioned in Supabase PostgreSQL:
  </p>
  <div class="grid-4" style="font-size: 7.2pt;">
    <div class="card" style="padding:5px 7px;">
      <strong>Auth &amp; Gateway (7)</strong><br>
      <code>auth_organizations</code> • <code>auth_users</code> • <code>auth_roles</code> • <code>auth_permissions</code> • <code>auth_sessions</code> • <code>gateway_events</code> • <code>gateway_routes</code>
    </div>
    <div class="card" style="padding:5px 7px;">
      <strong>CRM &amp; Marketing (9)</strong><br>
      <code>crm_leads</code> • <code>crm_contacts</code> • <code>crm_companies</code> • <code>crm_deals</code> • <code>crm_quotes</code> • <code>crm_activities</code> • <code>mkt_campaigns</code> • <code>mkt_forms</code> • <code>mkt_utms</code>
    </div>
    <div class="card" style="padding:5px 7px;">
      <strong>Projects &amp; HR (9)</strong><br>
      <code>prj_projects</code> • <code>prj_sprints</code> • <code>prj_tasks</code> • <code>prj_worklogs</code> • <code>prj_milestones</code> • <code>hr_employees</code> • <code>hr_departments</code> • <code>hr_attendance</code> • <code>hr_payroll_runs</code>
    </div>
    <div class="card" style="padding:5px 7px;">
      <strong>Finance &amp; Supply (11)</strong><br>
      <code>fin_invoices</code> • <code>fin_payments</code> • <code>fin_journal_entries</code> • <code>fin_journal_lines</code> • <code>inv_warehouses</code> • <code>inv_products</code> • <code>inv_stock_moves</code> • <code>inv_assets</code> • <code>proc_vendors</code> • <code>proc_purchase_orders</code> • <code>proc_grns</code>
    </div>
  </div>
  <div class="grid-3" style="font-size: 7.2pt;">
    <div class="card" style="padding:6px 8px;">
      <strong>Support &amp; Collaboration (6)</strong><br>
      <code>sup_tickets</code> • <code>sup_sla_policies</code> • <code>sup_comments</code> • <code>collab_channels</code> • <code>collab_messages</code> • <code>collab_notifications</code>
    </div>
    <div class="card" style="padding:6px 8px;">
      <strong>Compliance &amp; Documents (5)</strong><br>
      <code>comp_audit_events</code> • <code>comp_controls</code> • <code>comp_dsar_requests</code> • <code>doc_files</code> • <code>doc_versions</code>
    </div>
    <div class="card" style="padding:6px 8px;">
      <strong>Automation &amp; AI Copilot (5)</strong><br>
      <code>auto_rules</code> • <code>auto_executions</code> • <code>ai_queries</code> • <code>ai_anomalies</code> • <code>ai_forecasts</code>
    </div>
  </div>

  <h2>6. Complete STAT6 BMS Architectural Mindmap <span class="sec-tag">Section 26</span></h2>
  <div class="mindmap-grid">
    <div class="mm-branch">
      <div class="mm-title">01. Identity &amp; Org</div>
      <ul class="mm-list">
        <li>JWT / OAuth2 / MFA Auth</li>
        <li>4-Persona RBAC Matrix</li>
        <li>Multi-Tenant <code>org_id</code> RLS</li>
        <li>Departments, Teams &amp; Locations</li>
      </ul>
    </div>
    <div class="mm-branch">
      <div class="mm-title">02. CRM &amp; Marketing</div>
      <ul class="mm-list">
        <li>Leads Capture &amp; Scoring</li>
        <li>Accounts 360° &amp; Contacts</li>
        <li>6-Stage Deals Kanban &amp; Quotes</li>
        <li>UTM Campaigns &amp; Blended ROI</li>
      </ul>
    </div>
    <div class="mm-branch">
      <div class="mm-title">03. Projects &amp; HR</div>
      <ul class="mm-list">
        <li>Sprint 44 Jira Kanban &amp; Tasks</li>
        <li>GitHub / Figma / Honeycomb Links</li>
        <li>Employee Roster &amp; ATS Pipeline</li>
        <li>Attendance Clock &amp; Monthly Payroll</li>
      </ul>
    </div>
    <div class="mm-branch">
      <div class="mm-title">04. Finance &amp; Supply Chain</div>
      <ul class="mm-list">
        <li>Net30 Invoices &amp; Auto-Dunning</li>
        <li>Double-Entry General Ledger</li>
        <li>Multi-Warehouse SKUs &amp; Assets</li>
        <li>Vendor POs &amp; 3-Way GRN Match</li>
      </ul>
    </div>
    <div class="mm-branch">
      <div class="mm-title">05. Support &amp; Collaboration</div>
      <ul class="mm-list">
        <li>SLA Countdown Ticket Queue</li>
        <li>Auto-Escalation on Breaches</li>
        <li>Multi-Channel Team Chat</li>
        <li>Versioned Document Cloud</li>
      </ul>
    </div>
    <div class="mm-branch">
      <div class="mm-title">06. Governance, Automation &amp; AI</div>
      <ul class="mm-list">
        <li>SHA-256 Immutable Audit Trail</li>
        <li>SOC 2 Type II &amp; GDPR DSAR</li>
        <li>Declarative WHEN-IF-DO Engine</li>
        <li>AI Copilot Telemetry Synthesis</li>
      </ul>
    </div>
  </div>

  <h2>7. Production Verification &amp; Automated QA Audit (67/67 Passing) <span class="sec-tag">Section 27</span></h2>
  <table class="arch-table" style="margin-bottom:0;">
    <thead>
      <tr>
        <th>Verification Phase</th>
        <th>Test Suite</th>
        <th>Validated Architectural Capabilities</th>
        <th>Assertions</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>Phases 1–3</strong></td><td><code>test_phase1..3.py</code></td><td>API Gateway Routing, JWT/RBAC Auth, CRM Lead Conversion, Deals Pipeline, Marketing ROI</td><td>16 / 16</td><td><span class="status-pass">100% PASS</span></td></tr>
      <tr><td><strong>Phases 4–6</strong></td><td><code>test_phase4..6.py</code></td><td>Jira Sprint Kanban, Time Worklogs, HR Attendance &amp; Payroll, Net30 Invoices, Double-Entry Ledger</td><td>18 / 18</td><td><span class="status-pass">100% PASS</span></td></tr>
      <tr><td><strong>Phases 7–9</strong></td><td><code>test_phase7..9.py</code></td><td>Warehouse Low-Stock Events, 3-Way PO/GRN Matching, SLA Timers, Chat Channels, SHA-256 Audit</td><td>18 / 18</td><td><span class="status-pass">100% PASS</span></td></tr>
      <tr><td><strong>Phase 10 &amp; E2E</strong></td><td><code>test_phase10 &amp; e2e.py</code></td><td>WHEN-IF-DO Rule Engine, AI Copilot Synthesis, Full Cross-Service Distributed E2E Lifecycle</td><td>15 / 15</td><td><span class="status-pass">100% PASS</span></td></tr>
    </tbody>
  </table>

</body>
</html>"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    # 1. Print the master Architectural + UI PDF
    cmd_pdf = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_pdf_downloads}",
        html_file
    ]
    subprocess.run(cmd_pdf, capture_output=True, text=True)
    shutil.copy2(output_pdf_downloads, output_pdf_repo)

    # 2. Generate a dedicated high-res standalone UI Showcase PNG so the GitHub repo shows how the UI looks directly
    ui_preview_html = os.path.join(downloads_dir, "stat6_ui_preview_temp.html")
    ui_preview_png = os.path.join(ui_dir, "STAT6_Enterprise_UI_Showcase.png")

    ui_only_start = html_content.find('<h2>3. How the STAT6 UI Looks')
    ui_only_end = html_content.find('<!-- PAGE 3:')
    style_end = html_content.find('</head>')
    ui_showcase_doc = (
        html_content[:style_end]
        + "<style>body { padding: 24px 32px; background: #f8fafc; }</style></head><body>"
        + html_content[ui_only_start:ui_only_end]
        + "</body></html>"
    )
    with open(ui_preview_html, "w", encoding="utf-8") as f:
        f.write(ui_showcase_doc)

    cmd_shot = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--window-size=1440,960",
        f"--screenshot={ui_preview_png}",
        ui_preview_html
    ]
    subprocess.run(cmd_shot, capture_output=True, text=True)

    # Also generate a high-res Architecture Diagram PNG for the README preview
    arch_preview_html = os.path.join(downloads_dir, "stat6_arch_preview_temp.html")
    arch_preview_png = os.path.join(ui_dir, "STAT6_System_Architecture_Topology.png")
    arch_start = html_content.find('<div class="cover-hero">')
    arch_end = html_content.find('<h2>3. How the STAT6 UI Looks')
    arch_showcase_doc = (
        html_content[:style_end]
        + "<style>body { padding: 24px 32px; background: #ffffff; }</style></head><body>"
        + html_content[arch_start:arch_end]
        + "</body></html>"
    )
    with open(arch_preview_html, "w", encoding="utf-8") as f:
        f.write(arch_showcase_doc)

    cmd_arch_shot = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--window-size=1440,1220",
        f"--screenshot={arch_preview_png}",
        arch_preview_html
    ]
    subprocess.run(cmd_arch_shot, capture_output=True, text=True)

    # 3. Write a clean, executive README.md for the private repository containing ONLY the Architecture PDF & UI Showcase
    readme_path = os.path.join(repo_stage_dir, "README.md")
    readme_content = """# STAT6 — Enterprise Business Management System (BMS) Architecture & UI

> **Official Product & Technical Architecture Specification (v2.4 Production)**

---

## 📄 Architectural Specification PDF

- **[Download / View `STAT6_BMS_Architecture_and_UI.pdf`](./STAT6_BMS_Architecture_and_UI.pdf)**  
  *Complete 4-page executive architecture specification covering the 14 autonomous FastAPI microservices (`:8000`–`:8013`), 52-table Supabase Cloud PostgreSQL 17.6 schema (`eu-central-1`), event-driven `WHEN-IF-DO` automation bus, double-entry General Ledger, 3-way procurement matching, SHA-256 cryptographic audit chain, and live UI visual showcase.*

---

## 🖥️ How the STAT6 UI Looks

![STAT6 Enterprise UI Showcase](./ui-showcase/STAT6_Enterprise_UI_Showcase.png)

### Key UI Design Pillars
1. **Deep Navy (`#162340`) Enterprise Sidebar**: Houses the blue `STAT6` brand emblem, color-coded outline vector icons, collapsible domain folders (*Sales Workspace*, *Operations*), and live Supabase connection telemetry.
2. **CRM Leads & Sales Workspace**: Full-bleed vertical-divider data tables (`border-r`), avatar initials badges, multi-criteria filtering, and 1-click lead conversion.
3. **Agile Sprint 44 Kanban & Slide-Over Inspector**: Real-time task cards (`FIN-50`, `FIN-51`, `FIN-52`) with story points and native GitHub PR / Figma / Honeycomb linkage.
4. **Executive Telemetry & AI Copilot**: Live revenue/pipeline KPIs paired with permission-checked natural-language AI synthesis and `WHEN-IF-DO` automation triggers.

---

## 🏗️ System Architecture Topology

![STAT6 System Architecture Topology](./ui-showcase/STAT6_System_Architecture_Topology.png)
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    for tmp in [html_file, ui_preview_html, arch_preview_html]:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except:
                pass

    print("PDF Exists in Downloads:", os.path.exists(output_pdf_downloads), os.path.getsize(output_pdf_downloads))
    print("PDF Exists in Repo Stage:", os.path.exists(output_pdf_repo), os.path.getsize(output_pdf_repo))
    print("UI Showcase PNG Exists:", os.path.exists(ui_preview_png), os.path.getsize(ui_preview_png))
    print("Arch Topology PNG Exists:", os.path.exists(arch_preview_png), os.path.getsize(arch_preview_png))

if __name__ == "__main__":
    generate_architecture_pdf_and_ui_assets()

