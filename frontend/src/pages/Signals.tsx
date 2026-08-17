import { useState } from "react";
import { api } from "../lib/api";
import { useSignals } from "../hooks/useSignals";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import Modal from "../components/Modal";
import { SignalTypeBadge, SourceBadge, TierBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { timeAgo } from "../utils/format";

const SOURCES = ["apollo", "sec_edgar", "newsapi", "ga4", "manual", "hunter"];
const TYPES = ["company_created", "company_growth", "hiring_spree", "funding_round", "product_launch", "negative_sentiment"];

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
  const [manualAccount, setManualAccount] = useState("");
  const [manualTitle, setManualTitle] = useState("");
  const [manualDescription, setManualDescription] = useState("");
  const [saving, setSaving] = useState(false);

  async function createManual() {
    setSaving(true);
    try {
      await api.post("/api/v1/signals", {
        account_id: manualAccount,
        title: manualTitle,
        description: manualDescription || undefined,
        source: "manual",
        signal_type: "product_launch",
        url: null,
      });
      toast("Signal created", "success");
      setManualOpen(false);
      setManualAccount("");
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
          <label className="label">Account ID</label>
          <input
            className="input"
            value={manualAccount}
            onChange={(event) => setManualAccount(event.target.value)}
            placeholder="UUID of the target account"
          />
        </div>
        <div className="field">
          <label className="label">Title</label>
          <input
            className="input"
            value={manualTitle}
            onChange={(event) => setManualTitle(event.target.value)}
            placeholder="e.g. Expanded sales team in Austin"
          />
        </div>
        <div className="field">
          <label className="label">Description</label>
          <textarea
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