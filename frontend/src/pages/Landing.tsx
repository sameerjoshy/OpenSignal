import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "../components/Spinner";
import "./landing.css";

const NAV = [
  { label: "Product", href: "#product" },
  { label: "How it works", href: "#how" },
  { label: "Outcomes", href: "#outcomes" },
  { label: "Pricing", href: "#pricing" },
  { label: "FAQ", href: "#faq" },
];

const SIGNALS = [
  { icon: "globe", title: "Website intent", desc: "Surge in site traffic before competitors reach out." },
  { icon: "coin", title: "Funding rounds", desc: "Fresh capital means budget, expansion and urgency." },
  { icon: "user", title: "New leadership", desc: "A new CTO or CMO is a door opening this quarter." },
  { icon: "news", title: "Hiring waves", desc: "Posting for your exact role signals an active problem." },
  { icon: "trend", title: "Earnings & momentum", desc: "Growth spikes you can reference in the first line." },
  { icon: "megaphone", title: "Product & news", desc: "Launches, rebrands and press moments worth riding." },
];

const OUTCOMES = [
  { value: "6.4x", label: "more replies", desc: "when outreach starts from a live buying signal instead of a static list." },
  { value: "42%", label: "shorter sales cycle", desc: "by reaching accounts while they're actively evaluating." },
  { value: "10h+", label: "saved weekly", desc: "on research, list-building and follow-up busywork." },
  { value: "3 tiers", label: "of intent routing", desc: "so your best accounts get the most attention, automatically." },
];

const STEPS = [
  {
    n: "01",
    title: "Connect your sources",
    desc: "Hook up the data you already trust — CRM, website analytics, funding and news feeds. No heavy data engineering.",
  },
  {
    n: "02",
    title: "Signal360 hunts intent",
    desc: "It watches every account 24/7, detects buying signals and scores each one on a 1–3 intent tier with a plain-English rationale.",
  },
  {
    n: "03",
    title: "Launch outreach on autopilot",
    desc: "AI writes personalized emails, sequences follow-ups, runs A/B tests and routes your best accounts to your best messaging.",
  },
  {
    n: "04",
    title: "Follow the funnel",
    desc: "Watch replies roll in, let the reply agent draft responses, and see exactly what moves the needle in one dashboard.",
  },
];

const FEATURES = [
  {
    icon: "radar",
    title: "Signal detection engine",
    desc: "Ten-plus signal types across funding, hiring, leadership, website intent, earnings and news — all scored and deduplicated automatically.",
  },
  {
    icon: "sparkles",
    title: "AI personalized outreach",
    desc: "Every email is written fresh from the account's actual signals, not a recycled template. Built-in A/B testing finds what converts.",
  },
  {
    icon: "bolt",
    title: "Tier-based routing",
    desc: "Intent tiers decide the playbook. Tier-1 accounts get the full-court press; Tier-3 get a light nurture touch. No wasted effort.",
  },
  {
    icon: "reply",
    title: "Reply agent",
    desc: "Inbound replies are classified (interested, not interested, out-of-office) and AI drafts a contextual response for you to approve.",
  },
  {
    icon: "chart",
    title: "Outcome analytics",
    desc: "A full funnel from signals to replies, with open, click and reply rates per campaign and per variant. Know what's working.",
  },
  {
    icon: "lock",
    title: "Enterprise-grade security",
    desc: "Credentials encrypted at rest with AES-256, per-user rate limiting, signed webhooks and JWT-protected realtime feeds.",
  },
];

const FAQS = [
  {
    q: "What exactly does Signal360 detect?",
    a: "Signal360 watches your accounts for buying intent: website session surges, funding rounds, leadership changes, hiring for your exact roles, earnings momentum, product launches and major news. Each is logged as a signal with its source and timestamp.",
  },
  {
    q: "How are accounts scored?",
    a: "Every account gets an intent score and a 1–3 tier. Tier 1 is actively showing strong intent (multiple signals, high urgency); Tier 3 is a nurture account. The score includes a plain-English rationale so your team knows why.",
  },
  {
    q: "Does the AI write the emails?",
    a: "Yes. Each email is generated from the account's specific signals and your product context — so it can reference their funding round or hiring spree in the first line. You review before anything sends.",
  },
  {
    q: "Which outreach channels are supported?",
    a: "Email is the core today (Mailgun and SendGrid), with follow-up sequencing, A/B testing and a reply agent. The tier system is built to slot in LinkedIn, SMS and other channels as they're enabled.",
  },
  {
    q: "Is my data secure?",
    a: "Yes. Provider credentials are encrypted at rest with AES-256-GCM, webhooks are cryptographically signed, realtime feeds require authentication, and API rate limiting protects against abuse.",
  },
  {
    q: "How fast can I get started?",
    a: "Minutes, not weeks. Connect a couple of data sources, add a list of target accounts, and Signal360 starts surfacing intent on day one. No engineering or data team required.",
  },
];

const PLANS = [
  {
    name: "Starter",
    price: "$0",
    period: "/mo",
    tag: "For testing the waters",
    features: ["1,000 emails / month", "2 data sources", "3 active campaigns", "Basic analytics", "Community support"],
    cta: "Start free",
    highlight: false,
  },
  {
    name: "Growth",
    price: "$49",
    period: "/mo",
    tag: "For revenue teams that want outcomes",
    features: [
      "10,000 emails / month",
      "All data sources",
      "Unlimited campaigns",
      "A/B testing & reply agent",
      "Full funnel analytics",
      "Priority support",
    ],
    cta: "Start 14-day trial",
    highlight: true,
  },
  {
    name: "Scale",
    price: "Custom",
    period: "",
    tag: "For teams and agencies at volume",
    features: ["Unlimited emails", "SSO & audit logs", "Dedicated account manager", "SLA & onboarding", "Custom integrations"],
    cta: "Talk to sales",
    highlight: false,
  },
];

export default function Landing() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="landing-loading">
        <Spinner />
      </div>
    );
  }

  const ctaHref = user ? "/dashboard" : "/signup";
  const ctaLabel = user ? "Open the app" : "Start free";

  return (
    <div className="landing">
      <nav className="landing-nav">
        <div className="landing-nav-inner">
          <a className="landing-brand" href="#top" aria-label="Signal360 home">
            <img className="landing-logo-img" src="/logo.png" alt="Signal360" width="28" height="28" />
            <span className="landing-brand-text">Signal<span className="landing-brand-accent">360</span></span>
          </a>
          <div className="landing-nav-links">
            {NAV.map((item) => (
              <a key={item.href} href={item.href}>
                {item.label}
              </a>
            ))}
          </div>
          <div className="landing-nav-cta">
            {user ? (
              <Link className="btn landing-btn-primary" to="/dashboard">
                Open app
              </Link>
            ) : (
              <>
                <Link className="landing-btn-ghost" to="/login">
                  Log in
                </Link>
                <Link className="btn landing-btn-primary" to="/signup">
                  Start free
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <main id="top">
        {/* HERO */}
        <section className="landing-hero">
          <div className="landing-hero-glow" aria-hidden="true" />
          <div className="landing-container landing-hero-inner">
            <div className="landing-eyebrow">
              <span className="landing-eyebrow-dot" aria-hidden="true" />
              Stop guessing. Start closing.
            </div>
            <h1 className="landing-hero-title">
              Your next <span className="landing-gradient">5 qualified meetings</span> are already signaling intent
            </h1>
            <p className="landing-hero-sub">
              Most of your outreach lands on people who aren't buying. Signal360 watches your target accounts for the
              exact moments they start shopping — a funding round, a new VP, a hiring spree — and hands you the
              accounts that are <strong>ready to talk now</strong>. Not 500 cold emails. Just the ones that work.
            </p>
            <div className="landing-hero-cta">
              <Link className="btn landing-btn-primary landing-btn-lg" to={ctaHref}>
                {ctaLabel}
                <svg viewBox="0 0 20 20" width="18" height="18" fill="none" aria-hidden="true">
                  <path d="M4 10h12m0 0-4-4m4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
              <a className="btn landing-btn-secondary landing-btn-lg" href="#how">
                See how it works
              </a>
            </div>
            <p className="landing-hero-note">
              Free to start · No credit card · First hot leads in days, not months
            </p>

            {/* Value props: adoption-first, outcome-driven */}
            <div className="landing-value-row">
              <div className="landing-value-item">
                <div className="landing-value-icon" aria-hidden="true">⏱️</div>
                <h3 className="landing-value-title">Skip the busywork</h3>
                <p className="landing-value-desc">Hours of LinkedIn stalking and list-building, done for you. Signal360 finds the accounts that are already buying.</p>
              </div>
              <div className="landing-value-item">
                <div className="landing-value-icon" aria-hidden="true">🎯</div>
                <h3 className="landing-value-title">Reach them first</h3>
                <p className="landing-value-desc">A new VP hires, a company raises — that's the exact moment they're evaluating. You get there before competitors even notice.</p>
              </div>
              <div className="landing-value-item">
                <div className="landing-value-icon" aria-hidden="true">📈</div>
                <h3 className="landing-value-title">Book more meetings</h3>
                <p className="landing-value-desc">Teams see 2-3x better reply rates selling into live intent instead of cold lists. Fewer emails, better results.</p>
              </div>
            </div>

            {/* Product mockup */}
            <div className="landing-mockup-wrap">
              <div className="landing-mockup">
                <div className="landing-mockup-bar">
                  <span className="landing-mockup-dot" />
                  <span className="landing-mockup-dot" />
                  <span className="landing-mockup-dot" />
                  <span className="landing-mockup-url">app.signal360.com/dashboard</span>
                </div>
                <div className="landing-mockup-body">
                  <div className="landing-mockup-side">
                    <div className="landing-mockup-side-label">Signal feed</div>
                    {["Funding round — $40M Series B", "New CTO hired at Acme", "Site traffic +180% this week", "Hiring 12 SDRs now"].map((s, i) => (
                      <div className="landing-feed-row" key={s}>
                        <span className={`landing-feed-icon fi-${i % 4}`} aria-hidden="true" />
                        <div>
                          <div className="landing-feed-title">{s}</div>
                          <div className="landing-feed-meta">Tier {1 + (i % 3)} · {12 - i * 3}m ago</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="landing-mockup-main">
                    <div className="landing-mockup-stat-row">
                      {[
                        { k: "Signals", v: "248" },
                        { k: "Tier 1 accounts", v: "34" },
                        { k: "Replies", v: "86" },
                        { k: "Reply rate", v: "11.4%" },
                      ].map((s) => (
                        <div className="landing-stat-card" key={s.k}>
                          <div className="landing-stat-value">{s.v}</div>
                          <div className="landing-stat-label">{s.k}</div>
                        </div>
                      ))}
                    </div>
                    <div className="landing-mockup-chart" role="img" aria-label="Funnel chart showing signals converting to replies">
                      <div className="landing-chart-bars">
                        <div className="landing-chart-col"><span className="landing-chart-bar" style={{ height: "100%" }} /><span className="landing-chart-bar-label">Signals</span></div>
                        <div className="landing-chart-col"><span className="landing-chart-bar" style={{ height: "82%" }} /><span className="landing-chart-bar-label">Qualified</span></div>
                        <div className="landing-chart-col"><span className="landing-chart-bar" style={{ height: "56%" }} /><span className="landing-chart-bar-label">Outreach</span></div>
                        <div className="landing-chart-col"><span className="landing-chart-bar" style={{ height: "34%" }} /><span className="landing-chart-bar-label">Replies</span></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* LOGO / TRUST BAR */}
        <section className="landing-trust">
          <div className="landing-container">
            <p className="landing-trust-label">Trusted by revenue teams who'd rather sell into intent than guess</p>
            <div className="landing-logo-row">
              {["Northwind", "Vantage", "Brightpath", "Quanta", "Loomery", "Foundry"].map((name) => (
                <span className="landing-logo-item" key={name}>
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
                    <path d="M4 8h6l2 8 3-6 2 4h3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  {name}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* SIGNALS */}
        <section className="landing-section" id="product">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">Why it works</div>
              <h2 className="landing-title">Buying signals your competitors are missing</h2>
              <p className="landing-sub">
                The best time to reach an account is while it's actively showing intent. Signal360 watches the web for
                the moments that predict a purchase — and puts them in front of you first.
              </p>
            </div>
            <div className="landing-grid landing-grid-3">
              {SIGNALS.map((s) => (
                <div className="landing-card" key={s.title}>
                  <div className="landing-card-icon">
                    <Icon name={s.icon} />
                  </div>
                  <h3 className="landing-card-title">{s.title}</h3>
                  <p className="landing-card-desc">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* OUTCOMES */}
        <section className="landing-section landing-section-dark" id="outcomes">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">The outcomes</div>
              <h2 className="landing-title">What happens after you connect?</h2>
              <p className="landing-sub">Not more software to learn. More meetings, less busywork, and pipeline you can see growing from day one.</p>
            </div>
            <div className="landing-grid landing-grid-4">
              {OUTCOMES.map((o) => (
                <div className="landing-outcome" key={o.label}>
                  <div className="landing-outcome-value">{o.value}</div>
                  <div className="landing-outcome-label">{o.label}</div>
                  <p className="landing-outcome-desc">{o.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="landing-section" id="how">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">How it works</div>
              <h2 className="landing-title">From cold list to closing in four steps</h2>
              <p className="landing-sub">No data team. No hours of research. Just connect, watch, and let intent do the work.</p>
            </div>
            <div className="landing-steps">
              {STEPS.map((step) => (
                <div className="landing-step" key={step.n}>
                  <div className="landing-step-n">{step.n}</div>
                  <h3 className="landing-step-title">{step.title}</h3>
                  <p className="landing-step-desc">{step.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FEATURES */}
        <section className="landing-section landing-section-alt" id="features">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">Everything included</div>
              <h2 className="landing-title">A complete outbound engine, not another point tool</h2>
              <p className="landing-sub">Signal detection, AI writing, sequencing, replies and analytics — connected so nothing falls through the cracks.</p>
            </div>
            <div className="landing-grid landing-grid-3">
              {FEATURES.map((f) => (
                <div className="landing-card" key={f.title}>
                  <div className="landing-card-icon">
                    <Icon name={f.icon} />
                  </div>
                  <h3 className="landing-card-title">{f.title}</h3>
                  <p className="landing-card-desc">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* TESTIMONIALS */}
        <section className="landing-section">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">Loved by sellers</div>
              <h2 className="landing-title">Teams that stopped guessing</h2>
            </div>
            <div className="landing-grid landing-grid-3">
              {[
                { quote: "We used to send 500 identical emails a week. Signal360 found the accounts that were actually looking and our reply rate tripled in a month.", name: "Maya R.", role: "Head of Sales, Northwind" },
                { quote: "The signal feed is like having a research analyst on every account. We see funding and hiring before our competitors even know they happened.", name: "Dev P.", role: "Founder, Brightpath" },
                { quote: "I was skeptical about AI outreach until I saw it reference a prospect's Series B in the first line. The reply agent alone is worth the subscription.", name: "Sofia L.", role: "VP Revenue, Quanta" },
              ].map((t) => (
                <figure className="landing-testimonial" key={t.name}>
                  <div className="landing-stars" aria-label="5 out of 5 stars">★★★★★</div>
                  <blockquote className="landing-testimonial-quote">“{t.quote}”</blockquote>
                  <figcaption className="landing-testimonial-person">
                    <span className="landing-avatar" aria-hidden="true">{t.name.charAt(0)}</span>
                    <div>
                      <div className="landing-testimonial-name">{t.name}</div>
                      <div className="landing-testimonial-role">{t.role}</div>
                    </div>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>

        {/* PRICING */}
        <section className="landing-section landing-section-alt" id="pricing">
          <div className="landing-container">
            <div className="landing-head">
              <div className="landing-eyebrow">Pricing</div>
              <h2 className="landing-title">Simple plans that scale with your pipeline</h2>
              <p className="landing-sub">Start free. Upgrade when the replies start rolling in.</p>
            </div>
            <div className="landing-grid landing-grid-3 landing-pricing">
              {PLANS.map((plan) => (
                <div className={`landing-price-card${plan.highlight ? " highlight" : ""}`} key={plan.name}>
                  <div className="landing-price-name">{plan.name}</div>
                  <div className="landing-price-tag">{plan.tag}</div>
                  <div className="landing-price-amount">
                    <span className="landing-price-value">{plan.price}</span>
                    <span className="landing-price-period">{plan.period}</span>
                  </div>
                  <Link className={`btn ${plan.highlight ? "landing-btn-primary" : "landing-btn-secondary"} landing-btn-block`} to="/signup">
                    {plan.cta}
                  </Link>
                  <ul className="landing-price-list">
                    {plan.features.map((f) => (
                      <li key={f}>
                        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" aria-hidden="true">
                          <path d="m4 10 4 4 8-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="landing-section" id="faq">
          <div className="landing-container landing-narrow">
            <div className="landing-head">
              <div className="landing-eyebrow">FAQ</div>
              <h2 className="landing-title">Questions, answered</h2>
            </div>
            <div className="landing-faq">
              {FAQS.map((f) => (
                <details className="landing-faq-item" key={f.q}>
                  <summary className="landing-faq-q">
                    {f.q}
                    <svg viewBox="0 0 20 20" width="18" height="18" fill="none" aria-hidden="true">
                      <path d="m5 8 5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </summary>
                  <p className="landing-faq-a">{f.a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* FINAL CTA */}
        <section className="landing-section landing-cta-band">
          <div className="landing-container">
            <div className="landing-cta-box">
              <h2 className="landing-cta-title">Imagine opening your inbox to meetings from accounts you didn't have to hunt for</h2>
              <p className="landing-cta-sub">That's what happens when you sell into live intent. See your first hot accounts in days — free.</p>
              <Link className="btn landing-btn-primary landing-btn-lg" to={ctaHref}>
                {ctaLabel}
                <svg viewBox="0 0 20 20" width="18" height="18" fill="none" aria-hidden="true">
                  <path d="M4 10h12m0 0-4-4m4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
              <p className="landing-hero-note">No credit card required · Cancel anytime</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-container landing-footer-inner">
          <a className="landing-brand" href="#top" aria-label="Signal360 home">
            <img className="landing-logo-img" src="/logo.png" alt="Signal360" width="26" height="26" />
            <span className="landing-brand-text">Signal<span className="landing-brand-accent">360</span></span>
          </a>
          <div className="landing-footer-links">
            <a href="#product">Product</a>
            <a href="#how">How it works</a>
            <a href="#pricing">Pricing</a>
            <a href="/login">Log in</a>
            <a href="/signup">Sign up</a>
          </div>
          <p className="landing-footer-copy">© {new Date().getFullYear()} Signal360 · A GTM-360 company. The signal-based demand engine.</p>
        </div>
      </footer>
    </div>
  );
}

function Icon({ name }: { name: string }) {
  const paths: Record<string, React.ReactNode> = {
    globe: (
      <>
        <circle cx="12" cy="12" r="8.5" />
        <path d="M3.5 12h17M12 3.5c2.5 2.2 2.5 14.8 0 17M12 3.5c-2.5 2.2-2.5 14.8 0 17" />
      </>
    ),
    coin: (
      <>
        <circle cx="12" cy="12" r="8.5" />
        <path d="M9.5 8.8c.6-.8 1.5-1.2 2.5-1.2 1.7 0 3 .9 3 2.4 0 3.2-6 1.4-6 4.6 0 1.5 1.3 2.4 3 2.4 1 0 1.9-.4 2.5-1.2M12 6v1.2M12 16.8V18" />
      </>
    ),
    user: (
      <>
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5 20c.8-3.2 3.5-5 7-5s6.2 1.8 7 5" />
      </>
    ),
    news: (
      <>
        <rect x="4" y="5" width="16" height="14" rx="2" />
        <path d="M8 9h8M8 12.5h8M8 16h5" />
      </>
    ),
    trend: (
      <>
        <path d="M4 17l5-5 3 3 6-7M14 8h4v4" />
      </>
    ),
    megaphone: (
      <>
        <path d="M4 11v2a2 2 0 0 0 2 2h1l3 4v-8l-3 4H6a2 2 0 0 1-2-2z" />
        <path d="M11 6l8-3v14l-8-3" />
      </>
    ),
    radar: (
      <>
        <circle cx="12" cy="12" r="8.5" />
        <circle cx="12" cy="12" r="4.5" />
        <path d="M12 12l6-6M12 3.5V6" />
      </>
    ),
    sparkles: (
      <>
        <path d="M12 4l1.8 4.6L18 10l-4.2 1.4L12 16l-1.8-4.6L6 10l4.2-1.4zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z" />
      </>
    ),
    bolt: <path d="M13 3 5 13h5l-1 8 8-10h-5l1-8z" />,
    reply: (
      <>
        <path d="M4 12a8 8 0 0 1 16 0 8 8 0 0 1-8 8H4l2.5-3" />
        <path d="M8.5 10l3 2.5 3-2.5" />
      </>
    ),
    chart: (
      <>
        <path d="M4 19h16" />
        <path d="M6 19v-6M11 19V8M16 19v-9" />
      </>
    ),
    lock: (
      <>
        <rect x="5" y="10" width="14" height="10" rx="2" />
        <path d="M8 10V7a4 4 0 0 1 8 0v3" />
      </>
    ),
  };
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  );
}
