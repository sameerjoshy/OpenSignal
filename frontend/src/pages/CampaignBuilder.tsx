import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useToast } from "../components/Toast";
import Spinner from "../components/Spinner";
import { parseCompaniesText, parseCompanyCsv, type CompanyRow } from "../utils/csv";
import type { Campaign } from "../types";

type Step = 1 | 2 | 3 | 4;

export default function CampaignBuilder() {
  const { toast } = useToast();

  const [step, setStep] = useState<Step>(1);
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

  const nameHint = name.trim().length === 0 ? null : name.trim().length < 4 ? "More descriptive names are easier to find later." : "Looks good. Clear and ready to go.";

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
      setStep(4);
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

  const parsedCount = pasted.trim() ? parseCompaniesText(pasted).length : 0;

  return (
    <div className="stack stack-narrow">
      {/* Progress steps */}
      <ol className="builder-steps" aria-label="Campaign builder progress">
        {(["Goal", "Targets", "Route", "Done"] as const).map((label, i) => {
          const n = (i + 1) as Step;
          const state = n === step ? "active" : n < step || step === 4 ? "done" : "";
          return (
            <li key={label} className={`builder-step ${state}`}>
              <span className="builder-step-dot">{step === 4 || n < step ? "✓" : n}</span>
              <span className="builder-step-label">{label}</span>
            </li>
          );
        })}
      </ol>

      {step === 1 && (
        <div className="card">
          <div className="card-body">
            <h2 className="card-title">What's your campaign about?</h2>
            <p className="card-sub">Give it a name — the rest gets configured automatically.</p>
            <div className="field">
              <label className="label" htmlFor="campaign-name">Campaign name</label>
              <input
                id="campaign-name"
                className="input input-lg"
                autoFocus
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. H2 ABM — Series B funded startups"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && name.trim()) setStep(2);
                }}
              />
              {nameHint && (
                <p className={`input-hint ${nameHint === "Looks good. Clear and ready to go." ? "hint-ok" : ""}`}>
                  {nameHint === "Looks good. Clear and ready to go." ? "✓ " : ""}
                  {nameHint}
                </p>
              )}
              <p className="input-help">Type like this: "H2 ABM for tech leaders" · "Series B funded startups"</p>
            </div>
            <div className="field">
              <label className="label" htmlFor="campaign-desc">Product context (optional)</label>
              <textarea
                id="campaign-desc"
                className="textarea"
                rows={2}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Used to personalize emails, e.g. 'We sell revenue intelligence for GTM teams.'"
              />
            </div>
            <div className="builder-actions">
              <button className="btn btn-primary" disabled={!name.trim()} onClick={() => setStep(2)}>
                Next →
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="card">
          <div className="card-body">
            <h2 className="card-title">Add your target accounts</h2>
            <p className="card-sub">Paste company names or upload a CSV. We'll detect and score them automatically.</p>
            <div className="field">
              <label className="label" htmlFor="targets">Company names</label>
              <textarea
                id="targets"
                className="textarea"
                rows={6}
                value={pasted}
                onChange={(event) => setPasted(event.target.value)}
                placeholder={"Acme Inc.\nGlobex Corp, globex.com\nInitech"}
              />
              {pasted.trim() && parsedCount > 0 && (
                <p className="input-hint hint-ok">✓ Detected {parsedCount} compan{parsedCount === 1 ? "y" : "ies"}</p>
              )}
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
            <div className="builder-actions">
              <button className="btn btn-ghost" onClick={() => setStep(1)}>
                ← Back
              </button>
              {importedCount !== null ? (
                <button className="btn btn-primary" onClick={() => setStep(3)}>
                  Route & launch →
                </button>
              ) : (
                <button className="btn btn-primary" disabled onClick={() => undefined} title="Import companies first">
                  Route & launch →
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {step === 3 && campaign && (
        <div className="card">
          <div className="card-body">
            <h2 className="card-title">Route & launch</h2>
            <p className="card-sub">Set who gets what, then launch — everything else happens on autopilot.</p>

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
              <p className="input-help">1 = single email · 3 = nudge sequence · 5 = full pursuit</p>
            </div>

            <div className="summary-box">
              <div className="summary-row">
                <span>Campaign</span>
                <strong>{name}</strong>
              </div>
              <div className="summary-row">
                <span>Companies</span>
                <strong>{importedCount ?? 0} imported</strong>
              </div>
              <div className="summary-row">
                <span>Routing</span>
                <strong>{Object.entries(tierFilters).filter(([, v]) => v).map(([t]) => `Tier ${t}`).join(", ")}</strong>
              </div>
              <div className="summary-row">
                <span>Cadence</span>
                <strong>{cadenceSteps} step{cadenceSteps === 1 ? "" : "s"}</strong>
              </div>
            </div>

            <div className="builder-actions">
              <button className="btn btn-ghost" onClick={() => setStep(2)}>
                ← Back
              </button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={creating}>
                {creating ? <Spinner size={18} /> : "🚀 Create & launch"}
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 4 && campaign && (
        <div className="card success-card">
          <div className="card-body">
            <div className="success-icon">✓</div>
            <h2 className="card-title">Campaign created!</h2>
            <p className="card-sub">
              <strong>{name}</strong> is live with {importedCount ?? 0} target accounts. Signal detection and scoring are running in the background.
            </p>
            <div className="builder-actions builder-actions-center">
              <Link className="btn btn-primary" to={`/campaigns/${campaign.id}`}>
                View campaign
              </Link>
              <button className="btn btn-secondary" onClick={() => window.location.reload()}>
                + Add another
              </button>
            </div>
            <p className="muted-note">
              Tip: connect data sources in Settings to keep the signal feed flowing.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}