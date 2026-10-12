import os
import subprocess


def generate_comparison_pdf():
    downloads_dir = os.path.expanduser(r"~\Downloads")
    if not os.path.exists(downloads_dir):
        downloads_dir = r"C:\Users\prann\Downloads"

    output_pdf = os.path.join(
        downloads_dir, "STAT6_vs_Previous_BMS_Architecture_Comparison.pdf"
    )
    html_file = os.path.join(downloads_dir, "stat6_vs_bms_temp.html")

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Technical Architecture Comparative Evaluation: STAT6 BMS vs. Legacy BMS Specification</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4;
      margin: 18mm 18mm 18mm 18mm;
      @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Inter', Arial, sans-serif;
        font-size: 8pt;
        color: #000000;
      }
      @bottom-left {
        content: "STAT6 Engineering Architecture Evaluation";
        font-family: 'Inter', Arial, sans-serif;
        font-size: 8pt;
        color: #000000;
      }
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      color: #000000;
      background-color: #ffffff;
      line-height: 1.48;
      font-size: 9pt;
      margin: 0;
      padding: 0;
    }

    /* FORMAL DOCUMENT HEADER */
    .doc-header {
      border-bottom: 2px solid #000000;
      padding-bottom: 10px;
      margin-bottom: 14px;
    }

    .doc-type {
      font-size: 8pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 4px;
      color: #000000;
    }

    .doc-title {
      font-size: 15pt;
      font-weight: 700;
      color: #000000;
      margin: 0 0 6px 0;
      line-height: 1.25;
      letter-spacing: -0.01em;
    }

    .doc-meta-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      font-size: 8.2pt;
    }

    .doc-meta-table td {
      padding: 3px 6px 3px 0;
      border: none;
      color: #000000;
      vertical-align: top;
    }

    .doc-meta-table td.meta-label {
      font-weight: 700;
      width: 16%;
      white-space: nowrap;
    }

    .doc-meta-table td.meta-val {
      width: 34%;
    }

    /* HEADINGS */
    h2 {
      font-size: 10.5pt;
      font-weight: 700;
      color: #000000;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      border-bottom: 1px solid #000000;
      padding-bottom: 3px;
      margin-top: 16px;
      margin-bottom: 8px;
      page-break-after: avoid;
    }

    h3 {
      font-size: 9.5pt;
      font-weight: 700;
      color: #000000;
      margin-top: 11px;
      margin-bottom: 5px;
      page-break-after: avoid;
    }

    p {
      margin-top: 0;
      margin-bottom: 7px;
      color: #000000;
      text-align: justify;
    }

    ul, ol {
      margin: 4px 0 8px 0;
      padding-left: 18px;
    }

    li {
      margin-bottom: 3.5px;
      color: #000000;
      text-align: left;
    }

    code {
      font-family: Consolas, "Courier New", monospace;
      font-size: 8.2pt;
      color: #000000;
    }

    /* FORMAL BLACK & WHITE TABLES */
    table.formal-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
      margin-bottom: 12px;
      font-size: 8.2pt;
      background-color: #ffffff;
    }

    table.formal-table tr {
      page-break-inside: avoid;
    }

    table.formal-table th,
    table.formal-table td {
      border: 1px solid #000000;
      padding: 5px 7px;
      text-align: left;
      vertical-align: top;
      color: #000000;
      background-color: #ffffff;
    }

    table.formal-table th {
      font-weight: 700;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      border-bottom: 1.5px solid #000000;
    }

    .page-break {
      page-break-before: always;
    }

    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 6px;
      margin-bottom: 10px;
    }

    .col-block {
      border: 1px solid #000000;
      padding: 8px 10px;
      background-color: #ffffff;
      page-break-inside: avoid;
    }

    .col-block-title {
      font-weight: 700;
      font-size: 8.8pt;
      border-bottom: 1px solid #000000;
      padding-bottom: 3px;
      margin-bottom: 6px;
      text-transform: uppercase;
    }
  </style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PAGE 1                                                                -->
  <!-- ===================================================================== -->
  <div class="doc-header">
    <div class="doc-type">Technical Architecture Evaluation &amp; Comparative Audit</div>
    <h1 class="doc-title">Comparative Architectural Assessment: STAT6 Enterprise BMS (v2.4) vs. Reference BMS Architecture Specification (v1.0)</h1>
    <table class="doc-meta-table">
      <tr>
        <td class="meta-label">Document Ref:</td>
        <td class="meta-val">ARCH-EVAL-2026-04</td>
        <td class="meta-label">System Under Review:</td>
        <td class="meta-val">STAT6 Business Management System (v2.4)</td>
      </tr>
      <tr>
        <td class="meta-label">Baseline Reference:</td>
        <td class="meta-val">BMS Architecture Specification (v1.0 PDF)</td>
        <td class="meta-label">Database Infrastructure:</td>
        <td class="meta-val">Supabase PostgreSQL 17.6 (AWS eu-central-1)</td>
      </tr>
    </table>
  </div>

  <h2>1.0 Executive Summary</h2>
  <p>
    This document presents a formal technical comparison between the <strong>STAT6 Enterprise Business Management System (v2.4)</strong> and the previously provided <strong>BMS Business Management System Architecture (v1.0)</strong> specification. While both architectures target unified enterprise operations across CRM, Sales, Marketing, Project Management, Human Resources, Finance, Inventory, Procurement, Customer Support, Collaboration, Compliance, and Automation, they differ fundamentally in architectural maturity, service decomposition, database design, financial controls, and implementation status.
  </p>
  <p>
    The baseline v1.0 specification outlines a conceptual 12-month development plan that begins as a <strong>Modular Monolith</strong> and defers microservice extraction, supply chain matching, and AI capabilities to later phases. In contrast, <strong>STAT6 v2.4</strong> is an operational, cloud-connected distributed system comprising <strong>14 independent FastAPI microservices (ports <code>8000</code>–<code>8013</code>)</strong>, <strong>52 relational tables deployed on Supabase Cloud PostgreSQL 17.6</strong>, a production <strong>React 18 + TypeScript + Vite 6</strong> frontend, and an automated verification suite passing <strong>67 of 67 integration and end-to-end assertions</strong>.
  </p>

  <h2>2.0 Architectural Comparison Matrix</h2>
  <table class="formal-table">
    <thead>
      <tr>
        <th style="width: 20%;">Evaluation Criterion</th>
        <th style="width: 38%;">Reference BMS Specification (v1.0 PDF)</th>
        <th style="width: 42%;">STAT6 Enterprise Platform (v2.4 Implementation)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Service Topology</strong></td>
        <td>Recommends starting as a <strong>Modular Monolith</strong> ("Start as a modular monolith — extract to microservices later"). Couples all business domains into a single runtime process and single failure domain.</td>
        <td>Engineered as <strong>14 autonomous FastAPI microservices</strong> (<code>:8000</code> Gateway + 13 domain services <code>:8001</code>–<code>:8013</code>). Each domain scales independently with strict process and fault isolation.</td>
      </tr>
      <tr>
        <td><strong>2. Delivery &amp; Build Status</strong></td>
        <td>Conceptual specification only. Proposes a sequential 12-month roadmap (Phase 1: Months 1–3; Phase 2: Months 4–6; Phase 3: Months 7–9; Phase 4: Months 10–12) with no executable code.</td>
        <td><strong>Fully implemented and verified.</strong> All 10 architectural phases (Phases 1 through 10) are built, connected to cloud PostgreSQL, and verified via 67 automated test assertions.</td>
      </tr>
      <tr>
        <td><strong>3. Database Schema &amp; Persistence</strong></td>
        <td>Lists approximately 25 high-level table names in text without physical schema definitions, foreign key constraints, or connection pooling configuration.</td>
        <td><strong>52 domain-prefixed relational tables</strong> live in <strong>Supabase PostgreSQL 17.6</strong> via AWS <code>eu-central-1</code> Supavisor connection pooler (port <code>6543</code>) with strict <code>org_id</code> multi-tenant isolation.</td>
      </tr>
      <tr>
        <td><strong>4. Accounting &amp; Ledger Controls</strong></td>
        <td>Mentions Chart of Accounts and Journal Entries conceptually without transaction balance enforcement or automated dunning logic.</td>
        <td><code>finance-service (:8006)</code> enforces GAAP double-entry accounting invariants (<code>SUM(debit) == SUM(credit)</code>) across <code>fin_journal_entries</code> and <code>fin_journal_lines</code>, plus Net30 dunning.</td>
      </tr>
      <tr>
        <td><strong>5. Procurement &amp; Inventory Controls</strong></td>
        <td>Defers warehouse management, purchase orders, and 3-way matching to Phase 3 (Months 7–9).</td>
        <td><code>inventory-service (:8007)</code> emits <code>stock.low</code> events when SKUs breach thresholds; <code>procurement-service (:8008)</code> executes automated <strong>3-Way Matching</strong> (<code>PO ↔ GRN ↔ Vendor Invoice</code>).</td>
      </tr>
      <tr>
        <td><strong>6. Audit Trail &amp; Regulatory Compliance</strong></td>
        <td>Describes a standard database audit table without cryptographic tamper-evidence or automated privacy export endpoints.</td>
        <td><code>compliance-service (:8011)</code> implements an immutable <strong>SHA-256 hash-chained audit ledger</strong> (<code>prev_hash + payload → curr_hash</code>), SOC 2 Type II control tracking, and GDPR DSAR exports.</td>
      </tr>
      <tr>
        <td><strong>7. Event Bus &amp; Workflow Engine</strong></td>
        <td>Illustrates conceptual <code>WHEN → IF → DO</code> rules without a message relay or webhook delivery tracking mechanism.</td>
        <td>Central API Gateway Event Relay + <code>automation-service (:8012)</code> evaluates live <code>WHEN-IF-DO</code> rules across <code>deal.won</code>, <code>lead.captured</code>, <code>stock.low</code>, <code>invoice.paid</code>, and <code>ticket.urgent</code>.</td>
      </tr>
      <tr>
        <td><strong>8. User Interface &amp; Frontend Architecture</strong></td>
        <td>No frontend codebase, UI screen specifications, or component hierarchy provided. Diagrams on Pages 3 and 12 contain unrendered font glyphs (<code>■■■</code>).</td>
        <td>Production <strong>React 18.3 + TypeScript 5.5 + Vite 6 + Tailwind CSS</strong> SPA featuring a structured enterprise sidebar, vertical-divider data tables, Jira-style Kanban board, and sub-15ms global search.</td>
      </tr>
    </tbody>
  </table>

  <h2>3.0 Structural Analysis: Distributed Microservices vs. Modular Monolith</h2>
  <p>
    A primary architectural divergence lies in Section 02 of the baseline BMS document, which advocates constructing a single monolithic application first and postponing service decomposition. In multi-tenant enterprise software, starting with a monolith introduces four operational risks that STAT6 avoids by design:
  </p>

  <div class="two-col">
    <div class="col-block">
      <div class="col-block-title">Limitations of the Baseline Monolith Approach</div>
      <ul>
        <li><strong>Shared Failure Domain</strong>: A resource-intensive operation in one module (such as monthly payroll calculation or large financial exports) degrades or crashes CRM, Support, and API responsiveness for all tenants.</li>
        <li><strong>Database Lock Contention</strong>: Monolithic ORM models frequently rely on cross-domain joins that create table lock contention under concurrent read/write workloads.</li>
        <li><strong>High Refactoring Cost</strong>: Decomposing a tightly coupled monolith after 12 months requires rewriting internal method calls into authenticated network calls and untangling shared database transactions.</li>
        <li><strong>Coupled Release Cycles</strong>: A minor change to a marketing form or support ticket workflow requires rebuilding, testing, and redeploying the entire financial and authentication core.</li>
      </ul>
    </div>
    <div class="col-block">
      <div class="col-block-title">Advantages of the STAT6 Microservice Architecture</div>
      <ul>
        <li><strong>Process &amp; Fault Isolation (Ports <code>8000</code>–<code>8013</code>)</strong>: Each business domain executes in an independent FastAPI process. High load on <code>marketing-service (:8003)</code> has zero impact on <code>finance-service (:8006)</code>.</li>
        <li><strong>Unified API Gateway (<code>:8000</code>)</strong>: Centralizes JWT verification, tenant <code>org_id</code> enforcement, health monitoring, and distributed cross-service omnisearch (<code>/api/v1/search</code>).</li>
        <li><strong>Event-Driven Decoupling</strong>: Services communicate state transitions asynchronously via signed events (such as <code>deal.won</code>) rather than mutating external domain tables directly.</li>
        <li><strong>Independent Deployment</strong>: Any individual microservice can be updated, scaled, or restarted without interrupting the remaining 13 services.</li>
      </ul>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PAGE 2                                                                -->
  <!-- ===================================================================== -->
  <div class="page-break"></div>

  <h2>4.0 Service-by-Service Implementation Audit</h2>
  <p>
    The table below details all 14 microservices operating in STAT6 v2.4, their physical PostgreSQL tables in Supabase, their verified functional scope, and their corresponding status in the baseline v1.0 specification.
  </p>

  <table class="formal-table">
    <thead>
      <tr>
        <th style="width: 16%;">Service &amp; Port</th>
        <th style="width: 30%;">Physical PostgreSQL Tables (Supabase)</th>
        <th style="width: 38%;">Implemented Capabilities in STAT6 v2.4</th>
        <th style="width: 16%;">Baseline v1.0 Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>api-gateway :8000</code></td>
        <td><code>gateway_events</code>, <code>gateway_routes</code></td>
        <td>Request routing, JWT authentication guard, event bus relay, distributed omnisearch (<code>&lt;15ms</code>), health aggregation.</td>
        <td>Conceptual diagram only</td>
      </tr>
      <tr>
        <td><code>auth-service :8001</code></td>
        <td><code>auth_organizations</code>, <code>auth_users</code>, <code>auth_roles</code>, <code>auth_permissions</code>, <code>auth_sessions</code></td>
        <td>Multi-tenant <code>org_id</code> partitioning, HMAC-SHA256 JWT + Supabase JWKS validation, 4-persona RBAC permission matrix.</td>
        <td>Conceptual diagram only</td>
      </tr>
      <tr>
        <td><code>crm-service :8002</code></td>
        <td><code>crm_leads</code>, <code>crm_contacts</code>, <code>crm_companies</code>, <code>crm_deals</code>, <code>crm_quotes</code>, <code>crm_activities</code></td>
        <td>Lead capture and scoring (0–100), atomic 1-click lead conversion, 6-stage Deals pipeline, quotations, <code>deal.won</code> event trigger.</td>
        <td>Proposed for Phase 1 (Months 1–3)</td>
      </tr>
      <tr>
        <td><code>marketing :8003</code></td>
        <td><code>mkt_campaigns</code>, <code>mkt_forms</code>, <code>mkt_utms</code></td>
        <td>Multi-channel campaign management, inbound webhook lead capture (<code>lead.captured</code>), UTM tracking, CAC and ROI calculation.</td>
        <td>Proposed for Phase 2 (Months 4–6)</td>
      </tr>
      <tr>
        <td><code>projects :8004</code></td>
        <td><code>prj_projects</code>, <code>prj_sprints</code>, <code>prj_tasks</code>, <code>prj_worklogs</code>, <code>prj_milestones</code></td>
        <td>Agile Sprint 44 Kanban board, backlog list view, story points, task inspector, time worklogs, GitHub/Figma/Honeycomb links.</td>
        <td>Proposed for Phase 1 (Months 1–3)</td>
      </tr>
      <tr>
        <td><code>hr-service :8005</code></td>
        <td><code>hr_employees</code>, <code>hr_departments</code>, <code>hr_attendance</code>, <code>hr_payroll_runs</code></td>
        <td>Employee directory, department hierarchy, ATS recruitment pipeline, attendance clock-in/out, automated monthly payroll runs.</td>
        <td>Proposed for Phase 2 (Months 4–6)</td>
      </tr>
      <tr>
        <td><code>finance :8006</code></td>
        <td><code>fin_invoices</code>, <code>fin_payments</code>, <code>fin_journal_entries</code>, <code>fin_journal_lines</code></td>
        <td>Net30 invoice generation, automated dunning, double-entry General Ledger (<code>debit == credit</code>), P&amp;L and Balance Sheet reporting.</td>
        <td>Proposed for Phases 1–2 (Months 1–6)</td>
      </tr>
      <tr>
        <td><code>inventory :8007</code></td>
        <td><code>inv_warehouses</code>, <code>inv_products</code>, <code>inv_stock_moves</code>, <code>inv_assets</code></td>
        <td>Multi-warehouse SKU catalog, stock movement ledger, low-stock threshold detection (<code>stock.low</code>), hardware asset lifecycle.</td>
        <td>Proposed for Phase 3 (Months 7–9)</td>
      </tr>
      <tr>
        <td><code>procurement :8008</code></td>
        <td><code>proc_vendors</code>, <code>proc_purchase_orders</code>, <code>proc_grns</code></td>
        <td>Vendor management, automated PO creation from low-stock triggers, Goods Received Notes (GRN), 3-Way Match validation.</td>
        <td>Proposed for Phase 3 (Months 7–9)</td>
      </tr>
      <tr>
        <td><code>support :8009</code></td>
        <td><code>sup_tickets</code>, <code>sup_sla_policies</code>, <code>sup_comments</code></td>
        <td>Customer support ticket lifecycle, priority routing, dynamic SLA countdown timers, breach detection, <code>ticket.urgent</code> escalation.</td>
        <td>Proposed for Phase 2 (Months 4–6)</td>
      </tr>
      <tr>
        <td><code>collab :8010</code></td>
        <td><code>collab_channels</code>, <code>collab_messages</code>, <code>collab_notifications</code></td>
        <td>Topic-based team channels (<code>#general</code>, <code>#deals</code>, <code>#engineering</code>), threaded messaging, user mentions, event broadcasts.</td>
        <td>Proposed for Phase 2 (Months 4–6)</td>
      </tr>
      <tr>
        <td><code>compliance :8011</code></td>
        <td><code>comp_audit_events</code>, <code>comp_controls</code>, <code>comp_dsar_requests</code>, <code>doc_files</code>, <code>doc_versions</code></td>
        <td>Versioned Document Cloud, SHA-256 cryptographic hash-chained audit log, SOC 2 Type II control checks, GDPR DSAR export.</td>
        <td>Proposed for Phase 3 (Months 7–9)</td>
      </tr>
      <tr>
        <td><code>automation :8012</code></td>
        <td><code>auto_rules</code>, <code>auto_executions</code></td>
        <td>Declarative <code>WHEN-IF-DO</code> workflow engine evaluating cross-service events with execution logging and retry handling.</td>
        <td>Proposed for Phase 3 (Months 7–9)</td>
      </tr>
      <tr>
        <td><code>ai-copilot :8013</code></td>
        <td><code>ai_queries</code>, <code>ai_anomalies</code>, <code>ai_forecasts</code></td>
        <td>Role-scoped natural-language query synthesis across CRM, Finance, Projects, and Inventory; anomaly detection and forecasting.</td>
        <td>Proposed for Phase 4 (Months 10–12)</td>
      </tr>
    </tbody>
  </table>

  <h2>5.0 End-to-End Cross-Domain Transaction Integrity</h2>
  <p>
    Whereas the baseline BMS specification describes cross-module workflows theoretically, STAT6 executes them deterministically in production. For example, when a sales representative marks a deal as <strong>Won</strong> in <code>crm-service (:8002)</code>:
  </p>
  <ol>
    <li><strong>Event Emission</strong>: <code>crm-service (:8002)</code> updates <code>crm_deals.stage = 'Won'</code> and dispatches a signed <code>deal.won</code> payload to the Central API Gateway Event Bus (<code>:8000</code>).</li>
    <li><strong>Automated Project Provisioning</strong>: <code>projects-service (:8004)</code> consumes the event and creates a linked delivery project in <code>prj_projects</code> along with onboarding sprint tasks in <code>prj_tasks</code>.</li>
    <li><strong>Automated Invoicing &amp; Double-Entry Ledger Posting</strong>: <code>finance-service (:8006)</code> generates a Net30 customer invoice in <code>fin_invoices</code> and posts a balanced journal entry in <code>fin_journal_entries</code> and <code>fin_journal_lines</code> (debiting Accounts Receivable and crediting Revenue).</li>
    <li><strong>Team Notification &amp; Cryptographic Audit</strong>: <code>collaboration-service (:8010)</code> broadcasts the contract win to the <code>#deals</code> channel, and <code>compliance-service (:8011)</code> appends a SHA-256 hash-chained audit record to <code>comp_audit_events</code>.</li>
  </ol>

  <h2>6.0 Frontend Engineering, UI Standards &amp; Verification Summary</h2>
  <p>
    Beyond backend architecture, STAT6 provides a complete enterprise user interface built with <strong>React 18.3, TypeScript 5.5, Vite 6, and Tailwind CSS 3.4</strong>, whereas the baseline specification includes no frontend implementation:
  </p>
  <ul>
    <li><strong>Information Density &amp; Readability</strong>: Enforces a structured enterprise layout with a dark navy navigation sidebar, high-contrast solid black (<code>#000000</code>) regular-weight data cells, vertical column dividers, and vector outline icons.</li>
    <li><strong>Interactive Operational Views</strong>: Includes full-bleed CRM Leads and Deals tables, an interactive Sprint 44 Kanban board with a slide-over task inspector, real-time financial ledger views, and a live 4-Persona RBAC switcher (<em>Super Admin</em>, <em>Finance Manager</em>, <em>Sales Rep</em>, <em>Project Lead</em>).</li>
    <li><strong>Production Verification &amp; Deployment Readiness</strong>: Backed by 11 automated verification suites passing <strong>67/67 assertions (100%)</strong> across all 14 microservices, and configured with root <code>vercel.json</code> routing rules for immediate cloud deployment.</li>
  </ul>

</body>
</html>"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_exe):
        edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    cmd_pdf = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_pdf}",
        html_file,
    ]
    subprocess.run(cmd_pdf, capture_output=True, text=True)

    if os.path.exists(html_file):
        try:
            os.remove(html_file)
        except Exception:
            pass

    print("Formal Black-and-White PDF Exists:", os.path.exists(output_pdf), os.path.getsize(output_pdf))


if __name__ == "__main__":
    generate_comparison_pdf()
