# OKR Creator: Best-in-Class UI/UX Design System

## THE ADOPTION PROBLEM (Why Most OKR Tools Fail)

**Lattice Problem:** 
- 5 menu options before users even start
- Cascading selector feels academic
- Multiple modals for one action
- Users think: "This is complex. We'll use spreadsheets."

**Our Approach:**
- **One entry point:** "Create OKR" (that's it)
- **Progressive disclosure:** Show guidance only when needed
- **B2C simplicity:** Notion-like minimalism + Slack-like delight
- **Enterprise credibility:** Serious, professional, trustworthy
- **Friction-free:** Every screen has ONE clear action

---

## DESIGN PRINCIPLES

### 1. **Ruthless Simplification**
- One action per screen when possible
- Hide complexity until needed
- No dead-end flows
- Every input has a reason (visible to user)

### 2. **Progressive Disclosure**
- Start with 3 fields (objective + 2 KRs)
- Add more only when user needs
- Help panels appear on-demand (not forced)
- Examples show, don't explain

### 3. **Contextual Guidance**
- Guidance appears next to input (not popup)
- B2C principle: "Show, don't tell"
- Learning embedded in workflow (not docs)
- Real-time validation without errors

### 4. **B2C Delight + Enterprise Credibility**
- Smooth animations (Figma-like)
- Clear data hierarchy
- Professional color palette
- Micro-interactions that feel alive

### 5. **Adoption-First**
- 3-minute onboarding (not 30-minute tutorial)
- "Good defaults" over customization
- Mobile-responsive (planning on-the-go)
- Works offline (progressive Web App)

---

## DESIGN SYSTEM TOKENS

### Color Palette

**Primary (Trust & Action):**
- Blue-600: #2563eb (primary action, highlights)
- Blue-50: #eff6ff (backgrounds)

**Secondary (Confidence & Positivity):**
- Green-600: #16a34a (success, achieved)
- Green-50: #f0fdf4

**Caution (Alert & Risk):**
- Amber-600: #d97706 (warnings, at-risk)
- Amber-50: #fffbeb

**Danger (Critical):**
- Red-600: #dc2626 (blockers, failures)
- Red-50: #fef2f2

**Neutral (Content & Structure):**
- Gray-900: #111827 (headings)
- Gray-700: #374151 (body text)
- Gray-500: #6b7280 (secondary text)
- Gray-300: #d1d5db (borders)
- Gray-50: #f9fafb (surfaces)

**Gradients (Emotional Storytelling):**
- Success: Linear green-500 → green-600
- Warning: Linear amber-400 → amber-600
- Risk: Linear red-400 → red-600

### Typography

**Headlines:**
- H1: 32px, weight 700, color gray-900 (page titles)
- H2: 24px, weight 600, color gray-900 (section titles)
- H3: 18px, weight 600, color gray-900 (subsection titles)

**Body:**
- Body: 16px, weight 400, line-height 1.5, color gray-700
- Small: 14px, weight 400, color gray-600
- Tiny: 12px, weight 500, color gray-500 (labels, badges)

**Mono (Data):**
- Family: SF Mono / Monaco / Courier New
- Used for: Numbers, formulas, code snippets

### Spacing

- 2px, 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- **Card padding:** 24px
- **Section gap:** 32px
- **Section padding:** 48px

### Components

**Buttons:**
- Primary: Blue-600 bg, white text, 8px rounded, 12px vertical padding
- Secondary: Gray-100 bg, gray-700 text, 8px rounded
- Tertiary: No background, blue-600 text, underline on hover
- Icon: 24px square, gray-400 on hover

**Inputs:**
- 12px padding, gray-300 border, 8px rounded
- Focus: blue-500 border (2px), shadow-sm
- Label: 12px gray-600, above input
- Error state: Red border, red-600 text below
- Help text: 12px gray-500, below input

**Cards:**
- White background, gray-100 border (1px), 8px rounded
- 24px padding
- Hover: subtle gray-50 background shift

**Badges:**
- 6px vertical, 12px horizontal padding, 6px rounded
- Status colors (green/amber/red/blue)
- Font: 12px weight 600

### Shadows

- Subtle: 0 1px 2px rgba(0,0,0,0.05)
- Card: 0 1px 3px rgba(0,0,0,0.1)
- Hover: 0 4px 6px rgba(0,0,0,0.1)
- Modal: 0 20px 25px rgba(0,0,0,0.1)

### Animations

- Transition duration: 150ms (fast)
- Easing: cubic-bezier(0.4, 0, 0.2, 1)
- Page transitions: Fade in 300ms
- Micro-interactions: Bounce, scale, color shift

---

## KEY SCREENS: WIREFRAMES & FLOWS

### SCREEN 1: Dashboard (Entry Point)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  OKR Creator                                    Q4 2024    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │  Company Goal: Grow Revenue 30%                     │  │
│  │  Target: $10M new revenue                           │  │
│  │                                                      │  │
│  │  ████████░░ 65% (Company OKR Progress)              │  │
│  │                                                      │  │
│  │  Status:                                             │  │
│  │  ✓ Sales $10M     ████░░░░░░ 70%                   │  │
│  │  ✓ Marketing 20k  ██████░░░░ 60%                   │  │
│  │  ✓ Product Ret.   ███████░░░ 70%                   │  │
│  │  ✓ Finance CAC    ████████░░ 75%                   │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [+ Create OKR]  [View All]  [Grading Mode]               │
│                                                             │
│  Weekly Check-In Reminders:                               │
│  ┌─────────────────────┐  ┌─────────────────────┐        │
│  │ Your Team (4 OKRs)  │  │ Sales Team (3)      │        │
│  │ Due: Today          │  │ Due: Tomorrow       │        │
│  │ 2 of 4 complete     │  │ 0 of 3 complete     │        │
│  └─────────────────────┘  └─────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

KEY PRINCIPLES:
- Status at a glance (no drilling)
- One clear action: "+ Create OKR"
- Reminders built-in (no notifications needed)
- Color coding (green=on track, amber=at risk, red=blocked)
```

---

### SCREEN 2: Create OKR (The Magic Screen)

**Phase 1: ONE input field**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Create OKR for: Q4 2024                        [Cancel]   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ What do you want to achieve?                        │  │
│  │                                                      │  │
│  │ [_____________________________________]             │  │
│  │                                                      │  │
│  │ Type like this:                                      │  │
│  │ "Increase qualified leads by 40%"                   │  │
│  │ "Improve retention from 85% to 90%"                 │  │
│  │                                                      │  │
│  │                                  [Next]             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

INTERACTION:
- As they type: Real-time validation appears below
- ✓ Looks like an outcome (good)
- ⚠ This might be too vague, add target
- Suggest: "Increase qualified leads from 1k to 1.4k/month"
```

**Phase 2: Add Key Results**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Objective: "Increase qualified leads by 40%"      [Edit]  │
│                                                             │
│  Key Results (2-4):                                        │
│                                                             │
│  1. [_______________________]  current: ___  target: ___  │
│     What's the first measure?                             │
│                                                             │
│  2. [_______________________]  current: ___  target: ___  │
│     What else proves success?                             │
│                                                             │
│  [+ Add Another KR]                                        │
│                                                             │
│                                    [Back]  [Next]          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

INTERACTIONS:
- Placeholder text guides ("What's the first measure?")
- Smart parsing: "1000 leads" → baseline, "1400" → target
- Real-time validation: All KRs measurable? ✓
- One at a time (not overwhelming)
```

**Phase 3: Set Confidence & Link**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Objective: "Increase qualified leads by 40%"              │
│  KRs: (all filled in, shown as summary)                   │
│                                                             │
│  How confident are you? (0-100%)                          │
│  ◄─────●────────────────────────────► (at 70%)            │
│  60%         70% (recommended)         90%                 │
│                                                             │
│  Why 70%?                                                   │
│  "Ambitious target. Requires new tactics.                  │
│   Your team usually achieves 75% on 70% goals. Smart."    │
│                                                             │
│  This ladders to:                                          │
│  Company Goal: Grow Revenue 30%                           │
│  ✓ Automatically linked (no work needed)                   │
│                                                             │
│  Add enablement context? (optional)                        │
│  "Why are we doing this?" [Show examples]                 │
│                                                             │
│                                    [Back]  [Create]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

SMART DEFAULTS:
- Default confidence: 70% (best practice anchor)
- Auto-linked to parent (no cascading selector hell)
- Enablement optional (not forced)
```

**Phase 4: Success (No Modal)**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ✓ OKR Created!                                            │
│                                                             │
│  Objective: "Increase qualified leads by 40%"              │
│  Confidence: 70%                                           │
│  Ladder to: Company Goal (Revenue)                        │
│                                                             │
│  What's next?                                              │
│  [+ Add Another OKR]  [Invite Team]  [View OKR]           │
│                                                             │
│  Tip: Invite your team to add their OKRs                  │
│       by EOD Friday. We'll show you the                    │
│       alignment map.                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

NO FRICTION:
- No "please wait" spinner
- Instant feedback (perceived speed)
- Clear next step (what to do now?)
```

---

### SCREEN 3: Weekly Check-In (Lightweight)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Weekly Check-In: Week 3 of Q4                            │
│                                                             │
│  Your OKRs (3):                                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Increase qualified leads by 40%                     │  │
│  │                                                      │  │
│  │ Status:  ⦿ On Track    ○ At Risk    ○ Off Track   │  │
│  │                                                      │  │
│  │ Progress: ███████░░░░░ 55% (target: 70% by now)   │  │
│  │                                                      │  │
│  │ Confidence: Still 70%?  ⦿ Yes  ○ Lower  ○ Higher  │  │
│  │                                                      │  │
│  │ Any blockers?                                        │  │
│  │ [_________________________________]                  │  │
│  │                                                      │  │
│  │ What's your top priority this week?                 │  │
│  │ [_________________________________]                  │  │
│  │                                                      │  │
│  │                                    [Save]           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [2 more OKRs...]                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Time: 10 minutes for 3 OKRs                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

WHY THIS WORKS:
- One card per OKR (visual clarity)
- Radio buttons (not dropdowns)
- 4 simple fields per OKR
- Time estimate shown (10 minutes total)
- Card-based layout = mobile ready
```

---

### SCREEN 4: Grading Mode (Quarter End)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Grade Your OKRs: Q4 2024                                 │
│  (Results locked 24 hours after quarter ends)             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Increase qualified leads by 40%                     │  │
│  │ Your confidence: 70%                                │  │
│  │ Actual achievement: ??%                             │  │
│  │                                                      │  │
│  │ What did you achieve?                               │  │
│  │ Baseline: 1,000 leads/month                         │  │
│  │ Target: 1,400 leads/month                           │  │
│  │ Actual: [_______] leads/month                       │  │
│  │                                                      │  │
│  │ → Score: 0.65 (65% of target = partial success)    │  │
│  │                                                      │  │
│  │ What did you learn?                                 │  │
│  │ [_____________________________________]             │  │
│  │ (Be honest. This isn't about blame.)                │  │
│  │                                                      │  │
│  │ Confidence vs Actual:                               │  │
│  │ You set 70% confidence and achieved 65%.            │  │
│  │ ✓ Good! This is expected with ambitious goals.      │  │
│  │                                                      │  │
│  │                                    [Save & Next]    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Progress: 1 of 3 OKRs graded                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

PSYCHOLOGY:
- Shows score automatically (no guessing)
- Validates learning (not just punishment)
- Confidence comparison (shows they did well at ambitious target)
- One at a time (not overwhelming)
```

---

### SCREEN 5: Org Dashboard (CEO View)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Q4 2024: OKR Rollup & Health                             │
│                                                             │
│  Company Goal: Grow Revenue 30%                            │
│  ████████░░ 65% Achieved                                   │
│                                                             │
│  Department Breakdown:                                      │
│  ┌────────────────────┬──────────┬──────────┬────────────┐  │
│  │ Department         │ Status   │ Progress │ Confidence │  │
│  ├────────────────────┼──────────┼──────────┼────────────┤  │
│  │ Sales              │ ✓ Track  │ 70%      │ 75%        │  │
│  │ Marketing          │ ⚠ Risk   │ 60%      │ 70%        │  │
│  │ Product            │ ✓ Track  │ 70%      │ 80%        │  │
│  │ Finance            │ ✓ Track  │ 75%      │ 85%        │  │
│  └────────────────────┴──────────┴──────────┴────────────┘  │
│                                                             │
│  Org Health Signals:                                       │
│  ┌─────────────────┬─────────────────┬─────────────────┐  │
│  │ Confidence Dist │ Dependency Met  │ Gaming Flags    │  │
│  │ 70%: 60% ✓      │ 85% confirmed   │ 0 alerts ✓      │  │
│  │ 80%: 35% ✓      │ 15% uncertain   │ Clean slate     │  │
│  │ 90%: 5% ⚠       │                 │                 │  │
│  └─────────────────┴─────────────────┴─────────────────┘  │
│                                                             │
│  Blockers (Top 3):                                         │
│  1. ⚠ Marketing needs Product feature (3 days old)        │  │
│  2. ⚠ Engineering capacity tight (2 days old)             │  │
│  3. → Finance working on CAC data (resolved)              │  │
│                                                             │
│  Actions:                                                   │
│  [Review All OKRs]  [Check Blockers]  [Gaming Report]     │  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

EXEC SUMMARY:
- One glance: Health is good
- Colored status (green/amber/red)
- Blockers visible (no surprises)
- No drilling needed (everything at top level)
```

---

## ADOPTION BARRIER REMOVAL

### What KILLS Adoption:

| Problem | Example | Impact |
|---------|---------|--------|
| **Too many steps** | 7 clicks to create OKR | Users abandon |
| **Cascading hell** | Dropdown selector for 50 parent OKRs | Analysis paralysis |
| **Jargon** | "Set confidence in OKR lifecycle" | "What does this mean?" |
| **No examples** | Blank form | No idea what to write |
| **Forced fields** | 10 mandatory inputs | "This is too much" |
| **Slow feedback** | No validation until submit | Wasted time |
| **Mobile-hostile** | Requires large screen | Can't use on phone |
| **Academic feeling** | "Goal Cycle", "Key Metric" | Feels like homework |

### What ACCELERATES Adoption:

| Solution | How | Result |
|----------|-----|--------|
| **One-action entry** | "Create OKR" button only | Users know what to do |
| **Auto-linking** | System links to parent | No cascading selector |
| **Plain English** | "How confident?" not "confidence score" | Understood immediately |
| **Live examples** | "Like this: ..." inline | Users know format |
| **Progressive disclosure** | Start with 3 fields, add more | Not overwhelming |
| **Real-time validation** | Checks as you type | Instant feedback |
| **Mobile-first** | Works great on phone | Planning anywhere |
| **Casual language** | "What do you want to achieve?" | Feels like conversation |

---

## INTERACTION PATTERNS (Micro-Interactions)

### Pattern 1: Input Validation (Real-Time)

**As user types objective:**
```
"Improve sales..."
⚠ This might be vague. What's your target?

"Improve sales by 30%"
✓ Looks like an outcome. Good.

"Improve sales by 30%..."
[User is typing...]
🤔 [system waiting]

"Improve sales by 30% through enterprise expansion"
✓ This is clear and measurable. Ready to add KRs.
```

**Animation:** Validation message fades in/out (not jarring)

---

### Pattern 2: Progressive Disclosure (Show → Hide → Show)

```
Step 1: Just the objective
[Objective input]

Step 2: Now KRs
[Objective - filled]
[KR 1 input]
[KR 2 input]
[+ Add another]

Step 3: Now confidence + context
[Objective - filled]
[KR 1, 2, 3 - filled - summarized]
[Confidence slider]
[Context panel - optional]

Step 4: Summary
[Everything summarized]
[What's next?]
```

**Principle:** Each step gets narrower, then expands slightly

---

### Pattern 3: Smart Defaults

When user doesn't specify, system fills in intelligently:

```
User creates OKR with no confidence level
→ System sets: 70% (best practice)
→ Shows: "Why 70%? Ambitious but achievable."
→ User can change, but most don't (friction reduced)

User creates OKR with no parent
→ System links to obvious parent
→ Shows: "This ladders to Company Goal"
→ No cascading selector needed
```

---

### Pattern 4: Status Colors (Universal)

**Green (#16a34a):**
- OKR on track
- Blocker resolved
- Feedback given

**Amber (#d97706):**
- OKR at risk
- Blocker active
- Review needed

**Red (#dc2626):**
- OKR blocked
- Blocker critical
- Action required

**Blue (#2563eb):**
- In progress
- Information
- Pending action

---

## LANDING PAGE: ADOPTION-FIRST DESIGN

### Above the Fold

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  [Logo] OKR Creator                              [Start]   │
│                                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                             │
│  OKRs That Actually Work                                  │
│                                                             │
│  Most OKR tools are complicated.                          │
│  We made one that's simple.                               │
│                                                             │
│  [Watch 60-sec demo]                [Start Free]          │
│                                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                             │
│  [Screenshot of dashboard - simple, clean]                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

COPY PRINCIPLES:
- "Simple" not "Intelligent"
- "Works" not "Sophisticated"
- Action-focused ("Start Free", "Watch Demo")
```

### Value Props (Three Columns)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ ⚡ Simple    │  │ 🎯 Aligned   │  │ 📈 Works     │    │
│  │              │  │              │  │              │    │
│  │ Create an    │  │ Your OKRs    │  │ 70% of teams │    │
│  │ OKR in 3     │  │ automatically │  │ hit targets  │    │
│  │ minutes.     │  │ roll up to    │  │ on first try.│    │
│  │ No training  │  │ company goals.│  │              │    │
│  │ needed.      │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

DESIGN:
- Icons (not dense text)
- One sentence each (not paragraphs)
- Problem → solution (implicit)
```

### Social Proof (Small, Not Pushy)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Trusted by 200+ companies                                │
│                                                             │
│  [Logo] [Logo] [Logo] [Logo] [Logo]                       │
│                                                             │
│  "We went from spreadsheets to real OKRs in a week."      │
│  — Jane, COO at Acme Corp                                 │
│                                                             │
│  "Finally, an OKR tool that doesn't feel like homework."  │
│  — Marcus, VP Ops at Startup Inc                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

CREDIBILITY:
- Small numbers (200+ not 10,000+)
- Relatable quotes (not gushing)
- Real role names (not generic "CEO")
```

### CTA Section (Bottom)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Ready to align your team?                                │
│                                                             │
│  [Start Free Trial] (no credit card)                      │
│                                                             │
│  Questions?  [Schedule 15-min chat]                       │
│                                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                             │
│  [Footer links]                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## COMPARISON: Lattice vs OKR Creator UX

| Moment | Lattice | OKR Creator |
|--------|---------|-------------|
| **Landing** | "Enterprise Goal Management" | "OKRs That Actually Work" |
| **Signup** | 8 fields | 3 fields + continue with Google |
| **First OKR** | Modal → Cascading selector → Form | One input field, progressive steps |
| **Validation** | After submit | Real-time, as you type |
| **Examples** | Link to docs | Inline in every workflow |
| **Confidence** | Not built-in | Central, with guidance |
| **Check-in** | Multi-step form | One card, 4 fields |
| **Dashboard** | Drill-into-detail | Status at a glance |
| **Onboarding** | 30 min tutorial | 3 minute walkthrough |
| **Feel** | Academic | Conversational |

---

## ACCESSIBILITY & MOBILE

### Mobile (Important!)

- **Touch targets:** 44px minimum (buttons, links)
- **One column:** Stack everything vertically
- **Large text:** 16px minimum (prevents zoom-to-read)
- **Form fields:** 44px tall (easy to tap)
- **Modal dialogs:** Full screen on mobile

**Mobile check-in (should be FAST):**
```
Phone view of weekly check-in:
Status: [Tap to select]
Progress: [Slider]
Confidence: [Tap to select]
Blocker: [Text input]
[Save]

Total screen height: One viewport (no scroll)
```

### Accessibility

- **Color + Icon:** Never rely on color alone
- **Labels:** Every input has associated label
- **ARIA:** Screen reader friendly
- **Keyboard:** Tab through all interactive elements
- **Contrast:** WCAG AA minimum (4.5:1 for text)

---

## DESIGN IMPLEMENTATION ROADMAP

### Phase 1: Core Flows (Weeks 1-4)
- [ ] Design system (tokens, components)
- [ ] Dashboard mockup
- [ ] OKR creation flow (all 4 phases)
- [ ] Weekly check-in card
- [ ] Figma components library

### Phase 2: Advanced Flows (Weeks 5-8)
- [ ] Grading interface
- [ ] Org dashboard (CEO view)
- [ ] Cascade tree visualization
- [ ] Mobile designs (all screens)
- [ ] Micro-interactions (Figma prototypes)

### Phase 3: Polish & Test (Weeks 9-10)
- [ ] Usability testing (5 users)
- [ ] Accessibility audit
- [ ] Mobile testing (iOS + Android)
- [ ] Animation refinement
- [ ] Design handoff to dev

---

## THE ONE-LINE DESIGN PHILOSOPHY

**"Simple enough for your first meeting, sophisticated enough for your quarterly review."**

---

## NEXT STEPS

1. **Create Figma project** with design system
2. **Build interactive prototypes** for all flows
3. **Run usability tests** with 5 COOs
4. **Iterate based on feedback** (especially check-in flow)
5. **Hand off to dev** with component specs

This design removes the "academic exercise" feeling and makes adoption feel natural.
