# STAT6 — Enterprise Business Management & Microservices Platform

STAT6 is a high-density, multi-tenant enterprise business management system replacing legacy monolithic ERP/CRM stacks with a modern, high-throughput distributed microservices architecture.

---

## Architecture Overview

STAT6 runs across **14 autonomous microservices** connected through a Central API Gateway and asynchronous event mesh:

| Microservice | Port | Domain Responsibilities |
| :--- | :--- | :--- |
| **API Gateway** | `8000` | Central reverse proxy, distributed omnisearch, event bus relay |
| **Auth Service** | `8001` | Tenant onboarding, JWT issue/verify, RBAC permissions |
| **CRM Service** | `8002` | Leads, contacts, deals pipeline, quotes, lead conversion |
| **Marketing Service** | `8003` | Inbound web forms, campaign tracking, blended ROI |
| **Projects Service** | `8004` | Sprints, Jira Kanban board, time worklogs, project budgets |
| **HR Service** | `8005` | Employee directory, attendance clock, monthly payroll runs |
| **Finance Service** | `8006` | Net30 invoicing, payment settlement, double-entry ledger |
| **Inventory Service** | `8007` | Multi-warehouse stock tracking, stock.low threshold triggers |
| **Procurement Service** | `8008` | Automated PO drafting, GRN intake, 3-way matching validation |
| **Support Service** | `8009` | SLA countdown timers, ticket triage, auto-escalations |
| **Collaboration Service** | `8010` | Real-time multi-channel chat (`#general`, `#engineering`, `#deals`) |
| **Compliance Service** | `8011` | Immutable audit trail, GDPR subject exports, SOC 2 readiness |
| **Automation Service** | `8012` | Declarative WHEN-IF-DO event workflow engine |
| **AI Copilot Service** | `8013` | Cross-microservice NLP synthesis, anomaly alerts |

---

## Cloud Database Integration (Supabase)

STAT6 natively connects to **Supabase PostgreSQL** (`aws-0-eu-central-1.pooler.supabase.com:6543/postgres`).
All 52 relational tables across all 14 microservices are partitioned and provisioned in the cloud database.

---

## Instant Vercel Deployment

This repository is pre-configured with `vercel.json` for one-click deployment on **Vercel**:

1. Import this repository into [Vercel](https://vercel.com/new).
2. **Framework Preset**: Vite (detected automatically).
3. **Build Command**: `cd frontend && npm install && npm run build` (configured in `vercel.json`).
4. **Output Directory**: `frontend/dist`.
5. *(Optional)* Add the environment variable `VITE_API_BASE` pointing to your deployed backend API gateway.
6. Click **Deploy**.

---

## Local Development Quickstart

### Prerequisites
- Node.js 18+ & npm
- Python 3.10+

### 1. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### 2. Run Backend Microservices
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/dev_orchestrator.py
```
Central API Gateway will be live at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.
