import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import MetricCard from "../components/MetricCard";
import Skeleton from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { AreaChart, FunnelBars, MiniBars } from "../components/charts";
import { useLiveMetrics } from "../hooks/useLiveMetrics";
import { useToast } from "../components/Toast";
import { timeAgo, formatCurrency } from "../utils/format";
import type { Analytics, EmailReply, Learning, Outcomes, Signal } from "../types";

interface FollowUp {
  message_id: string;
  account_id?: string | null;
  company_name?: string | null;
  contact_email: string;
  subject: string;
  campaign_name?: string | null;
  clicked_at: string;
}

const LIVE_LABELS: Record<string, string> = {
  email_sent: "Email sent",
  email_event: "Email event",
  account_scored: "Account scored",
  campaign_run: "Campaign run finished",
  reply_classified: "Reply classified",
};

const EMPTY_ANALYTICS: Analytics = {
  total_signals: 0,
  total_accounts: 0,
  total_campaigns: 0,
  active_campaigns: 0,
  signals_this_week: 0,
  emails_sent: 0,
  emails_opened: 0,
  emails_clicked: 0,
  emails_replied: 0,
  top_sources: [],
  signals_by_tier: [],
  funnel: [],
  weekly_activity: [],
};

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [outcomes, setOutcomes] = useState<Outcomes | null>(null);
  const [learning, setLearning] = useState<Learning | null>(null);
  const [recentSignals, setRecentSignals] = useState<Signal[]>([]);
  const [replies, setReplies] = useState<EmailReply[]>([]);
  const [followUps, setFollowUps] = useState<FollowUp[]>([]);
  const [followUpSending, setFollowUpSending] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { events, connected } = useLiveMetrics();
  const { toast } = useToast();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      const results = await Promise.allSettled([
        api.get<Analytics>("/api/v1/analytics"),
        api.get<Outcomes>("/api/v1/analytics/outcomes"),
        api.get<Learning>("/api/v1/analytics/learning"),
        api.get<Signal[]>("/api/v1/signals?limit=8"),
        api.get<EmailReply[]>("/api/v1/replies"),
        api.get<FollowUp[]>("/api/v1/follow-ups"),
      ]);
      if (cancelled) return;
      if (results[0].status === "fulfilled") setAnalytics(results[0].value);
      if (results[1].status === "fulfilled") setOutcomes(results[1].value);
      if (results[2].status === "fulfilled") setLearning(results[2].value);
      if (results[3].status === "fulfilled") setRecentSignals(results[3].value);
      if (results[4].status === "fulfilled") setReplies(results[4].value);
      if (results[5].status === "fulfilled") setFollowUps(results[5].value);
      const failed = results.filter((r) => r.status === "rejected").length;
      setError(failed > 0 ? `Some data couldn't load (${failed} section${failed > 1 ? "s" : ""}). Retrying may help.` : null);
      setLoading(false);
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function sendFollowUp(messageId: string) {
    setFollowUpSending(messageId);
    try {
      const result = await api.post<{ message: string }>(`/api/v1/follow-ups/${messageId}/send`);
      toast(result.message, "success");
      setFollowUps((prev) => prev.filter((f) => f.message_id !== messageId));
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setFollowUpSending(null);
    }
  }

  const hotSignals = useMemo(
    () => recentSignals.filter((s) => s.account_tier === 1 || (s.account_score ?? 0) >= 70).slice(0, 6),
    [recentSignals],
  );

  const recommendations = useMemo(() => (learning?.recommendations ?? []).slice(0, 4), [learning]);

  const a = analytics ?? EMPTY_ANALYTICS;

  if (loading) {
    return <Skeleton variant="page" />;
  }

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-desc">Your signal intelligence pipeline — live and at a glance.</p>
        </div>
        <button className="btn btn-secondary" onClick={() => window.location.reload()} title="Refresh dashboard">
          ↻ Refresh
        </button>
      </div>
      {error && (
        <div className="alert alert-warning" role="alert">
          <span>{error}</span>
          <button className="btn btn-secondary btn-sm" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      )}
      <div className="metric-grid">
        <MetricCard label="Signals this week" value={a.signals_this_week} icon="◎" accent="indigo" />
        <MetricCard label="Target accounts" value={a.total_accounts} icon="◈" accent="blue" />
        <MetricCard label="Active campaigns" value={a.active_campaigns} icon="◉" accent="amber" />
        <MetricCard label="Emails sent" value={a.emails_sent} icon="✉" accent="green" />
        <MetricCard label="Replies" value={a.emails_replied} icon="↩" accent="rose" />
      </div>

      <div className={`live-banner${connected ? " live-on" : ""}`}>
        <span className="live-dot" />
        <span>{connected ? "Live — streaming account activity" : "Live feed offline — reconnecting…"}</span>
        {events.length > 0 && <span className="live-event-count">{events.length} events</span>}
      </div>

      <div className="metric-grid">
        <MetricCard label="Pipeline value" value={outcomes ? formatCurrency(outcomes.pipeline_value) : "—"} icon="◉" accent="green" />
        <MetricCard label="Monthly forecast" value={outcomes ? formatCurrency(outcomes.monthly_forecast) : "—"} icon="◍" accent="indigo" />
        <MetricCard label="Time saved" value={outcomes ? `${outcomes.time_saved_hours}h` : "—"} icon="◷" accent="blue" />
        <MetricCard label="Deals (est.)" value={outcomes ? outcomes.deals_estimate : "—"} icon="◈" accent="amber" />
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Hot signals</h2>
            <Link to="/signals" className="link">
              View all
            </Link>
          </div>
          <div className="card-body">
            {hotSignals.length === 0 ? (
              <EmptyState title="No hot signals yet" description="Tier-1 accounts will surface here." />
            ) : (
              <ul className="signal-list">
                {hotSignals.map((signal) => (
                  <li key={signal.id} className="signal-row">
                    <div className="signal-main">
                      <div className="signal-title">{signal.title}</div>
                      <div className="signal-meta">
                        <span className="signal-account">{signal.account_name || "Unknown account"}</span>
                        {signal.url && (
                          <a href={signal.url} target="_blank" rel="noreferrer" className="link">
                            source
                          </a>
                        )}
                      </div>
                    </div>
                    <div className="signal-badges">
                      <SourceBadge source={signal.source} />
                      <SignalTypeBadge type={signal.signal_type} />
                      <TierBadge tier={signal.account_tier} />
                    </div>
                    <span className="signal-time">{timeAgo(signal.detected_at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recommended next steps</h2>
          </div>
          <div className="card-body">
            {recommendations.length === 0 ? (
              <EmptyState title="No recommendations yet" description="Insights will appear as you run campaigns." />
            ) : (
              <ol className="recommendation-list">
                {recommendations.map((rec) => (
                  <li key={rec.label} className="recommendation-item">
                    <div className="recommendation-title">{rec.label}</div>
                    <div className="recommendation-detail">{rec.detail}</div>
                    <span className="recommendation-tag">{rec.value}</span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Follow up now</h2>
            <span className="muted">{followUps.length} clicked, no reply</span>
          </div>
          <div className="card-body">
            {followUps.length === 0 ? (
              <EmptyState title="Nothing to follow up on" description="Accounts that click but don't reply appear here — prime time to send a step-2 nudge." />
            ) : (
              <ul className="signal-list">
                {followUps.slice(0, 5).map((f) => (
                  <li key={f.message_id} className="signal-row">
                    <div className="signal-main">
                      <div className="signal-title">{f.company_name ?? f.contact_email}</div>
                      <div className="signal-meta">
                        <span className="signal-account">{f.contact_email}</span>
                        <span className="signal-account">· “{f.subject}”</span>
                      </div>
                      <div className="signal-meta">Clicked {timeAgo(f.clicked_at)}</div>
                    </div>
                    <button className="btn btn-secondary btn-sm" onClick={() => void sendFollowUp(f.message_id)} disabled={followUpSending === f.message_id}>
                      {followUpSending === f.message_id ? "Sending…" : "Send follow-up"}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Weekly activity</h2>
            <div className="card-sub">Signals captured per week</div>
          </div>
          <div className="card-body">
            <AreaChart data={a.weekly_activity} height={190} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement funnel</h2>
            <div className="card-sub">Conversion vs. previous stage</div>
          </div>
          <div className="card-body">
            <FunnelBars data={a.funnel} />
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Live activity</h2>
          </div>
          <div className="card-body">
            {events.length === 0 ? (
              <EmptyState title="No live events yet" description="Send emails or score accounts to see live updates." />
            ) : (
              <ul className="signal-list">
                {[...events].reverse().map((event, idx) => (
                  <li key={`${event.type}-${idx}`} className="signal-row">
                    <div className="signal-main">
                      <div className="signal-title">{LIVE_LABELS[event.type] || event.type}</div>
                      <div className="signal-meta">
                        <span className="signal-account">
                          {event.payload.company_name ? String(event.payload.company_name) : event.payload.from_email ? String(event.payload.from_email) : event.payload.to_email ? String(event.payload.to_email) : "event"}
                        </span>
                      </div>
                    </div>
                    <span className="live-event-time">now</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent signals</h2>
            <Link to="/signals" className="link">
              View all
            </Link>
          </div>
          <div className="card-body">
            {recentSignals.length === 0 ? (
              <EmptyState title="No signals yet" description="Signals will appear once sources are connected." />
            ) : (
              <ul className="signal-list">
                {recentSignals.slice(0, 5).map((signal) => (
                  <li key={signal.id} className="signal-row">
                    <div className="signal-main">
                      <div className="signal-title">{signal.title}</div>
                      <div className="signal-meta">
                        <span className="signal-account">{signal.account_name || "Unknown account"}</span>
                      </div>
                    </div>
                    <span className="signal-time">{timeAgo(signal.detected_at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent replies</h2>
          </div>
          <div className="card-body">
            {replies.length === 0 ? (
              <EmptyState title="No replies classified yet" description="Inbound replies will be classified here automatically." />
            ) : (
              <ul className="signal-list">
                {replies.slice(0, 5).map((reply) => (
                  <li key={reply.id} className="signal-row">
                    <div className="signal-main">
                      <div className="signal-title">
                        <span className={`intent-tag intent-${reply.classification === "hot" ? 1 : reply.classification === "question" ? 2 : 0}`}>
                          {reply.classification}
                        </span>{" "}
                        {reply.from_email}
                      </div>
                      <div className="signal-meta">
                        <span className="signal-account">{reply.summary || reply.subject || reply.company_name || "Reply"}</span>
                      </div>
                    </div>
                    <span className="signal-time">{timeAgo(reply.created_at)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Top signal sources</h2>
          </div>
          <div className="card-body">
            <MiniBars data={a.top_sources} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Accounts by tier</h2>
          </div>
          <div className="card-body">
            <MiniBars data={a.signals_by_tier} />
          </div>
        </div>
      </div>
    </div>
  );
}