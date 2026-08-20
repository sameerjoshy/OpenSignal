import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import Modal from "../components/Modal";
import ConfirmDialog, { type ConfirmState } from "../components/Confirm";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/Toast";
import { serviceFields, hasRequiredInput } from "../lib/serviceFields";
import type { EmailTemplate, ServiceStatus } from "../types";

type Tab = "services" | "templates" | "account" | "quota";

function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const { toast } = useToast();
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied to clipboard", "success");
    } catch {
      toast("Copy failed", "error");
    }
  }
  return (
    <button className="btn btn-ghost btn-sm" onClick={() => void copy()} title={`Copy ${label.toLowerCase()}`}>
      ⧉ {label}
    </button>
  );
}

const TABS: Tab[] = ["services", "templates", "account", "quota"];

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const { toast } = useToast();
  const [tab, setTab] = useState<Tab>("services");

  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loadingServices, setLoadingServices] = useState(false);
  const [connectTarget, setConnectTarget] = useState<ServiceStatus | null>(null);
  const [connectValues, setConnectValues] = useState<Record<string, string>>({});
  const [connecting, setConnecting] = useState(false);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);

  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [templateModal, setTemplateModal] = useState(false);
  const [templateForm, setTemplateForm] = useState({ name: "", subject: "", body: "", sequence_step: 1 });

  const [quota, setQuota] = useState<{ service: string; name: string; note: string; usage?: number | null }[]>([]);
  const [fullName, setFullName] = useState(user?.full_name || "");

  const loadServices = useCallback(async () => {
    setLoadingServices(true);
    try {
      const result = await api.get<ServiceStatus[]>("/api/v1/settings/services");
      setServices(result);
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setLoadingServices(false);
    }
  }, [toast]);

  const loadTemplates = useCallback(async () => {
    setLoadingTemplates(true);
    try {
      const result = await api.get<EmailTemplate[]>("/api/v1/email/templates");
      setTemplates(result);
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setLoadingTemplates(false);
    }
  }, [toast]);

  const loadQuota = useCallback(async () => {
    try {
      const result = await api.get<{ service: string; name: string; note: string; usage?: number | null }[]>(
        "/api/v1/settings/quota"
      );
      setQuota(result);
    } catch {
      // non-fatal
    }
  }, []);

  useEffect(() => {
    if (tab === "services") void loadServices();
    if (tab === "templates") void loadTemplates();
    if (tab === "quota") void loadQuota();
  }, [tab, loadServices, loadTemplates, loadQuota]);

  function openConnect(service: ServiceStatus) {
    setConnectTarget(service);
    setConnectValues({});
  }

  async function handleConnect() {
    if (!connectTarget) return;
    setConnecting(true);
    try {
      const fields = serviceFields(connectTarget.service);
      const payload: { service: string; api_key?: string; config?: Record<string, string> } = {
        service: connectTarget.service,
      };
      for (const field of fields) {
        const value = connectValues[field.key]?.trim() ?? "";
        if (!value) continue;
        if (field.target === "api_key") {
          payload.api_key = value;
        } else {
          payload.config = { ...payload.config, [field.target.replace("config.", "")]: value };
        }
      }
      await api.post("/api/v1/settings/services", payload);
      toast(`${connectTarget.name} connected`, "success");
      setConnectTarget(null);
      await loadServices();
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setConnecting(false);
    }
  }

  async function handleTest(service: ServiceStatus) {
    try {
      const result = await api.post<{ ok: boolean; message: string }>(`/api/v1/settings/services/${service.service}/test`);
      toast(`${service.name}: ${result.message}`, result.ok ? "success" : "error");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function handleDisconnect(service: ServiceStatus) {
    try {
      await api.delete(`/api/v1/settings/services/${service.service}`);
      toast(`${service.name} disconnected`, "info");
      await loadServices();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function createTemplate() {
    try {
      await api.post("/api/v1/email/templates", templateForm);
      toast("Template created", "success");
      setTemplateModal(false);
      setTemplateForm({ name: "", subject: "", body: "", sequence_step: 1 });
      await loadTemplates();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function deleteTemplate(template: EmailTemplate) {
    try {
      await api.delete(`/api/v1/email/templates/${template.id}`);
      toast("Template deleted", "info");
      await loadTemplates();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function updateProfile() {
    try {
      await api.patch("/api/v1/settings/account", { full_name: fullName });
      await refreshUser();
      toast("Profile updated", "success");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  return (
    <div className="settings-layout">
      <div className="settings-tabs" role="tablist" aria-label="Settings sections">
        {TABS.map((t) => (
          <button
            key={t}
            className={`settings-tab${tab === t ? " active" : ""}`}
            role="tab"
            aria-selected={tab === t}
            aria-controls={`tab-${t}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "services" && (
        <div className="stack" role="tabpanel" id="tab-services">
          <div className="page-head" style={{ marginBottom: 8 }}>
            <div>
              <h1 className="page-title">Connected services</h1>
              <p className="page-desc">Wire up your data sources, sending infrastructure and CRM.</p>
            </div>
          </div>
          {loadingServices ? (
            <div className="page-loading">
              <Spinner />
            </div>
          ) : (
            <div className="service-grid">
              {services.map((service) => (
                <div key={service.service} className={`service-card${service.connected ? " connected" : ""}`}>
                  <div className="service-card-header">
                    <strong>{service.name}</strong>
                    <span className={`badge ${service.connected ? "badge-connected" : "badge-muted"}`}>
                      {service.connected ? "Connected" : "Not connected"}
                    </span>
                  </div>
                  <p className="service-desc">{service.description}</p>
                  <p className="service-note">
                    {service.keyless ? "No API key needed · Public API" : service.free_tier_note}
                    {!service.keyless && ` · source: ${service.source}`}
                  </p>
                  <div className="service-actions">
                    {service.keyless ? (
                      <button className="btn btn-secondary btn-sm" onClick={() => handleTest(service)}>
                        Verify connection
                      </button>
                    ) : service.connected ? (
                      <>
                        <button className="btn btn-secondary btn-sm" onClick={() => handleTest(service)}>
                          Test
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => openConnect(service)}>
                          Reconnect
                        </button>
                        <button
                          className="btn btn-ghost btn-sm btn-danger-text"
                          onClick={() =>
                            setConfirm({
                              title: `Disconnect ${service.name}?`,
                              message: `Credentials will be removed and ${service.name} will stop syncing. You can reconnect anytime.`,
                              confirmLabel: "Disconnect",
                              danger: true,
                              onConfirm: () => void handleDisconnect(service),
                            })
                          }
                        >
                          Disconnect
                        </button>
                      </>
                    ) : (
                      <button className="btn btn-secondary btn-sm" onClick={() => openConnect(service)}>
                        Connect
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "templates" && (
        <div className="stack" role="tabpanel" id="tab-templates">
          <div className="filter-bar">
            <div className="filter-spacer" />
            <button className="btn btn-primary" onClick={() => setTemplateModal(true)}>
              + New template
            </button>
          </div>
          {loadingTemplates ? (
            <div className="page-loading">
              <Spinner />
            </div>
          ) : templates.length === 0 ? (
            <div className="card">
              <div className="card-body">
                <p className="muted">No templates yet. Templates personalize follow-up sequences.</p>
              </div>
            </div>
          ) : (
            <div className="card">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Subject</th>
                    <th>Step</th>
                    <th>Default</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {templates.map((template) => (
                    <tr key={template.id}>
                      <td className="cell-title">{template.name}</td>
                      <td>{template.subject}</td>
                      <td>{template.sequence_step}</td>
                      <td>{template.is_default ? "Yes" : "—"}</td>
                      <td>
                        <button
                          className="btn btn-ghost btn-sm btn-danger-text"
                          onClick={() =>
                            setConfirm({
                              title: `Delete template "${template.name}"?`,
                              message: "This cannot be undone. Campaigns already using it keep their generated emails.",
                              confirmLabel: "Delete",
                              danger: true,
                              onConfirm: () => void deleteTemplate(template),
                            })
                          }
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {tab === "account" && (
        <div className="card stack-narrow" role="tabpanel" id="tab-account">
          <div className="card-body">
            <div className="field">
              <label className="label">Full name</label>
              <input className="input" value={fullName} onChange={(event) => setFullName(event.target.value)} />
            </div>
            <div className="field">
              <label className="label">Email</label>
              <div className="action-bar">
                <input className="input" value={user?.email || ""} disabled />
                <CopyButton text={user?.email || ""} label="Copy" />
              </div>
            </div>
            <div className="field">
              <label className="label">Plan</label>
              <input className="input" value={user?.plan || ""} disabled />
            </div>
            <button className="btn btn-primary" onClick={updateProfile}>
              Save profile
            </button>
          </div>
        </div>
      )}

      {tab === "quota" && (
        <div className="card" role="tabpanel" id="tab-quota">
          <div className="card-header">
            <h2 className="card-title">Free tier usage</h2>
          </div>
          <div className="card-body">
            <ul className="source-list">
              {quota.map((item) => (
                <li key={item.service} className="source-row">
                  <span className="source-name">
                    {item.name} <span className="muted">· {item.note}</span>
                  </span>
                  <span className="source-count">{item.usage ?? "—"}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <Modal
        open={connectTarget !== null}
        title={`Connect ${connectTarget?.name || ""}`}
        onClose={() => setConnectTarget(null)}
        footer={
          <>
            <button className="btn btn-ghost" onClick={() => setConnectTarget(null)}>
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={handleConnect}
              disabled={connecting || !hasRequiredInput(connectTarget?.service || "", connectValues)}
            >
              {connecting ? "Saving…" : "Save"}
            </button>
          </>
        }
      >
        {connectTarget && (
          <div className="connect-form">
            {serviceFields(connectTarget.service).length === 0 ? (
              <p className="muted">
                {connectTarget.keyless
                  ? "This service is free and needs no API key. Use Verify connection to check it."
                  : "This service is configured via your workspace environment. Add an API key to manage it here."}
              </p>
            ) : (
              serviceFields(connectTarget.service).map((field) => (
                <div className="field" key={field.key}>
                  <label className="label" htmlFor={field.key}>
                    {field.label}
                  </label>
                  {field.multiline ? (
                    <textarea
                      id={field.key}
                      className="textarea"
                      rows={5}
                      value={connectValues[field.key] || ""}
                      onChange={(event) => setConnectValues({ ...connectValues, [field.key]: event.target.value })}
                      placeholder={field.placeholder}
                      autoComplete="off"
                    />
                  ) : (
                    <input
                      id={field.key}
                      type={field.secret ? "password" : "text"}
                      className="input"
                      value={connectValues[field.key] || ""}
                      onChange={(event) => setConnectValues({ ...connectValues, [field.key]: event.target.value })}
                      placeholder={field.placeholder}
                      autoComplete="off"
                    />
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </Modal>

      <Modal
        open={templateModal}
        title="New email template"
        onClose={() => setTemplateModal(false)}
        footer={
          <>
            <button className="btn btn-ghost" onClick={() => setTemplateModal(false)}>
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={createTemplate}
              disabled={!templateForm.name.trim() || !templateForm.subject.trim() || !templateForm.body.trim()}
            >
              Create
            </button>
          </>
        }
      >
        <div className="field">
          <label className="label">Name</label>
          <input className="input" value={templateForm.name} onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })} />
        </div>
        <div className="field">
          <label className="label">Subject</label>
          <input className="input" value={templateForm.subject} onChange={(e) => setTemplateForm({ ...templateForm, subject: e.target.value })} />
        </div>
        <div className="field">
          <label className="label">Body</label>
          <textarea className="textarea" rows={6} value={templateForm.body} onChange={(e) => setTemplateForm({ ...templateForm, body: e.target.value })} />
        </div>
        <div className="field">
          <label className="label">Sequence step</label>
          <input
            className="input"
            type="number"
            min={1}
            value={templateForm.sequence_step}
            onChange={(e) => setTemplateForm({ ...templateForm, sequence_step: Number(e.target.value) || 1 })}
          />
        </div>
      </Modal>

      <ConfirmDialog state={confirm} onClose={() => setConfirm(null)} />
    </div>
  );
}