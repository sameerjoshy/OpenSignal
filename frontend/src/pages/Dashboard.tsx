import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import MetricCard from "../components/MetricCard";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { timeAgo } from "../utils/format";
import type { Analytics, Signal } from "../types";

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [recentSignals, setRecentSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [analyticsData, signalsData] = await Promise.all([
          api.get<Analytics>("/api/v1/analytics"),
          api.get<Signal[]>("/api/v1/signals?limit=6"),
        ]);
        setAnalytics(analyticsData);
        setRecentSignals(signalsData);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

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
                    <div
                      className="bar-fill"
                      style={{ height: `${Math.max((point.value / maxWeekly) * 100, 3)}%` }}
                    />
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
              {recentSignals.map((signal) => (
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
    </div>
  );
}