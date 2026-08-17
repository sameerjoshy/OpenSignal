# OpenSignal: Complete Product Requirements Document
## ZERO-COST BUILD EDITION

**Version:** 2.0 (ZERO-COST STACK)  
**Date:** August 14, 2026  
**Client:** GTM-360  
**Product:** OpenSignal - Signal-Based Demand Generation Platform  
**Status:** Ready for Development - ZERO INFRASTRUCTURE COSTS  
**Build Cost:** $0 (Bedrock free credits + free tier services)

---

## ZERO-COST TECH STACK AT A GLANCE

| Component | Technology | Cost | Notes |
|-----------|-----------|------|-------|
| **Frontend** | React 18 + Cloudflare Pages | $0 | Deploy to your existing GTM-360 account |
| **Backend** | FastAPI + Render.com | $0 | Free tier deployment |
| **Database** | Supabase (PostgreSQL) | $0 | 500MB free, plenty for MVP |
| **Cache** | Upstash Redis | $0 | 10K commands/day free tier |
| **LLM/AI** | AWS Bedrock Claude | $0 | Free credits ($100/month value) |
| **Email** | Mailgun | $0 | 1000 emails/month free |
| **Services** | Apollo, Hunter, etc. | $0 | All free tiers |
| **Code Repository** | GitHub | $0 | Private repos free |
| **Monitoring** | Sentry | $0 | Free tier |
| **Total Build Cost** | | **$0** | |

---

## TABLE OF CONTENTS

1. Executive Summary
2. Product Overview
3. Tech Stack & Architecture (UPDATED - ZERO-COST)
4. Database Schema
5. API Integrations
6. Design System & UI/UX
7. Feature Specifications (Detailed Screens)
8. User Flows & Interactions
9. Copy & Content Library
10. Hosting & Deployment Instructions (UPDATED - CLOUDFLARE + RENDER + SUPABASE + UPSTASH)
11. Setup Guide for Developers
12. Testing & QA Requirements
13. Acceptance Criteria

---

## 1. EXECUTIVE SUMMARY

**OpenSignal** is a signal-based demand generation platform that detects buying signals (job changes, funding, tech stack, intent), scores accounts intelligently, and orchestrates multi-channel campaigns. Users plug in their own paid subscriptions (6sense, Bombora, Hunter, etc.) or use free versions.

**Core Promise:** Replicate DemandFarm functionality at 1/10th the cost by being modular and letting users bring their own tools.

**Build Model:** Zero infrastructure costs during development. Uses free tiers of Cloudflare Pages, Render, Supabase, Upstash, and Bedrock.

**Target Users:**
- Bootstrapped founders (Pre-PMF to $500K ARR)
- Growth operators ($500K-$5M ARR)
- Revenue Ops teams ($5M+ ARR)

**MVP Scope:** 16 weeks  
**Core Features:** Signal detection, account scoring, campaign routing, email execution, CRM integration  
**Deployment:** SaaS on zero-cost tier (scales with revenue)  
**Pricing:** Free tier + $99/month Pro + $299/month Business

---

## 2. PRODUCT OVERVIEW

### 2.1 Product Vision

OpenSignal transforms how early-stage companies acquire customers by shifting from volume-based outreach to precision signal-based targeting. Users detect buying signals, score accounts intelligently, and execute campaigns through a unified dashboard—using their own tool subscriptions or free tiers.

### 2.2 Key Features (MVP)

1. **Service Onboarding Wizard** - Users select free or paid tiers for each service (Apollo, Hunter, Mailgun, HubSpot, etc.)
2. **Encrypted Credential Storage** - Securely store API keys for auto-login on future sessions
3. **Signal Detection Engine** - Detect job changes, funding, news, website intent from 5+ sources
4. **AI Account Scoring** - Bedrock Claude scores accounts by buying intent, assigns Tier 1/2/3
5. **Campaign Routing** - Auto-route campaigns by tier with multi-channel orchestration
6. **Email Generation** - Claude generates personalized emails per account
7. **Email Execution** - Send via user's Mailgun/SendGrid, track opens/clicks
8. **CRM Integration** - Auto-create leads/deals in HubSpot or Salesforce
9. **Dashboard & Analytics** - Real-time signals → campaigns → replies tracking
10. **Auto-Login** - Remember credentials, auto-login on return visits

### 2.3 User Personas

**Persona 1: Bootstrapped Founder (Sarah, 28)**
- $0-50K/month revenue
- 1-2 person team
- Budget: $0-200/month
- Pain: "I need customers but can't afford DemandFarm ($10K/month)"
- Solution: Use free tiers (Apollo, Hunter, Mailgun, HubSpot free, Bedrock free credits)
- Expected outcome: 50-100 signals/week, 5-10 qualified meetings/month

**Persona 2: Growth Operator (Marcus, 35)**
- $500K-$5M revenue
- 5-15 person team
- Budget: $200-1000/month
- Pain: "My tools don't talk to each other. I'm stitching signals manually"
- Solution: Connect 6sense + Hunter + SendGrid + HubSpot in OpenSignal
- Expected outcome: 200-500 signals/week, 20-50 meetings/month

**Persona 3: Revenue Ops (Jennifer, 40)**
- $5M+ revenue
- 30-50 person team
- Budget: $500-2000/month
- Pain: "How do I maximize ROI on my $50K/month tool stack?"
- Solution: Unified hub for orchestration + analytics
- Expected outcome: 1000+ signals/week, enterprise reporting

---

## 3. TECH STACK & ARCHITECTURE (ZERO-COST)

### 3.1 Technology Decisions (LOCKED IN - ZERO-COST)

| Layer | Technology | Cost | Why |
|-------|-----------|------|-----|
| **Frontend** | React 18 + TypeScript | $0 | Modern, type-safe, Cloudflare Pages free |
| **Frontend Hosting** | Cloudflare Pages | $0 | Deploy to GTM-360 account, unlimited requests |
| **Backend** | Python FastAPI | $0 | Async-native, high performance |
| **Backend Hosting** | Render.com free tier | $0 | Deploy FastAPI, auto-scales, free tier sufficient for MVP |
| **Database** | PostgreSQL (Supabase) | $0 | 500MB free, generous for MVP, built-in auth |
| **Authentication** | Supabase Auth | $0 | Built into Supabase, unlimited users free tier |
| **Cache/Queue** | Redis (Upstash) | $0 | 10K commands/day free, serverless, auto-scaling |
| **LLM/AI** | AWS Bedrock Claude | $0 | Free credits ($100/month value for 12 months) |
| **Email Service** | Mailgun | $0 | 1000 emails/month free tier |
| **Error Tracking** | Sentry | $0 | Free tier, 5000 events/month |
| **Domain** | Your existing domain | $0 | Use GTM-360 domain for subdomains |
| **SSL/TLS** | Cloudflare | $0 | Included in Cloudflare Pages |
| **Code Repository** | GitHub | $0 | Private repos free for up to 3 collaborators |

### 3.2 Architecture Diagram (ZERO-COST)

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (React + Cloudflare Pages)         │
│  ├─ Auth Pages (Signup, Login, Onboarding)              │
│  ├─ Dashboard (Signals, Campaigns, Tracking)            │
│  ├─ Campaign Builder                                    │
│  └─ Settings (Services, Account, Billing)              │
│  Deployed to: app.gtm-360.com                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS (Cloudflare)
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼──────────┐      ┌────────▼─────────┐
│  Render.com      │      │  Supabase Auth   │
│  FastAPI Backend │      │  (JWT tokens)    │
│  (python app)    │      │                  │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
    ┌────┴──────────────────────────┴────┐
    │                                     │
┌───▼──────────┐          ┌──────────────▼──┐
│ Auth Service │          │ Signal Detection │
│ - Login      │          │ - Apollo API     │
│ - Signup     │          │ - SEC Edgar API  │
│ - JWT        │          │ - NewsAPI        │
└──────────────┘          │ - GA4            │
                          │ - Bedrock Score  │
                          └──────┬───────────┘
                                 │
    ┌────────────────────────────┼────────────────────────┐
    │                            │                        │
┌───▼──────────┐    ┌───────────▼────┐    ┌────────────▼─┐
│ Email Engine │    │ CRM Sync        │    │ Analytics    │
│ - Generate   │    │ - HubSpot API   │    │ - Dashboard  │
│ - Send       │    │ - Salesforce API│    │ - Reporting  │
│ - Track      │    │ - Create Leads  │    │ - Metrics    │
└──────────────┘    └─────────────────┘    └──────────────┘
         │
    ┌────┴──────────────┐
    │                   │
┌───▼──────┐    ┌──────▼──────┐
│ Mailgun  │    │  Sendgrid   │
│ (Email)  │    │  (Email)    │
└──────────┘    └─────────────┘

Database Layer (Supabase):
┌────────────────────────────────────────┐
│      PostgreSQL Database               │
│      (500MB free tier)                 │
├────────────────────────────────────────┤
│ - users                                │
│ - service_credentials (encrypted)      │
│ - campaigns                            │
│ - signals                              │
│ - email_events                         │
│ - crm_syncs                            │
│ - analytics                            │
│ Built-in: Auth, Realtime, Vector DB   │
└────────────────────────────────────────┘

Cache Layer (Upstash):
┌────────────────────────────────────────┐
│      Redis (Serverless)                │
│      (10K commands/day free)           │
├────────────────────────────────────────┤
│ - Task queue (signal detection)        │
│ - Session cache                        │
│ - Rate limiting                        │
└────────────────────────────────────────┘

External Services (Free Tiers):
┌─────────────────────────────────────────┐
│  Apollo, Hunter, 6sense, SEC Edgar,    │
│  NewsAPI, GA4, Bedrock Claude          │
│  (All free tier + free credits)        │
└─────────────────────────────────────────┘
```

### 3.3 Deployment Model (ZERO-COST)

**Frontend Deployment:**
- Deploy React app to Cloudflare Pages via GitHub integration
- URL: `app.gtm-360.com` (or your subdomain)
- Auto-deploys on every push to main
- Free SSL/TLS via Cloudflare
- Unlimited requests, bandwidth

**Backend Deployment:**
- Deploy FastAPI to Render.com free tier
- URL: `api.gtm-360.com` (or api subdomain)
- Auto-deploys on every push to main
- Free tier includes: up to 750 compute hours/month, PostgreSQL database, Redis
- Scales automatically
- Sleep mode: Free tier services spin down after 15 mins of inactivity (restarted on next request)

**Database:**
- Supabase PostgreSQL (500MB free)
- Includes: Auth system, real-time subscriptions, vector embeddings
- Automated backups
- Vector storage for future embedding features

**Cache/Queue:**
- Upstash Redis serverless (10K commands/day free)
- No server management
- Global edge locations
- Perfect for background task queue (Celery)

### 3.4 Development & Staging Environments

**Development (Local):**
```
Frontend: npm start → http://localhost:3000
Backend: uvicorn → http://localhost:8000
Database: Supabase (dev project)
Redis: Upstash (dev project)
Bedrock: Free credits
```

**Staging (On Supabase/Render Free Tier):**
```
Frontend: staging.gtm-360.com (Cloudflare Pages)
Backend: staging-api.gtm-360.com (Render free tier)
Database: Supabase (staging project - separate)
Redis: Upstash (staging project - separate)
Monitoring: Sentry (free tier)
```

**Production (On Supabase/Render Free Tier Initially):**
```
Frontend: app.gtm-360.com (Cloudflare Pages)
Backend: api.gtm-360.com (Render free tier)
Database: Supabase (production project - separate)
Redis: Upstash (production project - separate)
Monitoring: Sentry (free tier → paid at scale)
```

---

## 4. DATABASE SCHEMA

See original PRD - schema is identical (works on any PostgreSQL)

---

## 5. API INTEGRATIONS

See original PRD - all integrations unchanged

---

## 6. DESIGN SYSTEM & UI/UX

See original PRD - design system unchanged

---

## 7. FEATURE SPECIFICATIONS (Detailed Screens)

See original PRD - all screen specs unchanged

---

## 8. USER FLOWS & INTERACTIONS

See original PRD - all flows unchanged

---

## 9. COPY & CONTENT LIBRARY

See original PRD - all copy unchanged

---

## 10. HOSTING & DEPLOYMENT INSTRUCTIONS (ZERO-COST)

### 10.1 Cloudflare Pages Deployment (Frontend)

**Prerequisites:**
- GitHub account (repo ready)
- Cloudflare account (with GTM-360 domain)
- React app built (npm run build)

**Step 1: Connect GitHub to Cloudflare Pages**

```bash
1. Go to Cloudflare Dashboard > Pages
2. Click "Create a project" > "Connect to Git"
3. Authorize GitHub account
4. Select opensignal repository
5. Click "Begin setup"
```

**Step 2: Configure Build Settings**

```
Project name: opensignal
Production branch: main
Framework preset: React
Build command: npm run build
Build output directory: build
Environment variables:
  REACT_APP_API_URL: https://api.gtm-360.com
  REACT_APP_ENVIRONMENT: production
```

**Step 3: Set Custom Domain**

```
1. Go to project > Custom domains
2. Add domain: app.gtm-360.com
3. Add CNAME record (Cloudflare provides)
4. SSL/TLS: Automatic via Cloudflare
```

**Step 4: Auto-Deploy**

```bash
git push origin main
# Cloudflare automatically builds and deploys
# Check progress: Cloudflare Dashboard > Pages > opensignal
```

**Access:**
- Live: https://app.gtm-360.com
- Preview: PR previews auto-deployed
- Rollback: Cloudflare Dashboard > Pages > Deployments

---

### 10.2 Render.com Deployment (Backend)

**Prerequisites:**
- GitHub account (repo ready)
- Render account (free tier)
- FastAPI app ready

**Step 1: Create Render Service**

```bash
1. Go to Render Dashboard > Create New > Web Service
2. Connect GitHub account & select opensignal repo
3. Configure:
   Name: opensignal-api
   Environment: Python 3.11
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
   Plan: Free
```

**Step 2: Set Environment Variables**

```
ENVIRONMENT=production
DATABASE_URL=postgresql://...@supabase-instance.supabase.co:5432/opensignal
REDIS_URL=redis://default:password@upstash-endpoint.upstash.io:6379
BEDROCK_REGION=us-east-1
JWT_SECRET=your-long-random-secret-here
CORS_ORIGINS=https://app.gtm-360.com
APOLLO_API_KEY=your-key
HUNTER_API_KEY=your-key
MAILGUN_API_KEY=your-key
MAILGUN_DOMAIN=mail.gtm-360.com
NEWSAPI_KEY=your-key
```

**Step 3: Configure Custom Domain**

```bash
1. Go to Render service > Settings > Custom Domain
2. Add: api.gtm-360.com
3. Add CNAME record to Cloudflare DNS
4. SSL: Automatic via Render
```

**Step 4: Deploy**

```bash
git push origin main
# Render automatically deploys
# Check logs: Render Dashboard > opensignal-api > Logs
```

**Important: Free Tier Behavior**

```
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- 750 compute hours/month = enough for MVP (continuous = ~31 days)
- Upgrade to paid tier ($7/month) for no spin-down

For MVP: Free tier is fine. Users expect slight delay on cold start.
```

---

### 10.3 Supabase Setup (Database + Auth)

**Step 1: Create Supabase Project**

```bash
1. Go to supabase.com > Sign up
2. Create new project: opensignal
3. Region: Choose closest to you (us-east-1 recommended)
4. Generate strong database password
5. Create project (takes ~2 min)
```

**Step 2: Get Connection Details**

```
From Supabase Project Settings:
Database URL: postgresql://postgres:PASSWORD@db.supabase.co:5432/postgres
Anon Key (for client): <your-anon-key>
Service Role Key (for server): <your-service-role-key>
API URL: https://your-project.supabase.co
```

**Step 3: Run Database Migrations**

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link project
supabase link --project-ref your-project-ref

# Apply migrations
supabase db push

# Or via direct SQL:
# Copy database schema from Section 4 (Database Schema)
# Paste into Supabase SQL editor
# Execute
```

**Step 4: Enable Auth**

```
1. Go to Supabase > Authentication > Providers
2. Email/Password: Enable
3. Configure:
   - Email confirmations: Enabled (for signup verification)
   - SMTP: Use default (emails from noreply@supabase.io)
   - Redirect URL: https://app.gtm-360.com/auth/callback
```

**Step 5: Enable Row Level Security (RLS)**

```sql
-- Each table should have RLS enabled
-- Example for users table:
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access own data"
  ON users
  FOR ALL
  USING (auth.uid() = id);
```

---

### 10.4 Upstash Redis Setup (Cache & Queue)

**Step 1: Create Redis Database**

```bash
1. Go to upstash.com > Sign up (free)
2. Create database: opensignal
3. Region: us-east-1 (closest to your app)
4. Type: Redis (Serverless)
```

**Step 2: Get Connection Details**

```
From Upstash Console:
Redis URL: redis://default:PASSWORD@host:port
Also copy for environment variables:
REDIS_HOST=host
REDIS_PORT=port
REDIS_PASSWORD=password
```

**Step 3: Configure Celery (Task Queue)**

```python
# In FastAPI app
from celery import Celery
import os

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    "opensignal",
    broker=redis_url,
    backend=redis_url
)

# Tasks automatically queue in Redis
```

**Free Tier Limits:**
- 10K commands per day free
- Plenty for MVP (signal detection = ~100 commands/campaign)
- Scales automatically

---

### 10.5 GitHub Repository Setup

**Step 1: Initialize Repo**

```bash
git init
git add .
git commit -m "Initial commit: OpenSignal MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/opensignal.git
git push -u origin main
```

**Step 2: Folder Structure**

```
opensignal/
├── frontend/                    # React app
│   ├── src/
│   ├── package.json
│   └── .env.example
├── backend/                     # FastAPI app
│   ├── app/
│   ├── requirements.txt
│   ├── main.py
│   └── .env.example
├── .github/
│   └── workflows/
│       ├── deploy-frontend.yml  # Auto-deploy to Cloudflare
│       └── deploy-backend.yml   # Auto-deploy to Render
├── docker-compose.yml           # Local development
├── .gitignore
└── README.md
```

**Step 3: GitHub Actions (Optional - Auto-Deploy)**

```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend to Cloudflare

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install && npm run build
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: opensignal
          directory: frontend/build
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to Render

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Render Deploy
        run: |
          curl -X POST \
            -H "Content-Type: application/json" \
            https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_DEPLOY_KEY }}
```

---

## 11. SETUP GUIDE FOR DEVELOPERS

### 11.1 Prerequisites

- Python 3.11+
- Node 18+
- GitHub account
- Cloudflare account (with GTM-360 domain)
- Render account
- Supabase account
- Upstash account

### 11.2 Local Development Setup

**Step 1: Clone & Install Backend**

```bash
git clone https://github.com/YOUR_USERNAME/opensignal.git
cd opensignal/backend

# Setup Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your values:
# DATABASE_URL=postgresql://...@supabase.co:5432/postgres
# REDIS_URL=redis://...@upstash.io
# JWT_SECRET=generate-random-string
# BEDROCK_REGION=us-east-1
# AWS_ACCESS_KEY_ID=xxx (from AWS)
# AWS_SECRET_ACCESS_KEY=xxx (from AWS)
```

**Step 2: Setup Database**

```bash
# Run migrations
alembic upgrade head

# Or seed with test data (optional)
python scripts/seed_db.py
```

**Step 3: Setup Frontend**

```bash
cd ../frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local:
# REACT_APP_API_URL=http://localhost:8000
# REACT_APP_ENVIRONMENT=development
```

**Step 4: Run Services**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Terminal 2 (Celery Worker - optional, for background tasks):
```bash
cd backend
source venv/bin/activate
celery -A tasks worker -l info
```

Terminal 3 (Frontend):
```bash
cd frontend
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 11.3 Environment Variables Explained

**Backend (.env)**

```
# Database (from Supabase)
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres

# Cache (from Upstash)
REDIS_URL=redis://default:password@host:port

# JWT Secret (generate with: openssl rand -base64 32)
JWT_SECRET=your-256-bit-secret-here

# AWS Bedrock
BEDROCK_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# CORS (origins that can call API)
CORS_ORIGINS=http://localhost:3000,https://app.gtm-360.com

# Service API Keys
APOLLO_API_KEY=your-api-key
HUNTER_API_KEY=your-api-key
MAILGUN_API_KEY=your-api-key
MAILGUN_DOMAIN=mail.gtm-360.com
NEWSAPI_KEY=your-api-key

# Environment
ENVIRONMENT=development|staging|production
LOG_LEVEL=debug|info|warning|error
```

**Frontend (.env.local)**

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

### 11.4 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "feat: add signal detection for job changes"

# Push to remote
git push origin feature/my-feature

# Create PR on GitHub
# → Review
# → Merge to main

# Auto-deploys:
# - Frontend to Cloudflare Pages
# - Backend to Render
```

### 11.5 Project Structure

```
opensignal/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration
│   ├── requirements.txt         # Python dependencies
│   ├── app/
│   │   ├── auth/              # Authentication routes
│   │   ├── services/          # Service integrations
│   │   ├── signals/           # Signal detection logic
│   │   ├── campaigns/         # Campaign logic
│   │   ├── email/             # Email handling
│   │   ├── crm/               # CRM integrations
│   │   └── analytics/         # Analytics
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── crud.py            # Database operations
│   │   └── schemas.py         # Pydantic schemas
│   ├── migrations/            # Alembic migrations
│   ├── tasks/                 # Celery tasks
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utilities
│   │   ├── styles/            # Global styles
│   │   └── App.tsx            # Main app
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── docker-compose.yml         # Local dev environment
├── .env.example
├── .gitignore
└── README.md
```

---

## 12. TESTING & QA REQUIREMENTS

### 12.1 Test Structure

```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_signals.py
│   ├── test_campaigns.py
│   └── test_email.py
├── integration/
│   ├── test_campaign_flow.py
│   └── test_crm_sync.py
└── e2e/
    └── test_complete_workflow.py
```

### 12.2 Run Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Coverage
pytest tests/ --cov=app/
```

### 12.3 QA Checklist

**Authentication:**
- [ ] Signup form validates input correctly
- [ ] Email verification works
- [ ] Login persists session
- [ ] Logout clears session
- [ ] Password reset email works

**Service Integration:**
- [ ] Apollo API connects and returns data
- [ ] Hunter API finds emails successfully
- [ ] Mailgun can send test email
- [ ] HubSpot can create test contact
- [ ] Bedrock Claude returns valid JSON

**Campaign Flow:**
- [ ] Can create campaign with company list
- [ ] Signal detection completes without errors
- [ ] Signals are scored correctly (0-100)
- [ ] Emails are generated with proper personalization
- [ ] Emails send via Mailgun successfully
- [ ] Mailgun webhooks track opens/clicks
- [ ] CRM sync creates leads in HubSpot

**Dashboard:**
- [ ] Metrics update in real-time
- [ ] Campaign list shows correct status
- [ ] Filtering works (by tier, status, date)
- [ ] Export to CSV works
- [ ] Search functionality works

**UI/UX:**
- [ ] All forms are responsive
- [ ] All buttons have hover states
- [ ] Loading states appear appropriately
- [ ] Error messages are clear
- [ ] Mobile layout is usable

---

## 13. ACCEPTANCE CRITERIA

### MVP Launch Criteria

The product is ready to launch when:

1. **Authentication Works**
   - Users can signup, verify email, login
   - Credentials stored securely (AES-256 encrypted)
   - JWT tokens issued and validated
   - Sessions persist across browser reload

2. **Service Integration Works**
   - At least 3 services can be connected (Apollo, Hunter, Mailgun)
   - Credentials tested and validated on save
   - Fallback services work if primary unavailable
   - All services show quota/usage info

3. **Signal Detection Works**
   - Signals detected from 5 sources (Apollo, SEC Edgar, NewsAPI, GA4, Manual)
   - Bedrock Claude scores accounts (0-100)
   - Accounts assigned tiers (Tier 1/2/3) correctly
   - Dashboard shows real-time signal count

4. **Campaign Execution Works**
   - Campaigns created from company list (CSV or paste)
   - Emails generated per account (Claude personalization)
   - Emails sent via Mailgun/SendGrid
   - Opens/clicks tracked via webhooks
   - Email events logged to database

5. **CRM Sync Works**
   - Leads created in HubSpot/Salesforce
   - Contacts linked to campaigns
   - Deal data syncs correctly
   - Sync errors logged and visible to user

6. **Dashboard Works**
   - Real-time metrics (signals, campaigns, emails, replies)
   - Campaign list with filtering/sorting
   - Account detail view with history
   - Analytics view with conversion funnel

7. **Reliability**
   - 99% uptime during normal hours
   - No data loss on crashes
   - All errors logged to Sentry
   - Graceful degradation if service fails

8. **Security**
   - Credentials encrypted at rest (AES-256)
   - No credentials logged or exposed
   - JWT tokens validated on all requests
   - CORS configured properly
   - Rate limiting on API endpoints

9. **Performance**
   - Dashboard loads in <3 seconds
   - Campaign creation completes in <90 seconds
   - Email sends in real-time
   - Database queries use proper indexes

10. **Documentation**
    - API documentation generated (Swagger)
    - Setup guide for developers complete
    - Deployment instructions clear
    - README covers basic usage

---

## ZERO-COST PRICING SUMMARY

| Service | Free Tier | Cost | Notes |
|---------|-----------|------|-------|
| Cloudflare Pages | Unlimited | $0 | Auto-deploys, unlimited bandwidth |
| Render | 750 hrs/month | $0 | Spin-down after 15 min (acceptable for MVP) |
| Supabase | 500MB storage | $0 | Plenty for MVP, upgrade later |
| Upstash | 10K commands/day | $0 | 10K commands ≈ 100+ campaigns/day |
| Bedrock | Free credits | $0 | $100/month value for 12 months |
| Mailgun | 1000 emails/month | $0 | Perfect for MVP |
| Apollo | 50 searches/month | $0 | Free tier sufficient |
| Hunter | 50 searches/month | $0 | Free tier sufficient |
| NewsAPI | 100 req/day | $0 | Free tier sufficient |
| SEC Edgar | Unlimited | $0 | Public API |
| GA4 | Unlimited | $0 | Free tier |
| **Total Monthly Cost** | | **$0** | Scale incrementally as revenue grows |

---

## SCALING PATH (When Revenue Grows)

**At $10K/month revenue:**
- Upgrade Render to paid ($7/month) - eliminate cold start delays
- Keep everything else on free tier

**At $50K/month revenue:**
- Upgrade Supabase to $25/month (2GB storage)
- Upgrade Upstash to $25/month (10x throughput)
- Render: still $7/month
- Total infra: ~$57/month

**At $250K+/month revenue:**
- Move to AWS RDS for database ($300-800/month)
- Move to AWS ElastiCache for Redis ($50-100/month)
- Keep Cloudflare Pages ($0)
- Move backend to AWS ECS ($600+/month)
- Total infra: ~$1,000-2,000/month
- Infra cost = 0.4-0.8% of revenue (healthy)

---

## FINAL NOTES FOR DEVELOPMENT

**This document is production-ready for zero-cost build.**

**MVP Timeline:** 16 weeks  
**Infrastructure Cost:** $0 (dev phase)  
**Scaling Cost:** Gradual, tied to revenue growth  
**Build Cost:** Only time  

**Next Steps:**
1. Set up GitHub repo
2. Set up Supabase project
3. Set up Render account
4. Set up Upstash Redis
5. Set up Cloudflare Pages
6. Clone repo and start development
7. Deploy to staging (free tier)
8. Deploy to production (free tier)

**All services:**
- Auto-scale to handle growth
- Free tier → paid tier upgrade path
- Zero lock-in (can migrate anytime)
- Can be fully operational before spending a dollar

---

**Version:** 2.0 (ZERO-COST STACK)  
**Last Updated:** August 14, 2026  
**Status:** READY FOR DEVELOPMENT - ZERO INFRASTRUCTURE COSTS

This document is ready to paste into OpenCode. All sections updated for Cloudflare Pages, Render, Supabase, and Upstash deployment. No changes needed to database schema, API integrations, design system, or feature specifications from the original PRD.
