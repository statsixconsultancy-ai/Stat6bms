import os
import subprocess
import sys

def generate_pdf():
    downloads_dir = os.path.expanduser(r"~\Downloads")
    if not os.path.exists(downloads_dir):
        downloads_dir = r"C:\Users\prann\Downloads"
        
    output_pdf = os.path.join(downloads_dir, "STAT6_Frontend_Documentation.pdf")
    html_file = os.path.join(downloads_dir, "stat6_doc_temp.html")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>STAT6 Frontend Architecture & Technical Specification</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4;
      margin: 16mm 14mm 16mm 14mm;
      @bottom-right {
        content: "Page " counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }
    }
    
    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
    
    body {
      font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
      color: #0f172a;
      background-color: #ffffff;
      line-height: 1.5;
      font-size: 9.5pt;
      margin: 0;
      padding: 0;
    }

    h1, h2, h3, h4 {
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #090d16;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-top: 0;
    }

    h1 {
      font-size: 20pt;
      line-height: 1.2;
      border-bottom: 2px solid #2563eb;
      padding-bottom: 6px;
      margin-bottom: 14px;
    }

    h2 {
      font-size: 13pt;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 4px;
      margin-top: 18px;
      margin-bottom: 10px;
      color: #1e293b;
      page-break-after: avoid;
    }

    h3 {
      font-size: 10.5pt;
      margin-top: 12px;
      margin-bottom: 6px;
      color: #2563eb;
      page-break-after: avoid;
    }

    p {
      margin-top: 0;
      margin-bottom: 8px;
      color: #1e293b;
    }

    .cover-banner {
      background: linear-gradient(135deg, #162340 0%, #0d1527 100%);
      color: #ffffff;
      padding: 24px;
      border-radius: 12px;
      margin-bottom: 20px;
      border: 1px solid #1e293b;
    }

    .cover-badge {
      display: inline-block;
      background: #2563eb;
      color: #ffffff;
      font-size: 8pt;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 10px;
    }

    .cover-title {
      font-size: 22pt;
      font-weight: 800;
      color: #ffffff;
      margin: 0 0 6px 0;
      letter-spacing: -0.03em;
    }

    .cover-subtitle {
      font-size: 10.5pt;
      color: #cbd5e1;
      margin: 0 0 16px 0;
      font-weight: 400;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      background: rgba(255, 255, 255, 0.07);
      padding: 12px;
      border-radius: 8px;
      font-size: 8pt;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .meta-item strong {
      display: block;
      color: #93c5fd;
      font-size: 7.5pt;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .meta-item span {
      color: #ffffff;
      font-weight: 500;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      margin-bottom: 14px;
      font-size: 8.5pt;
      page-break-inside: avoid;
    }

    th, td {
      padding: 6px 9px;
      text-align: left;
      border: 1px solid #e2e8f0;
      vertical-align: top;
    }

    th {
      background-color: #f8fafc;
      color: #0f172a;
      font-weight: 700;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    td {
      color: #000000;
      font-weight: 400;
    }

    tr:nth-child(even) td {
      background-color: #fbfcfe;
    }

    .badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 7.5pt;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }

    .badge-blue { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .badge-green { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-rose { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
    .badge-purple { background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }
    .badge-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }

    .card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 12px;
      page-break-inside: avoid;
    }

    .card-title {
      font-size: 9.5pt;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
      page-break-inside: avoid;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
      page-break-inside: avoid;
    }

    code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 8pt;
      background: #f1f5f9;
      padding: 1px 4px;
      border-radius: 3px;
      color: #0f172a;
    }

    pre {
      background: #0f172a;
      color: #f8fafc;
      padding: 10px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      overflow-x: auto;
      line-height: 1.4;
      margin-top: 4px;
      margin-bottom: 10px;
      page-break-inside: avoid;
    }

    .page-break {
      page-break-before: always;
    }

    .callout {
      border-left: 3px solid #2563eb;
      background: #f8fafc;
      padding: 8px 12px;
      border-radius: 0 6px 6px 0;
      margin-bottom: 10px;
      font-size: 8.5pt;
    }

    .callout-title {
      font-weight: 700;
      color: #1e3a8a;
      margin-bottom: 2px;
    }

    .footer-note {
      font-size: 7.5pt;
      color: #64748b;
      text-align: center;
      margin-top: 20px;
      border-top: 1px solid #e2e8f0;
      padding-top: 8px;
    }

    .color-swatch {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 2px;
      vertical-align: middle;
      margin-right: 4px;
      border: 1px solid rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>

  <!-- COVER BANNER -->
  <div class="cover-banner">
    <div class="cover-badge">Enterprise Production Reference</div>
    <div class="cover-title">STAT6 Platform</div>
    <div class="cover-subtitle">Complete Front-End Architecture, Design System & Technical Specification Manual</div>
    <div class="meta-grid">
      <div class="meta-item">
        <strong>Document Version</strong>
        <span>Release 2.4.0 (Enterprise)</span>
      </div>
      <div class="meta-item">
        <strong>Target Stack</strong>
        <span>React 18 + Vite + Tailwind CSS</span>
      </div>
      <div class="meta-item">
        <strong>Cloud Database</strong>
        <span>Supabase PostgreSQL (EU)</span>
      </div>
      <div class="meta-item">
        <strong>Hosting / CI</strong>
        <span>Vercel + GitHub Actions</span>
      </div>
    </div>
  </div>

  <!-- SECTION 1 -->
  <h2>1. Executive Summary & Front-End Architecture</h2>
  <p>
    <strong>STAT6</strong> is a high-density, multi-tenant commercial and operations management platform designed to replace monolithic ERP/CRM software with a responsive, zero-latency distributed system. The front-end serves as the unified single-pane-of-glass interface connecting across <strong>14 autonomous microservices</strong> through a Central API Gateway reverse proxy and event mesh.
  </p>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Front-End Core Tenets</div>
      <ul style="margin: 0; padding-left: 16px; font-size: 8.5pt;">
        <li><strong>High Data Density</strong>: Maximized viewable information with compact table rows and minimal padding.</li>
        <li><strong>Zero Emojis</strong>: Exclusively clean vector outline SVG and Lucide icons across the entire platform.</li>
        <li><strong>Strict Typography Hierarchy</strong>: ONLY headlines and column titles are bold; all data cells, numbers, metadata, and body text are standard weight (<code>font-normal</code>).</li>
        <li><strong>Solid Black Legibility</strong>: All table content, labels, customer names, and emails are rendered in solid black (<code>#000000</code>).</li>
        <li><strong>Column Separation</strong>: Subtle vertical dividers (<code>border-r border-slate-200</code>) between column headers.</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">Technical Specifications</div>
      <ul style="margin: 0; padding-left: 16px; font-size: 8.5pt;">
        <li><strong>Core Framework</strong>: React 18.3 + TypeScript 5.5</li>
        <li><strong>Build Tooling</strong>: Vite 6.4.3 (HMR &lt; 500ms, tree-shaking)</li>
        <li><strong>Styling Engine</strong>: Tailwind CSS 3.4 JIT + Custom CSS layers</li>
        <li><strong>Typography</strong>: Google Fonts <em>Plus Jakarta Sans</em> &amp; <em>Inter</em></li>
        <li><strong>State Architecture</strong>: React State Hooks + Local Fallback Mock Layer</li>
        <li><strong>API Integration</strong>: Central Gateway Proxy (<code>/api/v1/*</code>) with 100% offline resilience</li>
      </ul>
    </div>
  </div>

  <!-- SECTION 2 -->
  <h2>2. Visual System, Typography & Color Tokens</h2>
  <p>
    The visual system enforces mathematical consistency across all viewports with precise font metrics, high contrast ratios, and deliberate color attributions:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Font Family / Role</th>
        <th style="width: 25%;">Weights &amp; Letter-Spacing</th>
        <th style="width: 50%;">Usage &amp; Visual Intent</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Plus Jakarta Sans</strong><br><em>Primary Geometric Sans</em></td>
        <td><code>700 (Bold)</code>, <code>800 (ExtraBold)</code><br>Tracking: <code>-0.02em</code></td>
        <td>Used for all primary headings (<code>h1</code>–<code>h6</code>), the STAT6 brand wordmark, column titles, and modal headers. Provides open counters and crisp geometric round forms.</td>
      </tr>
      <tr>
        <td><strong>Inter</strong><br><em>Interface &amp; Body Sans</em></td>
        <td><code>400 (Regular)</code>, <code>500 (Medium)</code><br>Tracking: <code>-0.01em</code></td>
        <td>Used for all table data cells, names, company names, emails, and form inputs. Features tabular numbers for aligned accounting and metric displays.</td>
      </tr>
      <tr>
        <td><strong>JetBrains Mono</strong><br><em>Monospace Code &amp; IDs</em></td>
        <td><code>400 (Regular)</code>, <code>600 (SemiBold)</code></td>
        <td>Used for transaction hashes, ticket IDs (<code>TICK-101</code>), sprint keys (<code>FIN-50</code>), invoice numbers, and currency formatting.</td>
      </tr>
    </tbody>
  </table>

  <h3>Color Palette &amp; Token Architecture</h3>
  <table>
    <thead>
      <tr>
        <th>Design Token</th>
        <th>Hex Code</th>
        <th>Role &amp; Element Mapping</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>sidebar-bg</code></td>
        <td><span class="color-swatch" style="background:#162340;"></span><code>#162340</code></td>
        <td>Deep Navy Sidebar background matching reference enterprise aesthetic.</td>
      </tr>
      <tr>
        <td><code>brand-blue</code></td>
        <td><span class="color-swatch" style="background:#2563eb;"></span><code>#2563eb</code></td>
        <td>STAT6 Logo badge, primary interactive buttons, and active tabs.</td>
      </tr>
      <tr>
        <td><code>sidebar-active</code></td>
        <td><span class="color-swatch" style="background:#243964;"></span><code>#243964</code></td>
        <td>Active pill background for selected menu items (e.g., Leads).</td>
      </tr>
      <tr>
        <td><code>accent-sales</code></td>
        <td><span class="color-swatch" style="background:#e11d48;"></span><code>#e11d48</code></td>
        <td>Sales category badge container with white letter 'S'.</td>
      </tr>
      <tr>
        <td><code>nav-home</code></td>
        <td><span class="color-swatch" style="background:#38bdf8;"></span><code>#38bdf8</code></td>
        <td>Sky Blue outline vector icon for Home / Executive Cockpit.</td>
      </tr>
      <tr>
        <td><code>nav-reports</code></td>
        <td><span class="color-swatch" style="background:#f43f5e;"></span><code>#f43f5e</code></td>
        <td>Rose Red outline vector icon for Reports / BI Analytics.</td>
      </tr>
      <tr>
        <td><code>nav-analytics</code></td>
        <td><span class="color-swatch" style="background:#c084fc;"></span><code>#c084fc</code></td>
        <td>Lavender Violet outline vector icon for Analytics &amp; Telemetry.</td>
      </tr>
      <tr>
        <td><code>nav-requests</code></td>
        <td><span class="color-swatch" style="background:#34d399;"></span><code>#34d399</code></td>
        <td>Mint Green outline vector icon for My Requests &amp; Support.</td>
      </tr>
      <tr>
        <td><code>nav-agents</code></td>
        <td><span class="color-swatch" style="background:#fb923c;"></span><code>#fb923c</code></td>
        <td>Amber Orange outline vector icon for Autonomous AI Agents.</td>
      </tr>
      <tr>
        <td><code>canvas-light</code></td>
        <td><span class="color-swatch" style="background:#f0f2f8;"></span><code>#f0f2f8</code></td>
        <td>Workspace canvas background; provides soft contrast against pure white cards.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 3 -->
  <h2>3. Master Application Shell &amp; Navigation Engine</h2>
  <p>
    The master layout is implemented in <code>frontend/src/App.tsx</code> using a three-tier layout model consisting of the <strong>Deep Navy Enterprise Sidebar</strong>, the <strong>Top Workspace Header Bar</strong>, and the <strong>Scrollable Viewport Canvas</strong>.
  </p>

  <div class="callout">
    <div class="callout-title">Sidebar Brand Component Specification</div>
    The top-left sidebar header displays the enterprise brand identity matching the reference design:
    <br>
    <code>&lt;div className="h-7 w-7 rounded-lg bg-[#2563eb] flex items-center justify-center text-white"&gt;&lt;BarChart2 size={16} /&gt;&lt;/div&gt;</code>
    paired with <code>&lt;span className="font-bold text-[16px] text-white tracking-wider"&gt;STAT6&lt;/span&gt;</code> and a version tag badge <code>v2.4</code>.
  </div>

  <h3>Navigation Hierarchy &amp; Tree Structure</h3>
  <div class="grid-3">
    <div class="card">
      <div class="card-title">1. Quick Header Links</div>
      <p style="font-size: 8pt; margin: 0;">Five direct action buttons with dedicated vector outline icons:</p>
      <ul style="margin: 4px 0 0 0; padding-left: 16px; font-size: 8pt;">
        <li><code>Home</code> (Sky Blue <code>#38bdf8</code>)</li>
        <li><code>Reports</code> (Coral Red <code>#f43f5e</code>)</li>
        <li><code>Analytics</code> (Purple <code>#c084fc</code>)</li>
        <li><code>My Requests</code> (Mint <code>#34d399</code>)</li>
        <li><code>Agents</code> (Orange <code>#fb923c</code>)</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">2. Category &amp; Search</div>
      <p style="font-size: 8pt; margin: 0;">Module context &amp; quick filtering:</p>
      <ul style="margin: 4px 0 0 0; padding-left: 16px; font-size: 8pt;">
        <li>Red 'S' badge: <code>bg-[#e11d48]</code></li>
        <li>Category Title: <code>Sales ▾</code></li>
        <li>Options button: <code>MoreHorizontal</code></li>
        <li>Omnisearch trigger: dark input with <code>Search</code> outline + <code>Ctrl+K</code></li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">3. Expandable Folders</div>
      <p style="font-size: 8pt; margin: 0;">Collapsible microservice domains:</p>
      <ul style="margin: 4px 0 0 0; padding-left: 16px; font-size: 8pt;">
        <li><strong>Sales</strong>: Leads, Contacts, Deals</li>
        <li><strong>Operations</strong>: Projects, Marketing, HR, Finance, Inventory, Procurement, Support</li>
        <li><strong>Governance &amp; AI</strong>: Team Chat, Compliance, Rules, Settings</li>
      </ul>
    </div>
  </div>

  <!-- SECTION 4 -->
  <h2>4. Detailed Module Specifications (All 14 Modules)</h2>
  
  <h3>Module 01: Sales &amp; CRM — Leads View (Reference Image Match)</h3>
  <p>
    The Leads view in <code>activeTab === 'leads'</code> reproduces the exact pixel layout from the user-provided reference image:
  </p>
  <ul>
    <li><strong>Page Header</strong>: Bold headline <code>Leads</code> with an action button <code>+ Add Lead</code>.</li>
    <li><strong>Table Container</strong>: Crisp white card with <code>rounded-2xl border border-slate-200 shadow-xs</code>.</li>
    <li><strong>Header Row</strong>: High-contrast bold column names with vertical divider lines (<code>border-r border-slate-200</code>):
      <br>1. <code>Lead Name (All ▾)</code> | 2. <code>Company</code> | 3. <code>Lead Source</code> | 4. <code>Email</code> | 5. <code>Lead Owner</code>
    </li>
    <li><strong>Data Cells</strong>: Standard regular weight (<code>font-normal</code>) and pure black (<code>#000000</code>).</li>
    <li><strong>Avatars</strong>: Circular photo avatars with subtle ring styling for both leads and assigned lead owners.</li>
    <li><strong>Clean Menu</strong>: The 3 unfilled placeholder rows under Deals Pipeline have been cleanly removed from the sidebar.</li>
  </ul>

  <table>
    <thead>
      <tr>
        <th>Lead Name</th>
        <th>Company</th>
        <th>Lead Source</th>
        <th>Email Address</th>
        <th>Lead Owner</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Greg Howard</strong></td>
        <td>Howard Techno</td>
        <td>Trade Show</td>
        <td><code>greg@howard.com</code></td>
        <td>Bob Ross</td>
      </tr>
      <tr>
        <td><strong>Robert Green</strong></td>
        <td>Hitech Solution</td>
        <td>Cold Call</td>
        <td><code>green.robert@hitech.com</code></td>
        <td>Tim Roberts</td>
      </tr>
      <tr>
        <td><strong>Kris Marrier</strong></td>
        <td>Brown Horizon LLC</td>
        <td>Advertisement</td>
        <td><code>kris@brownhorizon.com</code></td>
        <td>Richard Mc</td>
      </tr>
      <tr>
        <td><strong>Amelia Burrows</strong></td>
        <td>GemStone Tech</td>
        <td>Webinar</td>
        <td><code>b.amelia@zylker.com</code></td>
        <td>Bob Ross</td>
      </tr>
      <tr>
        <td><strong>Krishna Das</strong></td>
        <td>Zylker Logistics</td>
        <td>Email Campaign</td>
        <td><code>krishna.das@zylker.com</code></td>
        <td>Richard Mc</td>
      </tr>
    </tbody>
  </table>

  <h3>Module 01: Sales &amp; CRM — Deals Pipeline (Kanban Board)</h3>
  <p>
    Renders 6 sequential deal stages: <code>New</code>, <code>Contacted</code>, <code>Qualified</code>, <code>Proposal</code>, <code>Negotiation</code>, and <code>Won</code>. Each deal card displays the title, associated enterprise account, deal amount, and win probability percentage. Total pipeline value is aggregated live at the top (<code>$580,000</code>).
  </p>

  <div class="page-break"></div>

  <h3>Module 03: Projects &amp; Agile Sprints (Jira Board)</h3>
  <p>
    Sprint 44 execution board with drag-and-drop status columns: <code>Blocked</code>, <code>In progress</code>, <code>Ready for review</code>, and <code>Done</code>. Clicking an issue card opens the <strong>Jira Slide-Over Inspector Drawer</strong> with connected tool badges (GitHub PRs, Honeycomb telemetry, Figma design flows), story points, account linkages, and instant status transitions.
  </p>

  <h3>Remaining Microservice Views Summary</h3>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Module Tab</th>
        <th style="width: 20%;">Key Components</th>
        <th style="width: 55%;">Functionality &amp; UI Behavior</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>overview</code></td>
        <td>KPI Cards, Trajectory</td>
        <td>Paid revenue ($79.7k), active pipeline, overdue receivables ($27.5k), and consolidated monthly trajectory bar chart.</td>
      </tr>
      <tr>
        <td><code>contacts</code></td>
        <td>Accounts Directory</td>
        <td>360° enterprise customer directory with industry, employee count, global location, and annual revenue.</td>
      </tr>
      <tr>
        <td><code>marketing</code></td>
        <td>Campaign Ledger</td>
        <td>Multi-channel marketing attribution, CAC calculations, conversion rates, and blended ROI matrix.</td>
      </tr>
      <tr>
        <td><code>hr</code></td>
        <td>Employee Roster</td>
        <td>Staff directory with role badges, department classifications, attendance clocking, and monthly payroll execute trigger.</td>
      </tr>
      <tr>
        <td><code>finance</code></td>
        <td>Invoice Register</td>
        <td>Net30 invoice table with payment status indicators (<code>Paid</code> / <code>Overdue</code>), payment settlement, and ledger sync.</td>
      </tr>
      <tr>
        <td><code>inventory</code></td>
        <td>Warehouse SKUs</td>
        <td>Multi-warehouse stock levels with automated low-stock warnings and one-click purchase order auto-drafting.</td>
      </tr>
      <tr>
        <td><code>procurement</code></td>
        <td>Purchase Orders</td>
        <td>Vendor PO lifecycle tracking, delivery date monitoring, and automated 3-way matching against invoice ledger.</td>
      </tr>
      <tr>
        <td><code>support</code></td>
        <td>SLA Countdown Queue</td>
        <td>Customer ticket triage with dynamic SLA countdown badges, priority indicators, and live agent assignments.</td>
      </tr>
      <tr>
        <td><code>collaboration</code></td>
        <td>Team Channels</td>
        <td>Interactive multi-channel chat (<code>#general</code>, <code>#engineering</code>, <code>#deals</code>) with instant messaging and timestamps.</td>
      </tr>
      <tr>
        <td><code>compliance</code></td>
        <td>Security Audit</td>
        <td>SOC 2 Type II attestation badges, GDPR / HIPAA compliance markers, Single-Tenant RLS verification, and MSA modals.</td>
      </tr>
      <tr>
        <td><code>automation</code></td>
        <td>WHEN-IF-DO Rules</td>
        <td>Declarative business event automations displayed in 3-part cards (TRIGGER, CONDITION, ACTION) with active toggles.</td>
      </tr>
      <tr>
        <td><code>ai</code></td>
        <td>Operations Assistant</td>
        <td>Cross-microservice natural language queries with contextual recommendations and automated action triggers.</td>
      </tr>
      <tr>
        <td><code>settings</code></td>
        <td>Module Toggles</td>
        <td>Interactive 14-service toggle matrix enabling or disabling individual microservice capabilities on demand.</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 5 -->
  <h2>5. State Management &amp; Central API Gateway Integration</h2>
  <p>
    The front-end integrates with the backend through a unified reverse-proxy pattern via <code>API_BASE</code>:
  </p>
  <pre>const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api/v1";</pre>
  <p>
    All data fetching calls are wrapped in resilient handlers with <code>.catch(() =&gt; {})</code> fallbacks, ensuring that if the backend is unreachable during client previews or offline mode, the front-end continues to render rich, populated interface views without throwing fatal errors.
  </p>

  <!-- SECTION 6 -->
  <h2>6. Production Build &amp; Vercel Deployment Architecture</h2>
  <p>
    The repository has been structured for zero-configuration, automated deployment on <strong>Vercel</strong>:
  </p>

  <div class="card">
    <div class="card-title">Root <code>vercel.json</code> Configuration</div>
    <pre>{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}</pre>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Production Build Metrics</div>
      <ul style="margin: 0; padding-left: 16px; font-size: 8pt;">
        <li><strong>Transformations</strong>: 1,588 modules transformed cleanly</li>
        <li><strong>HTML Size</strong>: <code>0.84 kB</code> (gzip: 0.47 kB)</li>
        <li><strong>CSS Bundle</strong>: <code>20.32 kB</code> (gzip: 4.60 kB)</li>
        <li><strong>JS Bundle</strong>: <code>212.87 kB</code> (gzip: 59.32 kB)</li>
        <li><strong>Build Duration</strong>: 2.37 seconds (Zero TS errors)</li>
      </ul>
    </div>

    <div class="card">
      <div class="card-title">Deployment Steps</div>
      <ol style="margin: 0; padding-left: 16px; font-size: 8pt;">
        <li>Import <code>statsixconsultancy-ai/Statsixuni</code> in Vercel.</li>
        <li>Framework Preset defaults automatically to <strong>Vite</strong>.</li>
        <li>Build Command &amp; Output directory detected from <code>vercel.json</code>.</li>
        <li>Optionally add <code>VITE_API_BASE</code> in Environment Variables.</li>
        <li>Deploy with automated global edge CDN &amp; SSL certificates.</li>
      </ol>
    </div>
  </div>

  <div class="footer-note">
    STAT6 Commercial &amp; Operations Platform • Confidential &amp; Proprietary • Generated on September 24, 2026
  </div>

</body>
</html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Temporary HTML written to: {html_file}")
    
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_pdf}",
        html_file
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 0:
        size_kb = os.path.getsize(output_pdf) / 1024
        print(f"SUCCESS: PDF created at: {output_pdf} ({size_kb:.1f} KB)")
        try:
            os.remove(html_file)
        except:
            pass
        return output_pdf
    else:
        print("ERROR: Failed to generate PDF.")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return None

if __name__ == "__main__":
    generate_pdf()
