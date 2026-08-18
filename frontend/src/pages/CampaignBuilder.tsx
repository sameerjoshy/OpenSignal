import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useToast } from "../components/Toast";
import Spinner from "../components/Spinner";
import { parseCompaniesText, parseCompanyCsv, type CompanyRow } from "../utils/csv";
import type { Campaign } from "../types";

export default function CampaignBuilder() {
  const { toast } = useToast();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [tierFilters, setTierFilters] = useState<Record<string, boolean>>({ "1": true, "2": true, "3": true });
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [cadenceSteps, setCadenceSteps] = useState(3);
  const [creating, setCreating] = useState(false);

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [pasted, setPasted] = useState("");
  const [importing, setImporting] = useState(false);
  const [importedCount, setImportedCount] = useState<number | null>(null);

  async function handleCreate() {
    setCreating(true);
    try {
      const tiers = Object.entries(tierFilters)
        .filter(([, enabled]) => enabled)
        .map(([tier]) => Number(tier));
      const result = await api.post<Campaign>("/api/v1/campaigns", {
        name,
        description: description || undefined,
        tier_filters: { tiers },
        channels: { email: emailEnabled, cadence_steps: cadenceSteps },
        cadence: { steps: cadenceSteps, days_between: 2 },
      });
      setCampaign(result);
      toast("Campaign created", "success");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setCreating(false);
    }
  }

  async function handleImportFromText() {
    const companies = parseCompaniesText(pasted);
    if (companies.length === 0) {
      toast("Paste at least one company", "error");
      return;
    }
    await doImport(companies);
  }

  async function handleImportFile(file: File | null) {
    if (!file) return;
    try {
      const companies = await parseCompanyCsv(file);
      await doImport(companies);
    } catch {
      toast("Could not read CSV file", "error");
    }
  }

  async function doImport(companies: CompanyRow[]) {
    if (!campaign) return;
    setImporting(true);
    try {
      const result = await api.post<{ queued: number; message: string }>(`/api/v1/campaigns/${campaign.id}/import`, {
        companies: companies.map((c) => c.company_name),
      });
      setImportedCount(result.queued);
      toast(result.message, "success");
      setPasted("");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setImporting(false);
    }
  }

  return (
    <div className="stack stack-narrow">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Campaign details</h2>
        </div>
        <div className="card-body">
          <div className="field">
            <label className="label">Campaign name</label>
            <input className="input" value={name} onChange={(event) => setName(event.target.value)} placeholder="H2 ABM - Tech leaders" />
          </div>
          <div className="field">
            <label className="label">Description / product context</label>
            <textarea
              className="textarea"
              rows={3}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Used by DeepSeek to generate personalized emails, e.g. 'We sell revenue intelligence for GTM teams.'"
            />
          </div>
          <div className="field">
            <label className="label">Target tiers</label>
            <div className="check-row">
              <label className="check">
                <input
                  type="checkbox"
                  checked={tierFilters["1"]}
                  onChange={(event) => setTierFilters({ ...tierFilters, "1": event.target.checked })}
                />
                Tier 1 (highest intent)
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={tierFilters["2"]}
                  onChange={(event) => setTierFilters({ ...tierFilters, "2": event.target.checked })}
                />
                Tier 2
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={tierFilters["3"]}
                  onChange={(event) => setTierFilters({ ...tierFilters, "3": event.target.checked })}
                />
                Tier 3
              </label>
            </div>
          </div>
          <div className="field">
            <label className="label">Channels</label>
            <div className="check-row">
              <label className="check">
                <input
                  type="checkbox"
                  checked={emailEnabled}
                  onChange={(event) => setEmailEnabled(event.target.checked)}
                />
                Email
              </label>
            </div>
          </div>
          <div className="field">
            <label className="label">Cadence steps: {cadenceSteps}</label>
            <input
              type="range"
              min={1}
              max={5}
              value={cadenceSteps}
              onChange={(event) => setCadenceSteps(Number(event.target.value))}
              className="range"
            />
          </div>
          {campaign ? null : (
            <button className="btn btn-primary" onClick={handleCreate} disabled={creating || !name.trim()}>
              {creating ? "Creating…" : "Create campaign"}
            </button>
          )}
        </div>
      </div>

      {campaign && (
        <>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Import target companies</h2>
              {importedCount !== null && <span className="badge badge-connected">{importedCount} imported</span>}
            </div>
            <div className="card-body">
              <div className="field">
                <label className="label">Paste company names (one per line, or name,domain)</label>
                <textarea
                  className="textarea"
                  rows={6}
                  value={pasted}
                  onChange={(event) => setPasted(event.target.value)}
                  placeholder={"Acme Inc.\nGlobex Corp, globex.com\nInitech"}
                />
              </div>
              <div className="import-actions">
                <button className="btn btn-secondary" onClick={handleImportFromText} disabled={importing || !pasted.trim()}>
                  {importing ? "Importing…" : "Import pasted companies"}
                </button>
                <label className="btn btn-ghost">
                  Upload CSV
                  <input
                    type="file"
                    accept=".csv,text/csv"
                    className="file-input"
                    onChange={(event) => void handleImportFile(event.target.files?.[0] ?? null)}
                  />
                </label>
              </div>
              <p className="muted">CSV format: company_name,domain (first row optional header).</p>
              <div className="import-actions">
                {importing ? <Spinner size={20} /> : null}
                {importedCount !== null && (
                  <Link to={`/campaigns/${campaign.id}`} className="btn btn-primary">
                    Continue to campaign
                  </Link>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Next steps</h2>
            </div>
            <div className="card-body">
              <ol className="step-list">
                <li>Import target companies (above)</li>
                <li>Run the campaign to detect signals, score accounts and generate personalized emails</li>
                <li>Send emails via your connected provider</li>
                <li>Sync engagement to your CRM</li>
              </ol>
              <Link to={`/campaigns/${campaign.id}`} className="btn btn-secondary">
                Go to campaign
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}