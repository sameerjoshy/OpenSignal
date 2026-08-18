import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { StatusBadge, TierBadge } from "../components/Badges";
import { useToast } from "../components/Toast";
import { formatDateTime, timeAgo } from "../utils/format";
import type { Campaign, CampaignAccount, EmailMessage } from "../types";

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>();
  const { toast } = useToast();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [targets, setTargets] = useState<CampaignAccount[]>([]);
  const [emails, setEmails] = useState<EmailMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<"run" | "send" | "crm" | "emails" | null>(null);
  const [csvBusy, setCsvBusy] = useState(false);
  const [emailsText, setEmailsText] = useState("");

  const load = useCallback(async () => {
    if (!id) return;
    const [campaignData, targetsData, emailsData] = await Promise.all([
      api.get<Campaign>(`/api/v1/campaigns/${id}`),
      api.get<CampaignAccount[]>(`/api/v1/campaigns/${id}/accounts`),
      api.get<EmailMessage[]>(`/api/v1/campaigns/${id}/emails`),
    ]);
    setCampaign(campaignData);
    setTargets(targetsData);
    setEmails(emailsData);
  }, [id]);

  useEffect(() => {
    async function loadData() {
      try {
        await load();
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, [load]);

  async function runCampaign() {
    if (!id) return;
    setBusy("run");
    try {
      const result = await api.post<{ message: string }>(`/api/v1/campaigns/${id}/run`);
      toast(result.message || "Campaign run complete", "success");
      await load();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setBusy(null);
    }
  }

  async function sendCampaign() {
    if (!id) return;
    setBusy("send");
    try {
      const result = await api.post<{ message: string }>(`/api/v1/campaigns/${id}/send`);
      toast(result.message || "Emails sent", "success");
      await load();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setBusy(null);
    }
  }

  async function syncCrm(service: "hubspot" | "salesforce") {
    if (!id) return;
    setBusy("crm");
    try {
      const result = await api.post<{ message: string }>("/api/v1/crm/sync", { campaign_id: id, service });
      toast(result.message || `Synced to ${service}`, "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setBusy(null);
    }
  }

  async function updateStatus(status: string) {
    if (!id) return;
    try {
      await api.patch(`/api/v1/campaigns/${id}`, { status });
      await load();
      toast(`Campaign ${status}`, "success");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function importEmails() {
    if (!id) return;
    const emails = emailsText
      .split(/[\s,;]+/)
      .map((e) => e.trim())
      .filter((e) => e.includes("@"));
    if (emails.length === 0) {
      toast("Paste at least one email address", "error");
      return;
    }
    setBusy("emails");
    try {
      const result = await api.post<{ message: string }>(`/api/v1/campaigns/${id}/import-emails`, { emails });
      toast(result.message || `Imported ${emails.length} email(s)`, "success");
      setEmailsText("");
      await load();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setBusy(null);
    }
  }

  async function handleEmailFile(file: File | null) {
    if (!id || !file) return;
    setBusy("emails");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await api.postForm<{ message: string }>(`/api/v1/campaigns/${id}/import-emails-file`, formData);
      toast(result.message || "Emails imported", "success");
      await load();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setBusy(null);
    }
  }

  async function handleCsv(file: File | null) {
    if (!id || !file) return;
    setCsvBusy(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await api.postForm<{ message: string }>(`/api/v1/campaigns/${id}/import-csv`, formData);
      toast(result.message, "success");
      await load();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setCsvBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  if (!campaign) {
    return (
      <EmptyState
        title="Campaign not found"
        action={
          <Link to="/campaigns" className="btn btn-secondary">
            Back to campaigns
          </Link>
        }
      />
    );
  }

  const emailStats = [
    { label: "Sent", value: campaign.sent_count ?? 0 },
    { label: "Opened", value: campaign.open_count ?? 0 },
    { label: "Clicked", value: campaign.click_count ?? 0 },
    { label: "Replied", value: campaign.reply_count ?? 0 },
  ];

  return (
    <div className="stack">
      <div className="detail-header">
        <div>
          <h2 className="detail-title">{campaign.name}</h2>
          <div className="detail-sub">
            {campaign.description || "No description"}
            {campaign.tier_filters?.tiers ? ` · Targets tiers ${(campaign.tier_filters.tiers as number[]).join(", ")}` : ""}
          </div>
        </div>
        <div className="filter-spacer" />
        <StatusBadge status={campaign.status} />
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => updateStatus(campaign.status === "paused" ? "active" : "paused")}
          title="Pause / resume"
        >
          {campaign.status === "paused" ? "Resume" : "Pause"}
        </button>
      </div>

      <div className="metric-grid">
        <div className="metric-card accent-indigo">
          <div className="metric-label">Target accounts</div>
          <div className="metric-value">{campaign.account_count ?? 0}</div>
        </div>
        {emailStats.map((stat) => (
          <div key={stat.label} className="metric-card accent-blue">
            <div className="metric-label">{stat.label}</div>
            <div className="metric-value">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="action-bar">
        <button className="btn btn-primary" onClick={runCampaign} disabled={busy !== null}>
          {busy === "run" ? "Running…" : "▶ Run campaign"}
        </button>
        <button className="btn btn-secondary" onClick={sendCampaign} disabled={busy !== null}>
          {busy === "send" ? "Sending…" : "Send emails"}
        </button>
        <button className="btn btn-secondary" onClick={() => syncCrm("hubspot")} disabled={busy !== null}>
          Sync HubSpot
        </button>
        <button className="btn btn-secondary" onClick={() => syncCrm("salesforce")} disabled={busy !== null}>
          Sync Salesforce
        </button>
        <label className="btn btn-ghost" title="Import more companies (CSV)">
          Import CSV{csvBusy ? "…" : ""}
          <input
            type="file"
            accept=".csv,text/csv"
            className="file-input"
            onChange={(event) => void handleCsv(event.target.files?.[0] ?? null)}
          />
        </label>
        <span className="muted">Updated {formatDateTime(campaign.updated_at)}</span>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Import email list</h2>
        </div>
        <div className="card-body">
          <div className="stack">
            <textarea
              className="input"
              rows={4}
              placeholder={"Paste email addresses, one per line or comma-separated, e.g.\n  john@acme.com, jane@globex.io"}
              value={emailsText}
              onChange={(event) => setEmailsText(event.target.value)}
            />
            <div className="action-bar">
              <button className="btn btn-secondary" onClick={() => void importEmails()} disabled={busy !== null}>
                {busy === "emails" ? "Importing…" : "Import emails"}
              </button>
              <label className="btn btn-ghost" title="Upload .txt, .csv, .xls or .xlsx with email addresses">
                Or upload file ({busy === "emails" ? "…" : ".txt/.csv/.xls/.xlsx"})
                <input
                  type="file"
                  accept=".txt,.csv,.xls,.xlsx,text/csv"
                  className="file-input"
                  onChange={(event) => void handleEmailFile(event.target.files?.[0] ?? null)}
                />
              </label>
              <span className="muted">Emails create accounts by domain and pin the recipient for sending.</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Target accounts ({targets.length})</h2>
        </div>
        <div className="card-body">
          {targets.length === 0 ? (
            <EmptyState
              title="No target accounts"
              description="Import companies to start detecting signals and scoring."
              action={
                <Link to={`/campaigns/${campaign.id}`} className="btn btn-primary">
                  Import companies
                </Link>
              }
            />
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Score</th>
                  <th>Tier</th>
                  <th>Status</th>
                  <th>Added</th>
                </tr>
              </thead>
              <tbody>
                {targets.map((target) => (
                  <tr key={target.id}>
                    <td>
                      {target.account ? (
                        <Link to={`/accounts/${target.account_id}`} className="link">
                          {target.account.company_name}
                        </Link>
                      ) : (
                        target.account_id
                      )}
                    </td>
                    <td>{target.score ?? "—"}</td>
                    <td>
                      <TierBadge tier={target.tier} />
                    </td>
                    <td>{target.status}</td>
                    <td className="cell-time">{timeAgo(target.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Emails ({emails.length})</h2>
        </div>
        <div className="card-body">
          {emails.length === 0 ? (
            <EmptyState title="No emails generated yet" description="Run the campaign to generate personalized emails for target accounts." />
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>To</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Step</th>
                  <th>Sent</th>
                </tr>
              </thead>
              <tbody>
                {emails.map((email) => (
                  <tr key={email.id}>
                    <td>{email.to_email}</td>
                    <td>
                      <div className="cell-title">{email.subject}</div>
                      <div className="cell-sub">{email.body_text.slice(0, 120)}…</div>
                    </td>
                    <td>{email.status}</td>
                    <td>{email.sequence_step}</td>
                    <td className="cell-time">{timeAgo(email.sent_at || email.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}