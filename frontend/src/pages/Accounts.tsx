import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { TierBadge } from "../components/Badges";
import { formatDate, formatNumber } from "../utils/format";
import type { Account } from "../types";

export default function Accounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tierFilter, setTierFilter] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const params = new URLSearchParams();
        if (tierFilter) params.set("tier", tierFilter);
        const result = await api.get<Account[]>(`/api/v1/accounts${params.toString() ? `?${params}` : ""}`);
        setAccounts(result);
        setError(null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [tierFilter]);

  return (
    <div className="stack">
      <div className="filter-bar">
        <select className="input select" value={tierFilter} onChange={(event) => setTierFilter(event.target.value)}>
          <option value="">All tiers</option>
          <option value="1">Tier 1</option>
          <option value="2">Tier 2</option>
          <option value="3">Tier 3</option>
        </select>
        <div className="filter-spacer" />
        <span className="count-label">{accounts.length} accounts</span>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="page-loading">
          <Spinner />
        </div>
      ) : accounts.length === 0 ? (
        <EmptyState
          title="No accounts yet"
          description="Import companies in a campaign, or add accounts directly to start tracking intent."
          action={
            <Link to="/campaigns/new" className="btn btn-primary">
              Create campaign
            </Link>
          }
        />
      ) : (
        <div className="account-grid">
          {accounts.map((account) => (
            <Link key={account.id} to={`/accounts/${account.id}`} className="account-card card">
              <div className="account-card-header">
                <div className="account-avatar">{account.company_name.slice(0, 1).toUpperCase()}</div>
                <div>
                  <div className="account-name">{account.company_name}</div>
                  <div className="account-domain">{account.domain || account.website || "—"}</div>
                </div>
                <TierBadge tier={account.tier} />
              </div>
              <div className="account-card-stats">
                <div className="stat">
                  <span className="stat-value">{account.score ?? "—"}</span>
                  <span className="stat-label">Score</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{formatNumber(account.employee_count ?? 0)}</span>
                  <span className="stat-label">Employees</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{account.industry || "—"}</span>
                  <span className="stat-label">Industry</span>
                </div>
              </div>
              <div className="account-card-footer">
                <span>Added {formatDate(account.created_at)}</span>
                {account.revenue ? <span>${formatNumber(account.revenue / 1e6)}M</span> : null}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}