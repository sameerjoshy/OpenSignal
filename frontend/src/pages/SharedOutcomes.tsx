import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import { formatCurrency } from "../utils/format";
import type { Analytics, Outcomes } from "../types";

interface SharedData {
  shared_by: string;
  analytics: Analytics;
  outcomes: Outcomes;
}

export default function SharedOutcomes() {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<SharedData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setData(await api.get<SharedData>(`/api/v1/analytics/shared/${token}`));
      } catch (e) {
        setError(e instanceof Error ? e.message : "This share link is invalid or expired");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [token]);

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="stack" style={{ maxWidth: 980, margin: "0 auto", padding: "2rem 1rem" }}>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">OpenSignal outcomes — shared by {data?.shared_by ?? "a teammate"}</h2>
          <span className="muted">Read-only view</span>
        </div>
        <div className="card-body">
          {error ? (
            <div className="alert alert-error">{error}</div>
          ) : data ? (
            <div className="stack">
              <div className="metric-grid">
                <div className="metric-card accent-green">
                  <div className="metric-label">Pipeline value</div>
                  <div className="metric-value">{formatCurrency(data.outcomes.pipeline_value)}</div>
                </div>
                <div className="metric-card accent-indigo">
                  <div className="metric-label">Monthly forecast</div>
                  <div className="metric-value">{formatCurrency(data.outcomes.monthly_forecast)}</div>
                </div>
                <div className="metric-card accent-blue">
                  <div className="metric-label">Emails sent</div>
                  <div className="metric-value">{data.analytics.emails_sent}</div>
                </div>
                <div className="metric-card accent-amber">
                  <div className="metric-label">Reply rate</div>
                  <div className="metric-value">{data.outcomes.reply_rate}%</div>
                </div>
              </div>
              <div className="metric-grid">
                <div className="metric-card accent-blue">
                  <div className="metric-label">Signals detected</div>
                  <div className="metric-value">{data.analytics.total_signals}</div>
                </div>
                <div className="metric-card accent-indigo">
                  <div className="metric-label">Accounts scored</div>
                  <div className="metric-value">{data.analytics.total_accounts}</div>
                </div>
                <div className="metric-card accent-green">
                  <div className="metric-label">Time saved</div>
                  <div className="metric-value">{data.outcomes.time_saved_hours}h</div>
                </div>
                <div className="metric-card accent-rose">
                  <div className="metric-label">Deals (est.)</div>
                  <div className="metric-value">{data.outcomes.deals_estimate}</div>
                </div>
              </div>
              <p className="muted-note">{data.outcomes.note}</p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}