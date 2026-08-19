import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import MetricCard from "../components/MetricCard";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { useLiveMetrics } from "../hooks/useLiveMetrics";
import { timeAgo, formatCurrency } from "../utils/format";
import type { Analytics, EmailReply, Learning, Outcomes, Signal } from "../types";

const LIVE_LABELS: Record<string, string> = {
  email_sent: "Email sent",
  email_event: "Email event",
  account_scored: "Account scored",
  campaign_run: "Campaign run finished",
  reply_classified: "Reply classified",
};

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [outcomes, setOutcomes] = useState<Outcomes | null>(null);
  const [learning, setLearning] = useState<Learning | null>(null);
  const [recentSignals, setRecentSignals] = useState<Signal[]>([]);
  const [replies, setReplies] = useState<EmailReply[]>([]);
  const [loading, setLoading] = useState(true);
  const { events, connected } = useLiveMetrics();

  useEffect(() => {
    async function load() {
      try {
        const [analyticsData, outcomesData, learningData, signalsData, repliesData] = await Promise.all([
          api.get<Analytics>("/api/v1/analytics"),
          api.get<Outcomes>("/api/v1/analytics/outcomes"),
          api.get<Learning>("/api/v1/analytics/learning"),
          api.get<Signal[]>("/api/v1/signals?limit=8"),
          api.get<EmailReply[]>("/api/v1/replies"),
        ]);
        setAnalytics(analyticsData);
        setOutcomes(outcomesData);
        setLearning(learningData);
        setRecentSignals(signalsData);
        setReplies(repliesData);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  const hotSignals = useMemo(
    () => recentSignals.filter((s) => s.account_tier === 1 || (s.account_score ?? 0) >= 70).slice(0, 6),
    [recentSignals],
  );

  const recommendations = useMemo(() => (learning?.recommendations ?? []).slice(0, 4), [learning]);

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  if (!analytics) {
    return <EmptyState title="No data yet" description="Connect sources and start a campaign to see insights." />;
  }

  const maxWeekly = Math.max(...analytics.weekly_activity.map((m) => m.value), 1);
  const maxFunnel = Math.max(...analytics.funnel.map((f) => f.value), 1);

  return (
    <div className="stack">
      <div className="metric-grid">
        <MetricCard label="Signals this week" value={analytics.signals_this_week} icon="◎" accent="indigo" />
        <MetricCard label="Target accounts" value={analytics.total_accounts} icon="◈" accent="blue" />
        <MetricCard label="Active campaigns" value={analytics.active_campaigns} icon="◉" accent="amber" />
        <MetricCard label="Emails sent" value={analytics.emails_sent} icon="✉" accent="green" />
        <MetricCard label="Replies" value={analytics.emails_replied} icon="↩" accent="rose" />
      </div>

      <div className={`live-banner${connected ? " live-on" : ""}`}>
        <span className="live-dot" />
        <span>{connected ? "Live — streaming account activity" : "Live feed offline"}</span>
        {events.length > 0 && <span className="live-event-count">{events.length} events</span>}
      </div>

      <div className="metric-grid">
        <MetricCard label="Pipeline value" value={formatCurrency(outcomes?.pipeline_value ?? 0)} icon="◉" accent="green" />
        <MetricCard label="Monthly forecast" value={formatCurrency(outcomes?.monthly_forecast ?? 0)} icon="◍" accent="indigo" />
        <MetricCard label="Time saved" value={`${outcomes?.time_saved_hours ?? 0}h`} icon="◷" accent="blue" />
        <MetricCard label="Deals (est.)" value={outcomes?.deals_estimate ?? 0} icon="◈" accent="amber" />
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
      </div>

      <div className="card-grid">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Weekly activity</h2>
          </div>
          <div className="card-body">
            <div className="bar-chart">
              {analytics.weekly_activity.map((point) => (
                <div key={point.label} className="bar-item" title={`${point.label}: ${point.value}`}>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ height: `${Math.max((point.value / maxWeekly) * 100, 3)}%` }} />
                  </div>
                  <span className="bar-label">{point.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Engagement funnel</h2>
          </div>
          <div className="card-body">
            <div className="funnel">
              {analytics.funnel.map((step) => (
                <div key={step.label} className="funnel-step">
                  <div className="funnel-label">{step.label}</div>
                  <div className="funnel-track">
                    <div className="funnel-bar" style={{ width: `${(step.value / maxFunnel) * 100}%` }} />
                  </div>
                  <div className="funnel-value">{step.value}</div>
                </div>
              ))}
            </div>
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
            <ul className="source-list">
              {analytics.top_sources.map((source) => (
                <li key={source.label} className="source-row">
                  <span className="source-name">{source.label}</span>
                  <span className="source-count">{source.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Accounts by tier</h2>
          </div>
          <div className="card-body">
            <ul className="source-list">
              {analytics.signals_by_tier.map((tier) => (
                <li key={tier.label} className="source-row">
                  <span className="source-name">{tier.label}</span>
                  <span className="source-count">{tier.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}