import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useCampaigns } from "../hooks/useCampaigns";
import { SkeletonList } from "../components/Skeleton";
import EmptyState from "../components/EmptyState";
import ConfirmDialog, { type ConfirmState } from "../components/Confirm";
import { StatusBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { formatDate, formatNumber } from "../utils/format";

export default function Campaigns() {
  const { campaigns, loading, error, refresh } = useCampaigns();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [quickName, setQuickName] = useState("");
  const [quickEmails, setQuickEmails] = useState("");
  const [quickBusy, setQuickBusy] = useState(false);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);

  async function quickLaunch() {
    const emails = quickEmails
      .split(/[\s,;]+/)
      .map((e) => e.trim())
      .filter((e) => e.includes("@"));
    if (emails.length === 0) {
      toast("Paste at least one email address", "error");
      return;
    }
    setQuickBusy(true);
    try {
      const created = await api.post<{ id: string }>("/api/v1/campaigns", {
        name: quickName.trim() || `Quick launch (${emails.length} targets)`,
      });
      await api.post(`/api/v1/campaigns/${created.id}/import-emails`, { emails });
      await api.post(`/api/v1/campaigns/${created.id}/run`);
      toast("Campaign launched — detection running in the background", "success");
      void refresh();
      navigate(`/campaigns/${created.id}`);
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setQuickBusy(false);
    }
  }

  return (
    <div className="stack">
      <div className="filter-bar">
        <div className="filter-spacer" />
        <Link to="/campaigns/new" className="btn btn-primary">
          + New campaign
        </Link>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">🚀 One-click launch</h2>
        </div>
        <div className="card-body">
          <div className="stack">
            <div className="action-bar">
              <input
                className="input"
                placeholder="Campaign name (optional)"
                value={quickName}
                onChange={(event) => setQuickName(event.target.value)}
              />
            </div>
            <textarea
              className="input"
              rows={3}
              placeholder={"Paste prospect emails, one per line or comma-separated, e.g.\n  john@acme.com, jane@globex.io"}
              value={quickEmails}
              onChange={(event) => setQuickEmails(event.target.value)}
            />
            <div className="action-bar">
              <button
                className="btn btn-primary"
                onClick={() =>
                  setConfirm({
                    title: "Launch this campaign?",
                    message: "This creates the campaign, imports the targets, and immediately starts AI detection and scoring. Emails are generated but not sent until you review.",
                    confirmLabel: "Launch",
                    onConfirm: () => void quickLaunch(),
                  })
                }
                disabled={quickBusy}
              >
                {quickBusy ? "Launching…" : "Launch campaign"}
              </button>
              <span className="muted">
                Creates the campaign, imports targets, and starts AI detection + scoring automatically.
              </span>
            </div>
          </div>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <SkeletonList rows={5} />
      ) : campaigns.length === 0 ? (
        <EmptyState
          title="No campaigns yet"
          description="Create a campaign to import target companies and generate personalized outreach."
          action={
            <Link to="/campaigns/new" className="btn btn-primary">
              Create campaign
            </Link>
          }
        />
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Status</th>
                <th>Accounts</th>
                <th>Sent</th>
                <th>Replies</th>
                <th>Created</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td>
                    <div className="cell-title">{campaign.name}</div>
                    {campaign.description && <div className="cell-sub">{campaign.description}</div>}
                  </td>
                  <td>
                    <StatusBadge status={campaign.status} />
                  </td>
                  <td>{campaign.account_count ?? "—"}</td>
                  <td>{formatNumber(campaign.sent_count ?? 0)}</td>
                  <td>{formatNumber(campaign.reply_count ?? 0)}</td>
                  <td className="cell-time">{formatDate(campaign.created_at)}</td>
                  <td>
                    <Link to={`/campaigns/${campaign.id}`} className="btn btn-secondary btn-sm">
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog state={confirm} onClose={() => setConfirm(null)} />
    </div>
  );
}