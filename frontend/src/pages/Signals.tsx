import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useSignals } from "../hooks/useSignals";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import Modal from "../components/Modal";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { timeAgo } from "../utils/format";
import type { Account } from "../types";

const SOURCES = ["apollo", "sec_edgar", "newsapi", "ga4", "manual", "hunter"];
const TYPES = [
  "funding",
  "key_decision_maker",
  "website_intent",
  "major_event",
  "earnings",
  "leadership",
  "product_launch",
  "news",
  "job_change",
];

export default function Signals() {
  const [source, setSource] = useState("");
  const [signalType, setSignalType] = useState("");
  const [tier, setTier] = useState("");
  const { signals, loading, error, refresh } = useSignals({
    source: source || undefined,
    signal_type: signalType || undefined,
    tier: tier ? Number(tier) : undefined,
  });
  const { toast } = useToast();
  const [manualOpen, setManualOpen] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountsLoading, setAccountsLoading] = useState(false);
  const [manualAccount, setManualAccount] = useState("");
  const [manualType, setManualType] = useState("product_launch");
  const [manualTitle, setManualTitle] = useState("");
  const [manualDescription, setManualDescription] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!manualOpen || accounts.length > 0) return;
    setAccountsLoading(true);
    api
      .get<Account[]>("/api/v1/accounts?limit=500")
      .then(setAccounts)
      .catch(() => setAccounts([]))
      .finally(() => setAccountsLoading(false));
  }, [manualOpen, accounts.length]);

  async function createManual() {
    setSaving(true);
    try {
      await api.post("/api/v1/signals", {
        account_id: manualAccount,
        title: manualTitle,
        description: manualDescription || undefined,
        source: "manual",
        signal_type: manualType,
        url: null,
      });
      toast("Signal created", "success");
      setManualOpen(false);
      setManualAccount("");
      setManualType("product_launch");
      setManualTitle("");
      setManualDescription("");
      await refresh();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="stack">
      <div className="filter-bar">
        <select className="input select" value={source} onChange={(event) => setSource(event.target.value)}>
          <option value="">All sources</option>
          {SOURCES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <select className="input select" value={signalType} onChange={(event) => setSignalType(event.target.value)}>
          <option value="">All types</option>
          {TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <select className="input select" value={tier} onChange={(event) => setTier(event.target.value)}>
          <option value="">All tiers</option>
          <option value="1">Tier 1</option>
          <option value="2">Tier 2</option>
          <option value="3">Tier 3</option>
        </select>
        <div className="filter-spacer" />
        <button className="btn btn-primary" onClick={() => setManualOpen(true)}>
          + Add signal
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="page-loading">
          <Spinner />
        </div>
      ) : signals.length === 0 ? (
        <EmptyState
          title="No signals"
          description="No signals match the current filters. Connect sources or add a signal manually."
          action={
            <button className="btn btn-primary" onClick={() => setManualOpen(true)}>
              Add signal
            </button>
          }
        />
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Signal</th>
                <th>Account</th>
                <th>Source</th>
                <th>Type</th>
                <th>Tier</th>
                <th>Detected</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal) => (
                <tr key={signal.id}>
                  <td>
                    <div className="cell-title">{signal.title}</div>
                    {signal.description && <div className="cell-sub">{signal.description}</div>}
                  </td>
                  <td className="cell-account">{signal.account_name || "—"}</td>
                  <td>
                    <SourceBadge source={signal.source} />
                  </td>
                  <td>
                    <SignalTypeBadge type={signal.signal_type} />
                  </td>
                  <td>
                    <TierBadge tier={signal.account_tier} />
                  </td>
                  <td className="cell-time">{timeAgo(signal.detected_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={manualOpen}
        title="Add signal"
        onClose={() => setManualOpen(false)}
        footer={
          <>
            <button className="btn btn-ghost" onClick={() => setManualOpen(false)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={createManual} disabled={saving || !manualAccount || !manualTitle}>
              {saving ? "Saving…" : "Create signal"}
            </button>
          </>
        }
      >
        <div className="field">
          <label className="label" htmlFor="signal-account">Target account</label>
          {accountsLoading ? (
            <div className="input">Loading accounts…</div>
          ) : accounts.length === 0 ? (
            <div className="input">
              No accounts yet —{" "}
              <Link to="/campaigns/new" className="link" onClick={() => setManualOpen(false)}>
                create a campaign
              </Link>{" "}
              to import targets
            </div>
          ) : (
            <select
              id="signal-account"
              className="input select"
              value={manualAccount}
              onChange={(event) => setManualAccount(event.target.value)}
            >
              <option value="">Select an account…</option>
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.company_name}
                  {acc.tier ? ` · ${acc.tier === 1 ? "Tier 1" : acc.tier === 2 ? "Tier 2" : "Tier 3"}` : ""}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="field">
          <label className="label" htmlFor="signal-type">Type</label>
          <select
            id="signal-type"
            className="input select"
            value={manualType}
            onChange={(event) => setManualType(event.target.value)}
          >
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="label" htmlFor="signal-title">Title</label>
          <input
            id="signal-title"
            className="input"
            value={manualTitle}
            onChange={(event) => setManualTitle(event.target.value)}
            placeholder="e.g. Expanded sales team in Austin"
          />
        </div>
        <div className="field">
          <label className="label" htmlFor="signal-description">Description</label>
          <textarea
            id="signal-description"
            className="textarea"
            value={manualDescription}
            onChange={(event) => setManualDescription(event.target.value)}
            rows={3}
            placeholder="Optional context"
          />
        </div>
      </Modal>
    </div>
  );
}