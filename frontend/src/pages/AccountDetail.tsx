import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { formatDateTime, timeAgo } from "../utils/format";
import type { Account, Signal } from "../types";

export default function AccountDetail() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [account, setAccount] = useState<Account | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [scoring, setScoring] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [accountData, signalsData] = await Promise.all([
          api.get<Account>(`/api/v1/accounts/${id}`),
          api.get<Signal[]>(`/api/v1/accounts/${id}/signals`),
        ]);
        setAccount(accountData);
        setSignals(signalsData);
      } catch (err) {
        toast((err as Error).message, "error");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [id, toast]);

  async function rescore() {
    if (!id) return;
    setScoring(true);
    try {
      await api.post<{ score: number }>(`/api/v1/accounts/${id}/score`);
      const [accountData, signalsData] = await Promise.all([
        api.get<Account>(`/api/v1/accounts/${id}`),
        api.get<Signal[]>(`/api/v1/accounts/${id}/signals`),
      ]);
      setAccount(accountData);
      setSignals(signalsData);
      toast(`Account rescored — score ${accountData.score ?? "—"}`, "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setScoring(false);
    }
  }

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  if (!account) {
    return (
      <EmptyState
        title="Account not found"
        action={
          <Link to="/accounts" className="btn btn-secondary">
            Back to accounts
          </Link>
        }
      />
    );
  }

  return (
    <div className="stack">
      <div className="detail-header">
        <div className="account-avatar avatar-lg">{account.company_name.slice(0, 1).toUpperCase()}</div>
        <div>
          <h2 className="detail-title">{account.company_name}</h2>
          <div className="detail-sub">
            {account.domain || account.website || "—"}
            {account.industry ? ` · ${account.industry}` : ""}
          </div>
        </div>
        <div className="filter-spacer" />
        <button className="btn btn-secondary" onClick={rescore} disabled={scoring}>
          {scoring ? "Scoring…" : "Rescore account"}
        </button>
      </div>

      <div className="metric-grid">
        <div className="metric-card accent-indigo">
          <div className="metric-label">Score</div>
          <div className="metric-value">{account.score ?? "—"}</div>
          {account.score_rationale && <div className="metric-delta">{account.score_rationale}</div>}
        </div>
        <div className="metric-card accent-amber">
          <div className="metric-label">Tier</div>
          <div className="metric-value">
            <TierBadge tier={account.tier} />
          </div>
        </div>
        <div className="metric-card accent-blue">
          <div className="metric-label">Employees</div>
          <div className="metric-value">{account.employee_count ?? "—"}</div>
        </div>
        <div className="metric-card accent-green">
          <div className="metric-label">Revenue</div>
          <div className="metric-value">{account.revenue ? `$${Math.round(account.revenue / 1e6)}M` : "—"}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Signals ({signals.length})</h2>
          <span className="muted">Updated {formatDateTime(account.updated_at)}</span>
        </div>
        <div className="card-body">
          {signals.length === 0 ? (
            <EmptyState title="No signals for this account" description="Signals will appear when intent is detected." />
          ) : (
            <ul className="signal-list">
              {signals.map((signal) => (
                <li key={signal.id} className="signal-row">
                  <div className="signal-main">
                    <div className="signal-title">{signal.title}</div>
                    {signal.description && <div className="signal-meta">{signal.description}</div>}
                  </div>
                  <div className="signal-badges">
                    <SourceBadge source={signal.source} />
                    <SignalTypeBadge type={signal.signal_type} />
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