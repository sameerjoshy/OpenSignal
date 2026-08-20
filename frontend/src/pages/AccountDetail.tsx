import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { formatCompactCurrency, formatDateTime, timeAgo } from "../utils/format";
import type { Account, AccountIntelligence, Signal } from "../types";

interface ApolloContact {
  name?: string | null;
  title?: string | null;
  email?: string | null;
  phone?: string | null;
  linkedin_url?: string | null;
}

const HIGH_INTENT = new Set(["job_change", "funding", "acquisition", "key_decision_maker"]);
const MEDIUM_INTENT = new Set(["tech_stack", "web_traffic", "product_launch", "leadership", "major_event", "website_intent"]);

function intentOf(type: string): { level: "high" | "medium" | "low"; label: string } {
  if (HIGH_INTENT.has(type)) return { level: "high", label: "High intent" };
  if (MEDIUM_INTENT.has(type)) return { level: "medium", label: "Medium intent" };
  return { level: "low", label: "Low intent" };
}

export default function AccountDetail() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [account, setAccount] = useState<Account | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [intel, setIntel] = useState<AccountIntelligence | null>(null);
  const [contacts, setContacts] = useState<ApolloContact[] | null>(null);
  const [contactsLoading, setContactsLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [scoring, setScoring] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [accountData, signalsData, intelData] = await Promise.all([
          api.get<Account>(`/api/v1/accounts/${id}`),
          api.get<Signal[]>(`/api/v1/accounts/${id}/signals`),
          api.get<AccountIntelligence>(`/api/v1/accounts/${id}/intelligence`).catch(() => null),
        ]);
        setAccount(accountData);
        setSignals(signalsData);
        setIntel(intelData);
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
      const [accountData, signalsData, intelData] = await Promise.all([
        api.get<Account>(`/api/v1/accounts/${id}`),
        api.get<Signal[]>(`/api/v1/accounts/${id}/signals`),
        api.get<AccountIntelligence>(`/api/v1/accounts/${id}/intelligence`).catch(() => null),
      ]);
      setAccount(accountData);
      setSignals(signalsData);
      setIntel(intelData);
      toast(`Account rescored — score ${accountData.score ?? "—"}`, "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setScoring(false);
    }
  }

  async function findContacts() {
    if (!account?.company_name) return;
    setContactsLoading(true);
    try {
      const domainParam = account.domain ? `&domain=${encodeURIComponent(account.domain)}` : "";
      setContacts(await api.get<ApolloContact[]>(`/api/v1/contacts/search?company=${encodeURIComponent(account.company_name)}${domainParam}&limit=5`));
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setContactsLoading(false);
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

  const best = intel?.best_message;

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
          <div className="metric-value">{formatCompactCurrency(account.revenue)}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Account intelligence</h2>
          <span className="muted">Best contact · engagement · campaign history</span>
        </div>
        <div className="card-body">
          <div className="metric-grid">
            <div className="metric-card accent-green">
              <div className="metric-label">Best contact</div>
              <div className="metric-value">{intel?.contact_email ? "✓" : "—"}</div>
              {intel?.contact_email && <div className="metric-delta">{intel.contact_email}</div>}
            </div>
            <div className="metric-card accent-blue">
              <div className="metric-label">Emails sent</div>
              <div className="metric-value">{intel?.emails_sent ?? 0}</div>
            </div>
            <div className="metric-card accent-indigo">
              <div className="metric-label">Opened</div>
              <div className="metric-value">{intel ? `${intel.open_rate}%` : "—"}</div>
              <div className="metric-delta">{intel?.emails_opened ?? 0} opened</div>
            </div>
            <div className="metric-card accent-amber">
              <div className="metric-label">Replied</div>
              <div className="metric-value">{intel ? `${intel.reply_rate}%` : "—"}</div>
              <div className="metric-delta">{intel?.emails_replied ?? 0} replies</div>
            </div>
          </div>

          <div className="intent-legend" style={{ margin: "1rem 0 0.5rem" }}>
            <span className="intent-legend-item"><span className="intent-dot intent-dot-high" /> {intel?.high_intent_signals ?? 0} high-intent signals</span>
            <span className="intent-legend-item"><span className="intent-dot intent-dot-medium" /> {intel?.medium_intent_signals ?? 0} medium-intent signals</span>
            <span className="intent-legend-item"><span className="intent-dot intent-dot-low" /> {intel?.low_intent_signals ?? 0} low-intent signals</span>
          </div>

          {best && (
            <div className="recommendation-item">
              <div>
                <strong>Best-performing message</strong>
                <div className="signal-meta">“{best.subject}” · {best.campaign_name ?? "Campaign"}</div>
              </div>
              <span className="signal-time">{best.replied_at ? `Replied ${timeAgo(best.replied_at)}` : best.opened_at ? `Opened ${timeAgo(best.opened_at)}` : `Sent ${timeAgo(best.sent_at ?? best.created_at)}`}</span>
            </div>
          )}

          <div className="action-bar" style={{ margin: "1rem 0 0.5rem" }}>
            <button className="btn btn-secondary btn-sm" onClick={() => void findContacts()} disabled={contactsLoading}>
              {contactsLoading ? "Searching…" : "Find decision-makers"}
            </button>
            {contacts !== null && <span className="muted">People Search</span>}
          </div>
          {contacts !== null && contacts.length > 0 && (
            <div className="intent-legend" style={{ marginBottom: "0.75rem" }}>
              {contacts.map((c, i) => (
                <span key={i} className="intent-legend-item">
                  {c.name || c.email || c.title}
                  {c.title ? ` — ${c.title}` : ""}
                  {c.email ? ` · ${c.email}` : ""}
                </span>
              ))}
            </div>
          )}
          {contacts !== null && contacts.length === 0 && (
            <p className="muted" style={{ marginTop: "0.5rem" }}>No decision-makers found. Connect Hunter (free) for a fallback or check the company name.</p>
          )}

          {intel && intel.campaigns.length > 0 && (
            <table className="data-table" style={{ marginTop: "1rem" }}>
              <thead>
                <tr>
                  <th>Campaign</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Sent</th>
                </tr>
              </thead>
              <tbody>
                {intel.campaigns.map((m) => (
                  <tr key={m.id}>
                    <td>{m.campaign_name ?? "—"}</td>
                    <td>{m.subject}</td>
                    <td>
                      <span className={`status-pill status-${m.status}`}>{m.status}</span>
                    </td>
                    <td className="muted">{m.sent_at ? formatDateTime(m.sent_at) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {intel && intel.campaigns.length === 0 && (
            <p className="muted" style={{ marginTop: "0.5rem" }}>
              No campaign emails yet. Run this account in a campaign to build its history.
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Buying signals ({signals.length})</h2>
          <span className="muted">Updated {formatDateTime(account.updated_at)}</span>
        </div>
        <div className="card-body">
          <div className="intent-legend">
            <span className="intent-legend-item"><span className="intent-dot intent-dot-high" /> High intent — ready to engage</span>
            <span className="intent-legend-item"><span className="intent-dot intent-dot-medium" /> Medium intent — watch closely</span>
            <span className="intent-legend-item"><span className="intent-dot intent-dot-low" /> Low intent — nurture</span>
          </div>
          {signals.length === 0 ? (
            <EmptyState title="No signals for this account" description="Signals will appear when intent is detected." />
          ) : (
            <ul className="signal-list">
              {signals.map((signal) => {
                const intent = intentOf(signal.signal_type);
                return (
                  <li key={signal.id} className={`signal-row intent-row intent-${intent.level}`}>
                    <span className="intent-rail" />
                    <div className="signal-main">
                      <div className="signal-title">{signal.title}</div>
                      {signal.description && <div className="signal-meta">{signal.description}</div>}
                    </div>
                    <div className="signal-badges">
                      <span className={`intent-tag intent-${intent.level === "high" ? 1 : intent.level === "medium" ? 2 : 0}`}>{intent.label}</span>
                      <SourceBadge source={signal.source} />
                      <SignalTypeBadge type={signal.signal_type} />
                    </div>
                    <span className="signal-time">{timeAgo(signal.detected_at)}</span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}