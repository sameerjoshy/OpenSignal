# OpenSignal: Complete Refinements & Outcomes Spec
**For OpenCode Implementation**  
**Date:** August 19, 2026  
**Version:** 1.0 - Ready for Build  

---

## EXECUTIVE SUMMARY: WHAT OUTCOMES DOES OPENSIGNAL DRIVE?

OpenSignal transforms demand generation by shifting from spray-and-pray outreach to **precision signal-based targeting**. Here's the value:

### **PRIMARY OUTCOMES (What Users Get)**

**1. Pipeline Generation**
- **Detect** high-intent buying signals automatically (job changes, funding, tech stack shifts, website behavior)
- **Convert** signals into qualified accounts (AI scores each one 0-100)
- **Result:** 5-10 new qualified accounts/week → 20-50 meetings/month → $500K-$2M pipeline

**2. Time Saved**
- Reps spend 15+ hours/week on manual research (LinkedIn stalking, company research, email hunting)
- OpenSignal automates 80% of this
- **Result:** 12-15 hours/week back per rep = $60K-$120K/year in labor freed

**3. Response Rate Improvement**
- Industry average outbound reply rate: 2-3%
- OpenSignal users (signal-based + AI personalization): 4-6%
- **Result:** 2x-3x better engagement without more volume

**4. Cost Per Acquisition (CPA) Reduction**
- Traditional outbound: $50-$200 per qualified meeting
- OpenSignal (using free tools): $5-$15 per meeting
- **Result:** 10x cheaper customer acquisition

**5. Conversion Velocity**
- Sales reps close faster when they target buying signals
- Average deal cycle: 30% faster (90 days → 60 days)
- **Result:** Revenue pulled forward by 1-2 months annually

**6. Predictive Intelligence**
- Know which accounts will likely buy (Stage 1, 2, 3)
- Know which are at churn risk (existing customers)
- Know the ideal contact within the buying committee
- **Result:** Reps spend 3x more time on winnable deals

---

### **SECONDARY OUTCOMES (Platform Benefits)**

- **Competitive Intelligence:** See what signals competitors are detecting
- **Trend Analysis:** Know which technologies are trending in your ICP
- **Hiring Intelligence:** Track team changes, promotions, departures
- **Funding Intelligence:** Real-time tracking of funding rounds
- **Intent Intelligence:** Website traffic = buying signals

---

## HOME PAGE DESIGN: LEAD WITH OUTCOMES

### **Above the Fold (Hero Section)**

**Headline:** "5,000+ Signals. 100+ Hot Leads. In One Week."

**Subheading:** "AI-powered signal detection finds accounts actively buying. Then we do the work for you."

**Visual:** 
- 3-column flow graphic:
  ```
  [SIGNALS DETECTED] 
  "5,200 signals found" (job changes, funding, tech)
  
  [ACCOUNTS SCORED]
  "340 high-intent accounts" (AI scores 0-100)
  
  [CAMPAIGNS LAUNCHED]
  "24 hot replies this week" (auto-personalized emails)
  ```

**CTA Button:** "Start Free (2 min setup)"

---

### **Key Metrics Section (Below Hero)**

**What You Get in Week 1:**

| Metric | Value | Timeframe |
|--------|-------|-----------|
| 🔍 Signals Detected | 1,000+ | Per week |
| 🎯 High-Intent Accounts | 50-100 | Per week |
| 📧 Personalized Emails | Auto-sent | Daily |
| 💬 Hot Replies | 5-10 | Per week |
| ⏱️ Time Saved | 12+ hours | Per rep/week |
| 💰 Cost Per Meeting | $5-$15 | Down from $50-$200 |

---

### **How It Works Section (Carousel/Timeline)**

**Step 1: Detect** 
"Connect your signal sources (free: Apollo, Hunter, NewsAPI, GA4). We automatically detect job changes, funding, website visits, tech stack changes."

**Step 2: Score**
"AI analyzes each signal and scores accounts 0-100. Tier 1 = hot, Tier 2 = warm, Tier 3 = cold."

**Step 3: Campaign**
"Auto-generate personalized emails. Send to the right person at the right time. Track opens, clicks, replies in real-time."

**Step 4: Close**
"Know when to follow up. Get buying stage predictions. Track deal velocity."

---

### **Social Proof Section**

**Case Studies (add real numbers once users exist):**
- "SaaS Founder: 50 signals → 10 qualified meetings → $120K pipeline in 4 weeks"
- "Growth Operator: Scaled outbound from 1 to 5 reps without hiring sales ops"
- "RevOps: Unified 6 different tools into 1 workflow, cut martech spend by 40%"

---

### **Pricing Section**
```
FREE TIER
- 50 signals/day
- 3 campaigns
- Email only
- Basic reporting
→ Perfect for founders

PRO ($99/month)
- 500 signals/day
- Unlimited campaigns
- Multi-channel (email + SMS + LinkedIn)
- Advanced reporting
- API access

BUSINESS ($299/month)
- Unlimited signals
- Custom integrations
- Dedicated onboarding
- SSO
- Omnichannel orchestration
```

---

## DETAILED REFINEMENTS SPEC FOR OPENCODE

---

## **PHASE 1: WORLD-CLASS UI/UX (Weeks 1-2)**

### **1.1 Dashboard 2.0 - Context-First Design**

**Current State:** Generic dashboard with campaign list  
**Target State:** Exec summary that tells a story at a glance

**Layout (Desktop):**
```
┌─────────────────────────────────────────────────────────┐
│  OPENSIGNAL DASHBOARD                    [Settings] [👤]  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  THIS WEEK'S PERFORMANCE                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │                                                    │   │
│  │  🔥 HOT SIGNALS THIS WEEK                        │   │
│  │  ┌─────────────┬─────────────┬─────────────┐    │   │
│  │  │ Stripe      │ Figma       │ Notion      │    │   │
│  │  │ VP Growth   │ Hired CRO   │ $92M Funded │    │   │
│  │  │ hired       │ job posting │ Series D    │    │   │
│  │  │ 🎯 Tier 1   │ 🎯 Tier 1   │ 🎯 Tier 1   │    │   │
│  │  └─────────────┴─────────────┴─────────────┘    │   │
│  │                                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  CAMPAIGN PERFORMANCE                                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                                                    │   │
│  │  Sent: 340 | Opened: 48 (14%) | Clicked: 12 (3.5%)  │
│  │  Replied: 6 (1.8%) | Demos Booked: 2               │   │
│  │                                                    │   │
│  │  [Bar chart: daily opens/clicks/replies]           │   │
│  │                                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  AI RECOMMENDATIONS                                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 💡 "Try subject line with company name - gets  │   │
│  │    2x opens"                                      │   │
│  │ 💡 "Follow up with John at Stripe - 72 hrs    │   │
│  │    since click"                                   │   │
│  │ 💡 "Tech stack match: 8 companies now using   │   │
│  │    Kubernetes - add to Tier 1"                   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  PIPELINE FORECAST                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Signals Detected: 1,200 | Accounts Scored: 340  │   │
│  │ On track for $500K revenue this month ↑ 40%    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

**Design Specs:**
- **Cards:** Larger, cleaner cards (not cramped)
- **Colors:** Navy (#001A4D) for primary, Purple (#6B5FFF) for CTAs, Light Purple (#7C3AED) for highlights
- **Typography:** System font (SF Pro Display on Mac, Segoe UI on Windows)
- **Icons:** Lucide React icons (🔥 hot, 🎯 tier, 💡 insight, 📈 trend)
- **Mobile:** Responsive stacking (1 col on mobile, 3 col on desktop)

**Key Components to Build:**

1. **Hot Signals Card**
   ```
   Props: signals (array of recent detected signals)
   Render: 3-5 cards showing company + signal type + tier
   Interaction: Click company → see all signals + account page
   Animation: Fade in as signals arrive (real-time via WebSocket)
   ```

2. **Campaign Performance Widget**
   ```
   Props: campaigns (array), metrics (open/click/reply rates)
   Render: Waterfall chart (signals → emails → opens → clicks → replies)
   Chart library: Recharts (bar + line hybrid)
   Interaction: Hover = tooltip shows actual numbers
   ```

3. **AI Recommendations Carousel**
   ```
   Props: recommendations (array of AI-generated tips)
   Render: Scrollable cards (swipe on mobile, arrow on desktop)
   Each card: Icon + title + description + "Apply" button
   Interaction: Click "Apply" → auto-implement suggestion
   ```

4. **Pipeline Forecast**
   ```
   Props: quarterly_projection (revenue, deal count)
   Render: Current MoM progress + projected end of month
   Visual: Circular progress bar (40% filled = 40% through month)
   Text: "On track for $500K revenue (↑ 40% vs last month)"
   ```

---

### **1.2 One-Click Campaign Launch**

**Current Flow:**
1. Upload prospect list
2. Select signal type
3. Choose email template
4. Configure timing
5. Review settings
6. Launch

**New Flow (One-Click):**
1. Upload prospect list → AI auto-detects company + role
2. Hit "🚀 Launch" → Done (everything auto-configured)

**Implementation:**

```
UPLOAD SCREEN (Simplified)
┌───────────────────────────────┐
│  UPLOAD YOUR PROSPECT LIST    │
│  ┌──────────────────────────┐ │
│  │ Drag CSV/Excel here      │ │
│  └──────────────────────────┘ │
│                               │
│  [Preview: "Sarah, Stripe"]   │
│  [Preview: "John, Figma"]     │
│  [Preview: "Jane, Notion"]    │
│                               │
│  ⚡ Auto-Detection:           │
│  ✅ Detected 50 companies    │
│  ✅ Enriched emails (48/50)  │
│  ✅ Scored intent (all Tier1) │
│                               │
│         [🚀 LAUNCH NOW]       │
│                               │
│  Powered by AI Magic          │
└───────────────────────────────┘
```

**Backend Logic:**
- Parse CSV → extract company names
- Call Apollo Search API → find contacts at those companies
- Call Apollo Enrichment API → get emails
- Call DeepSeek → score each account (0-100) + assign tier
- Auto-select email template based on industry + tier
- Schedule sends for optimal times (Tue-Thu, 10am-2pm)
- Send all emails in 1 background job (Celery)
- Return campaign ID + tracking URL

---

### **1.3 Campaign Replay Timeline**

**Visual:** Interactive timeline showing campaign evolution

```
CAMPAIGN: "Stripe Campaign #1"
Timeline View (Bottom to Top = Oldest to Newest)

[👥 50 prospects uploaded]
├─ Jan 15, 9:00 AM
│
├─ [📧 50 emails sent]
├─ Jan 15, 9:30 AM
│
├─ [👁️ 12 opened (24%)]
├─ [👆 3 clicked (6%)]
├─ Jan 16, 10:45 AM
│
├─ [💬 2 replied (4%)]
├─ "Hi Sarah, interested in..." - John @ Stripe
├─ "Thanks for reaching out..." - Emma @ Stripe
├─ Jan 17, 2:15 PM
│
├─ [📞 1 scheduled demo]
├─ John @ Stripe - Demo with Sarah - Jan 20, 2pm
├─ Jan 18, 11:30 AM
│
├─ [✅ 1 deal created in HubSpot]
├─ $50K opportunity - Stripe - John @ Stripe
├─ Jan 20, 4:30 PM

METRICS OVERLAY
Total: 50 sent | 24% open | 6% click | 4% reply | 2% demo
Tier 1: 40 (50% reply) | Tier 2: 8 (12% reply) | Tier 3: 2 (0% reply)
```

**Design:**
- Vertical timeline (mobile-optimized)
- Color-coded events (green = positive, blue = neutral, red = issues)
- Click each event → see details + drill into accounts
- "Optimize" button → AI suggestions based on this campaign's performance

---

### **1.4 Account Intelligence Cards**

**One page per account with everything you need to know:**

```
┌─────────────────────────────────────────────────────┐
│  STRIPE                                  [← Back]   │
│  ┌──────────────────────────────────────────────┐  │
│  │ [Stripe Logo] San Francisco, CA              │  │
│  │ Payment Processing | Series K | $14B raised  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  BUYING SIGNALS (Last 30 Days)                     │
│  🔴 [High Intent] VP Growth hired (5 days ago)    │
│  🔴 [High Intent] Raised $500M Series K (10 days) │
│  🟡 [Medium] Tech stack: added Kubernetes (12)    │
│  🟡 [Medium] Website traffic up 40% (15 days)     │
│                                                     │
│  BEST PERSON TO CONTACT                           │
│  ┌──────────────────────────────────────────────┐  │
│  │ Sarah Chen                                    │  │
│  │ Chief Marketing Officer                      │  │
│  │ sarah.chen@stripe.com | (415) 555-1234      │  │
│  │ 📈 Open rate: 45% | Click rate: 12%         │  │
│  │ ⭐ AI Confidence: 95%                         │  │
│  │ [Send Email] [View Profile]                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  OTHER STAKEHOLDERS                                │
│  • John Do, VP Growth (hired 5 days ago)          │
│  • Jane Smith, CRO (new contact)                   │
│  • Mike Johnson, VP Sales (existing contact)       │
│                                                     │
│  EMAIL TEMPLATES THAT WORK FOR THIS ACCOUNT       │
│  • "Congratulations on the Series K..." (6% reply) │
│  • "We help companies like Stripe scale..." (4%)   │
│  • "Your team just grew..." (8% reply)             │
│                                                     │
│  CAMPAIGN HISTORY                                  │
│  ✅ Sent email to Sarah (Jan 15) → Opened (Jan 16) │
│  ❌ Sent email to John (Jan 18) → No open (yet)   │
│  ✅ Demo booked with Sarah (Jan 20)                │
│                                                     │
│  DEAL STATUS (if existing customer)                │
│  $50K Deal | Sales Stage: Negotiation | +30 days   │
│  Last activity: 3 days ago (email from John)       │
│  ⚠️ Churn Risk: Low (engagement: high)             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components to Build:**

1. **Buying Signals Tag Cloud**
   ```
   - Red (High): Job changes, funding, major website change
   - Yellow (Medium): Tech stack, team growth, web traffic
   - Gray (Low): News mentions, generic events
   - Animation: Fade in as signals arrive
   ```

2. **Contact Card**
   ```
   - Photo (pull from LinkedIn via Apollo)
   - Name, title, email, phone
   - Stats: open/click/reply rates for this person
   - AI confidence score (0-100)
   - Actions: [Send Email] [View Profile] [Add to Campaign]
   ```

3. **Email Template Recommendations**
   ```
   - Show top 3 templates sorted by reply rate
   - Each shows: title, snippet, reply rate %, apply button
   - Powered by: historical performance + signal matching
   ```

4. **Campaign Timeline (Account-specific)**
   ```
   - Show all campaigns sent to this account
   - Status: sent, opened, clicked, replied, demo booked
   - Dates and content
   - Interaction: click = see full email + response
   ```

---

### **1.5 Mobile Optimization**

**Home Screen (Mobile):**
```
┌──────────────────────┐
│ 🔥 HOT LEADS         │
│ 5 accounts this week │
│ [→ View All]         │
├──────────────────────┤
│ 📊 THIS WEEK         │
│ 340 signals detected │
│ 24 emails opened     │
│ 6 replies received   │
├──────────────────────┤
│ 💡 NEXT STEP         │
│ Follow up with Sarah │
│ @ Stripe - 72 hrs    │
│ [Send Email] [Skip]  │
├──────────────────────┤
│ [New Campaign] [+]   │
└──────────────────────┘
```

**Key Interactions:**
- Swipe campaigns to left = archive
- Swipe signals to right = add to account
- Long-press contact = quick reply
- Shake device = get AI recommendation (fun easter egg)

---

## **PHASE 2: OUTCOMES DASHBOARD & REPORTING (Week 3)**

### **2.1 Main Outcomes Dashboard**

**Purpose:** Show users exactly what revenue/meetings OpenSignal has driven

**Layout:**

```
┌──────────────────────────────────────────────────────┐
│  OUTCOMES & IMPACT                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  PIPELINE GENERATED                                 │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  $500,000  ← Total pipeline value from signals │ │
│  │                                                 │ │
│  │  Signals: 5,200 → Accounts: 340 → Deals: 6   │ │
│  │  Conversion rate: 0.11% → Revenue potential   │ │
│  │                                                 │ │
│  │  [Pie chart breakdown by signal type]          │ │
│  │  - Job changes: $200K (40%)                    │ │
│  │  - Funding: $180K (36%)                        │ │
│  │  - Web traffic: $80K (16%)                     │ │
│  │  - Tech stack: $40K (8%)                       │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  TIME SAVED                                         │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  312 hours  ← Total researcher time freed     │ │
│  │  @ $40/hour = $12,480 in labor recovered      │ │
│  │                                                 │ │
│  │  Per rep: 12 hours/week × 26 weeks = 312 hrs │ │
│  │                                                 │ │
│  │  [Timeline showing hours saved per week]       │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  ENGAGEMENT LIFT                                    │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  Industry Average: 2.5% reply rate             │ │
│  │  Your Campaigns:  5.2% reply rate (+108%)      │ │
│  │                                                 │ │
│  │  Your 340 emails → 18 replies                  │ │
│  │  Industry average would be: 9 replies          │ │
│  │  You're getting 2x engagement ✨               │ │
│  │                                                 │ │
│  │  [Comparison chart: industry vs you]           │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  COST PER ACQUISITION                               │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  Cost Per Meeting:      $12  (vs industry $75) │ │
│  │  Cost Per Opportunity:  $84  (vs industry $400)│ │
│  │  Cost Savings:          86%  ← Annual savings  │ │
│  │                                                 │ │
│  │  [ROI badge: "Your $0 spend = $500K pipeline"] │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
│  FORECAST                                           │
│  ┌────────────────────────────────────────────────┐ │
│  │                                                 │ │
│  │  Current Month Projection: $850,000           │ │
│  │  (↑ $350K from this week's 5 hot signals)    │ │
│  │                                                 │ │
│  │  Quarterly Projection: $2.4M                  │ │
│  │  (↑ 185% vs last quarter if signal trend holds) │ │
│  │                                                 │ │
│  │  [Line chart: monthly pipeline trend]         │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Key Metrics to Track:**

1. **Pipeline Generated**
   - Total deal value from accounts detected via OpenSignal
   - Breakdown by signal type (job changes, funding, etc.)
   - Breakdown by tier (Tier 1, 2, 3)
   - Breakdown by vertical/industry

2. **Time Saved**
   - Hours spent doing manual research (form field at signup)
   - Hours saved by automation = hours_per_campaign × campaigns_run
   - Labor value = hours_saved × avg_salary / 2000

3. **Engagement Metrics**
   - Reply rate vs industry benchmark (2.5%)
   - Open rate vs industry benchmark (12-15%)
   - Click rate vs industry benchmark (2-3%)
   - Demo booking rate

4. **Cost Metrics**
   - Cost per qualified meeting (total emails sent / meetings booked)
   - Cost per opportunity (total emails / deals created)
   - ROI (revenue generated / platform cost = revenue / $0 = ∞)

5. **Forecast**
   - MoM growth rate
   - Projected annual revenue based on current signals
   - Confidence level (based on historical conversion rates)

---

### **2.2 Export & Sharing**

**Features:**
- Export dashboard to PDF → email to CEO/board
- Share dashboard link → read-only view for stakeholders
- Schedule weekly email with top metrics
- Connect to Slack → daily standup bot with metrics

---

## **PHASE 3: LEARNING ENGINE (Week 4)**

### **3.1 Auto-Optimization Loop**

**What the app learns:**

1. **Email Template Performance**
   ```
   Track per template:
   - Subject line: which keywords get opened? ("company name" +2x, numbers +1.5x, urgency -0.5x)
   - Body copy: which CTAs get clicked? ("Let's chat" +1.2x, "Learn more" +0.8x)
   - Timing: when do people open? (Tue 10am +1.8x, Thu 2pm +1.5x)
   - Length: is long-form better or short? (Measure time-to-reply)
   
   Auto-suggestion to user:
   "Subject lines with [company name] get 2x opens. Apply this to your next campaign?"
   [Yes] [No] [Learn more]
   ```

2. **Account Fit Scoring**
   ```
   Measure per account attribute:
   - Company size: which range converts best? (100-500 emp = 5% reply)
   - Industry: which verticals? (Fintech = 6%, SaaS = 4%, Enterprise = 2%)
   - Growth stage: funded > bootstrapped > public
   - Tech stack: companies using X convert faster
   
   Auto-suggestion:
   "Companies with 100-500 employees in Fintech reply 40% faster.
   Add 150 companies to your next campaign?"
   [Add] [View list] [No thanks]
   ```

3. **Timing Optimization**
   ```
   Measure:
   - Best day of week to send (histogram)
   - Best time of day (histogram)
   - Day-to-open distribution (how long until they open?)
   - Day-to-reply distribution (how long until they respond?)
   
   Auto-suggestion:
   "Send on Tuesdays at 10am: 40% open rate
   Your current: Mondays at 9am (28% open rate)
   Reschedule your next 50 emails?"
   [Reschedule] [Keep current] [Explain]
   ```

4. **Contact Fit Scoring**
   ```
   Measure per contact attribute:
   - Job title: which titles reply fastest? (VP Growth = 8%, Founder = 6%, SDR = 1%)
   - Seniority: do higher/lower titles convert? (C-suite = faster reply, lower urgency)
   - Company tenure: new hires vs tenured (new hire signals = higher reply)
   - Historical engagement: past emails to this person?
   
   Auto-suggestion:
   "VPs of Growth reply 3x faster than other roles.
   Prioritize 5 VP Growth roles in your next campaign?"
   [Prioritize] [No] [Learn more]
   ```

---

### **3.2 AI Auto-Suggestions UI**

**Where to show:** Dashboard cards + inline in workflow

```
┌─────────────────────────────────────┐
│  💡 AI RECOMMENDATIONS              │
│  ┌─────────────────────────────────┐│
│  │ 1. Subject line with [Company]  ││
│  │    gets 2x opens                ││
│  │    [Apply to Next Campaign]     ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ 2. Target VPs of Growth first   ││
│  │    They reply 3x faster         ││
│  │    [Add VPs to Campaign]        ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ 3. Send on Tuesdays at 10am     ││
│  │    Your best performing time    ││
│  │    [Reschedule Campaign]        ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ 4. Follow up with Sarah (Stripe)││
│  │    72 hours since she clicked   ││
│  │    [Send Follow-up]             ││
│  └─────────────────────────────────┘│
│                                      │
│  [Dismiss] [Save for Later] [⋮ More] │
└─────────────────────────────────────┘
```

---

### **3.3 A/B Testing**

**Auto-run experiments:**

```
Backend:
- Split new campaigns 50/50
- Test A: current best template
- Test B: suggested variation
- Track: open rate, click rate, reply rate, conversion

Auto-winner selection:
- After 50 emails per variant, pick winner
- Auto-use winner for remaining emails
- Notify user: "Variant B won! 12% better open rate"

UI:
- Show A/B test results in campaign view
- "Variant A: 35% open | Variant B: 42% open ✅ Winner"
- [Use Winner] [See Both] [Run Another]
```

---

## **PHASE 4: BACKEND ENHANCEMENTS**

### **4.1 Apollo Integration (Search + Enrichment)**

**Code Location:** `backend/app/services/apollo_service.py`

```python
# Two functions to implement:

1. search_contacts(company_name: str, titles: list, limit: int = 10) -> list
   - Call Apollo Search API
   - Filter by company + job titles
   - Return: [{ id, email, phone, first_name, last_name, title, company_name, linkedin_url }]
   - Cache results 30 days (Upstash)
   - Track API calls (alert at 45/50)

2. enrich_contact(email: str) -> dict
   - Call Apollo Enrichment/Match API
   - Input: just email
   - Return: { phone, title, company_name, company_size, raised, industry, linkedin_url }
   - Cache results 30 days
   - Track API calls

Integration points:
- Signal detection: When NewsAPI finds "Stripe hired VP Growth"
  → Call search_contacts("Stripe", ["CMO", "VP Sales", "CRO"])
  → Store results in database
  
- Email reply: When email reply received
  → Extract sender email
  → Call enrich_contact(sender_email)
  → Update contact record with enriched data
```

---

### **4.2 Agentic Automation (Email Replies)**

**What:** Auto-respond to email replies intelligently

```
Workflow:
1. Mailgun webhook → email reply received
2. Extract: sender email, subject, body
3. Route to DeepSeek:
   "Email reply from [name@company.com]
    Subject: [subject]
    Body: [body]
    
    Is this a:
    A) Hot lead (wants to buy) → Flag for sales rep
    B) Not interested → Mark as lost
    C) Follow-up question → Generate auto-response
    D) Out of office → Note for later
    
    If C, generate response that:
    - Answers their question
    - Moves conversation forward
    - Includes next step
    - Uses company tone"

4. If Hot: Create notification + alert rep + create CRM task
5. If C: Send auto-response + notify rep
6. If B/D: Tag for manual review

Implementation:
- API endpoint: POST /webhooks/mailgun
- Parse email + send to DeepSeek
- Auto-respond if low-risk
- All high-confidence replies go to rep first
- Learn from manual corrections
```

---

### **4.3 Real-Time Metrics Engine**

**Current:** Dashboard data is stale (loads once at page load)  
**Target:** Real-time updates via WebSocket

```
Backend (FastAPI):
- Create WebSocket endpoint: /ws/metrics
- Every campaign send → broadcast to all connected clients
- Every email open (via Mailgun webhook) → broadcast
- Every email reply → broadcast
- Every demo booked (via CRM sync) → broadcast
- Every score updated → broadcast

Frontend (React):
- Connect to WebSocket on component mount
- Listen for metric events
- Auto-update dashboard cards with animation
- Show "live" badge when metrics updating

UI Animation:
- Card glows briefly when metric updates
- Number animates from old → new value (1.2s)
- If major change (+50%): show celebration animation
```

---

### **4.4 CRM Integration (HubSpot + Salesforce)**

**What:** Auto-create leads/contacts/deals in CRM when signals detected

```
HubSpot Integration:
- Trigger: Account scored + reaches Tier 1
- Action: Create contact + company in HubSpot
- Data: name, email, phone, company_name, industry, deal_size_estimate
- Create associated deal: title=company, amount=$5K-$50K based on tier

Salesforce Integration:
- Same workflow, use Salesforce REST API
- Create account + contact + opportunity
- Associate with user account

Sync bidirectional:
- Update in OpenSignal → update in CRM
- Update in CRM → update in OpenSignal (don't create duplicates)

Implementation:
- backend/app/services/hubspot_service.py
- backend/app/services/salesforce_service.py
- Async job: every 15 min, sync changes both ways
```

---

### **4.5 Omnichannel Foundation (Ready for Phase 3)**

**Current:** Email only  
**Future:** SMS + Slack + LinkedIn

```
Preparation:
- Add channel preferences to database:
  campaigns.channels = ["email", "sms", "slack"]
  
- Add channel templates:
  email_templates, sms_templates, slack_templates (same tables, different channel)
  
- Add channel credentials:
  service_credentials can now store SMS API keys (Twilio), Slack tokens, LinkedIn keys
  
- Add channel tracking:
  email_events table structure reusable for sms_events, slack_events, linkedin_events
  
- Add channel orchestration logic (backend/app/services/orchestration.py):
  def route_campaign(account, tier) -> list[channel]:
      if tier == 1: return ["email", "sms", "linkedin"]
      if tier == 2: return ["email", "slack"]
      if tier == 3: return ["email"]

Implementation (Phase 3):
- Add Twilio SMS integration
- Add Slack API integration  
- Add LinkedIn Campaign Manager integration
- Update campaign builder to select channels
```

---

## **PHASE 5: LEARNING & ANALYTICS (Week 4 Continued)**

### **5.1 Learning Dashboard**

**Where users see what the app has learned about them:**

```
┌─────────────────────────────────────────────────────┐
│  WHAT WE'VE LEARNED ABOUT YOUR ICP                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  TOP CONVERTING ACCOUNTS                           │
│  ┌───────────────────────────────────────────────┐ │
│  │ Company Size: 100-500 employees (+240% reply) │ │
│  │ Industry: Fintech, SaaS, Media                │ │
│  │ Funding: Series A-C                           │ │
│  │ Growth: "hiring" & "funding" signals best     │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  TOP CONVERTING PEOPLE                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ Titles: VP Growth, VP Sales, CRO (+150%)      │ │
│  │ Seniority: VP > Director > Manager            │ │
│  │ Tenure: < 1 year at company (+80% reply)     │ │
│  │ Companies: recent hires reply fastest         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  TOP CONVERTING SIGNALS                            │
│  ┌───────────────────────────────────────────────┐ │
│  │ #1: New VP hired (8.2% reply rate)            │ │
│  │ #2: Company funded (6.1% reply rate)          │ │
│  │ #3: Tech stack change (4.3% reply rate)       │ │
│  │ #4: High web traffic (3.8% reply rate)        │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  TOP CONVERTING EMAIL TACTICS                      │
│  ┌───────────────────────────────────────────────┐ │
│  │ Subject: Include company name (+240% opens)   │ │
│  │ Length: 50-75 words (best reply rate)          │ │
│  │ CTA: "Let's chat" beats "Learn more" (+25%)  │ │
│  │ Timing: Tuesday 10-11am (highest opens)      │ │
│  │ Follow-up: Day 5 + Day 12 (optimal sequence)  │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  YOUR ICP PROFILE                                  │
│  Based on: 50 campaigns, 1,200 emails, 65 replies │
│  Confidence: 87%                                   │
│  [Export ICP] [Share with Team]                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Data to Calculate:**

1. **Top Converting Account Attributes**
   ```
   For each campaign:
   - Track: company size, industry, stage, signals
   - Measure: reply rate, demo rate
   - Group by attribute value
   - Rank: sort by conversion lift (your rate / baseline)
   
   Query:
   SELECT 
     company_size,
     COUNT(*) as total_sent,
     SUM(CASE WHEN replied THEN 1 ELSE 0 END) as replies,
     ROUND(SUM(CASE WHEN replied THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as reply_rate
   FROM campaign_accounts
   WHERE sent_at > now() - interval '90 days'
   GROUP BY company_size
   ORDER BY reply_rate DESC
   ```

2. **Top Converting People Attributes**
   ```
   Same as above but by contact attributes:
   - job_title, seniority, tenure_at_company, etc.
   ```

3. **Signal Type Performance**
   ```
   SELECT 
     signal_type,
     COUNT(*) as total,
     SUM(CASE WHEN replied THEN 1 ELSE 0 END) as replies,
     ROUND(AVG(account_score), 0) as avg_score
   FROM signals
   JOIN campaign_accounts ON signals.account_id = campaign_accounts.account_id
   WHERE created_at > now() - interval '90 days'
   GROUP BY signal_type
   ORDER BY (SUM(CASE WHEN replied THEN 1 ELSE 0 END) / COUNT(*)) DESC
   ```

4. **Email Performance Analysis**
   ```
   Track per email template:
   - Subject line words → which appear in high-open emails?
   - Body length → word count vs open/reply rate
   - CTA type → which CTAs win?
   - Send time → day of week + hour
   - Results: open_rate, click_rate, reply_rate
   ```

---

### **5.2 Weekly Learning Email**

**Auto-send to user every Friday:**

```
Subject: "Your Week in Signals: 5 New Insights 🔍"

Hi Sarah,

This week, your signals detected 240 accounts and drove 18 replies.
Here's what we learned:

📊 TOP INSIGHT:
Companies with 200-500 employees reply 3x faster than others.
Your top 10 accounts by this metric: [list]
→ Suggest: Add 50 more companies in this size range to next campaign?

🎯 NEXT BEST ACTION:
Follow up with Sarah @ Stripe - she clicked your email 72 hours ago
Email open 48hr ago, click 24hr ago. Now is prime time to follow up.
→ [Send Follow-up Now]

🚀 SIGNAL TREND:
Job change signals are your best performer (8.2% reply).
Noticed: 5 new VP Growth hires at your target accounts this week.
→ [Launch Campaign for VPs]

💡 EMAIL TACTIC:
Subject lines with "[Company Name]" get 240% more opens.
You used company names in 40% of emails - try 80%?
→ [Use AI to Rewrite Subject Lines]

📈 FORECAST:
On pace for $450K pipeline this month (↑35% vs last month).
Keep this signal trend going and you'll hit $500K.

[View Full Analytics] [Share with Team] [Adjust Preferences]

Happy selling,
OpenSignal Team
```

---

## **SUCCESS METRICS: HOW TO MEASURE**

### **Primary KPIs**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Pipeline Generated** | $100K/month | Sum of deal values from OpenSignal-sourced accounts |
| **Time Saved** | 10+ hrs/week/rep | Qualitative (survey) + quantitative (usage tracking) |
| **Reply Rate** | 4-6% | (replies / emails sent) × 100 |
| **Demo Booking Rate** | 1-2% | (demos booked / emails sent) × 100 |
| **Cost Per Demo** | <$20 | (platform cost / demos booked) |
| **User Retention** | >60% month-over-month | Active users this month / last month |
| **NPS** | >50 | Survey after 30 days |

### **Secondary Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Signal Detection Accuracy** | >90% | Manual review of signals for false positives |
| **Email Open Rate** | 15-20% | Mailgun webhook tracking |
| **Click-Through Rate** | 3-5% | Link clicks in email |
| **CRM Sync Success** | >95% | Leads successfully created in HubSpot/Salesforce |
| **API Uptime** | >99.5% | Monitoring (Sentry) |
| **Page Load Time** | <2s | Lighthouse scores |
| **Feature Usage** | >80% using 3+ features | Product analytics |

---

## **DELIVERABLES FOR OPENCODE**

**Files to create/update:**

1. **Backend:**
   - `backend/app/services/apollo_service.py` (Search + Enrichment)
   - `backend/app/services/email_agent.py` (Agentic email responses)
   - `backend/app/services/learning_engine.py` (Track + suggest optimizations)
   - `backend/app/services/orchestration.py` (Multi-channel ready)
   - `backend/app/models.py` (Add learning + recommendation tables)
   - `backend/app/api/metrics.py` (Outcomes dashboard endpoints)
   - `backend/app/api/websocket.py` (Real-time metrics)

2. **Frontend:**
   - `frontend/src/pages/Dashboard2.tsx` (New dashboard with hot signals)
   - `frontend/src/components/CampaignLaunch.tsx` (One-click launch)
   - `frontend/src/components/CampaignTimeline.tsx` (Replay timeline)
   - `frontend/src/components/AccountCard.tsx` (Account intelligence)
   - `frontend/src/pages/OutcomesPage.tsx` (Metrics + impact dashboard)
   - `frontend/src/pages/LearningPage.tsx` (What we learned)
   - `frontend/src/pages/HomePage.tsx` (Hero + outcomes-focused home)
   - `frontend/src/hooks/useMetricsWebSocket.ts` (Real-time metrics)

3. **Database:**
   - `supabase/migrations/002_add_learning.sql` (Learning tables)
   - `supabase/migrations/003_add_outcomes.sql` (Outcome tracking tables)

4. **Documentation:**
   - `OPENCODE_BRIEFING.md` (This entire spec)
   - `API_INTEGRATION_GUIDE.md` (Apollo, Mailgun, DeepSeek integration details)
   - `DEPLOYMENT_CHECKLIST.md` (Step-by-step deployment guide)

---

## **PHASED ROLLOUT**

| Phase | Timeline | Focus | Owner |
|-------|----------|-------|-------|
| Phase 1 | Week 1-2 | World-class UI/UX | OpenCode |
| Phase 2 | Week 3 | Outcomes Dashboard | OpenCode |
| Phase 3 | Week 4 | Learning Engine | OpenCode |
| Phase 4 | Week 5+ | Omnichannel + Advanced | OpenCode + Sameer |

---

## **END OF SPEC**

**This is the complete briefing for OpenCode to build OpenSignal into a category-defining demand generation platform.**

**Key principles:**
- Lead with outcomes (not features)
- Design for daily use (not monthly)
- Automate everything possible (learning loop is critical)
- Make it beautiful (UI/UX is the differentiator)
- Free tier forever (users start free, upgrade when they see value)

Ready to ship. 🚀

