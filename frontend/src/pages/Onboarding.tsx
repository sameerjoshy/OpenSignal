import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import Modal from "../components/Modal";
import Spinner from "../components/Spinner";
import { useToast } from "../components/Toast";
import type { ServiceStatus } from "../types";

interface FieldDef {
  key: string;
  label: string;
  placeholder: string;
  secret?: boolean;
  multiline?: boolean;
  target: "api_key" | string;
}

const SERVICE_FIELDS: Record<string, FieldDef[]> = {
  apollo: [{ key: "api_key", label: "Apollo API key", placeholder: "apollo-…", secret: true, target: "api_key" }],
  hunter: [{ key: "api_key", label: "Hunter API key", placeholder: "hunter-…", secret: true, target: "api_key" }],
  newsapi: [{ key: "api_key", label: "NewsAPI key", placeholder: "…", secret: true, target: "api_key" }],
  mailgun: [
    { key: "api_key", label: "Mailgun API key", placeholder: "key-…", secret: true, target: "api_key" },
    { key: "domain", label: "Sending domain", placeholder: "mg.example.com", target: "config.domain" },
  ],
  sendgrid: [{ key: "api_key", label: "SendGrid API key", placeholder: "SG.…", secret: true, target: "api_key" }],
  hubspot: [{ key: "api_key", label: "HubSpot private app token", placeholder: "pat-…", secret: true, target: "api_key" }],
  salesforce: [
    { key: "client_id", label: "Client ID", placeholder: "…", target: "api_key" },
    { key: "client_secret", label: "Client secret", placeholder: "…", secret: true, target: "config.client_secret" },
    { key: "username", label: "Username", placeholder: "you@company.com", target: "config.username" },
    { key: "password", label: "Password", placeholder: "…", secret: true, target: "config.password" },
  ],
  ga4: [
    {
      key: "service_account_json",
      label: "Service account JSON",
      placeholder: '{ "type": "service_account", … }',
      multiline: true,
      target: "config.service_account_json",
    },
    { key: "property_id", label: "GA4 property ID", placeholder: "123456789", target: "config.property_id" },
  ],
  sec_edgar: [],
  deepseek: [],
};

const STEPS = [
  { id: 1, title: "Workspace", description: "Tell us about your company" },
  { id: 2, title: "Connect", description: "Link your data and channels" },
  { id: 3, title: "Launch", description: "Ready to find signals" },
];

export default function Onboarding() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(0);
  const [company, setCompany] = useState("");
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loadingServices, setLoadingServices] = useState(false);
  const [connectTarget, setConnectTarget] = useState<ServiceStatus | null>(null);
  const [connectValues, setConnectValues] = useState<Record<string, string>>({});
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    void loadServices();
  }, []);

  async function loadServices() {
    setLoadingServices(true);
    try {
      const result = await api.get<ServiceStatus[]>("/api/v1/settings/services");
      setServices(result);
    } catch {
      // Non-fatal during onboarding.
    } finally {
      setLoadingServices(false);
    }
  }

  function openConnect(service: ServiceStatus) {
    setConnectTarget(service);
    setConnectValues({});
  }

  async function handleConnect() {
    if (!connectTarget) return;
    setConnecting(true);
    try {
      const fields = SERVICE_FIELDS[connectTarget.service] || [];
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

  function finish() {
    localStorage.setItem("onboarding_done", "1");
    navigate("/dashboard", { replace: true });
  }

  const connectedCount = services.filter((s) => s.connected).length;

  return (
    <div className="onboarding">
      <div className="onboarding-header">
        <div className="auth-logo">
          <span className="logo-mark">◤</span>
          <span className="logo-text">OpenSignal</span>
        </div>
      </div>

      <div className="onboarding-steps">
        {STEPS.map((item, index) => (
          <div key={item.id} className={`step${index === step ? " active" : ""}${index < step ? " done" : ""}`}>
            <span className="step-dot">{index < step ? "✓" : item.id}</span>
            <div className="step-text">
              <div className="step-title">{item.title}</div>
              <div className="step-desc">{item.description}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="onboarding-card card">
        {step === 0 && (
          <div className="onboarding-body">
            <h2>Welcome{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}</h2>
            <p className="muted">Let&apos;s set up your workspace.</p>
            <div className="field">
              <label className="label" htmlFor="company">
                Company name
              </label>
              <input
                id="company"
                className="input"
                value={company}
                onChange={(event) => setCompany(event.target.value)}
                placeholder="Acme Inc."
              />
            </div>
            <div className="onboarding-actions">
              <button className="btn btn-primary" disabled={!company.trim()} onClick={() => setStep(1)}>
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="onboarding-body">
            <h2>Connect your services</h2>
            <p className="muted">Optional — you can add these later in Settings.</p>
            {loadingServices ? (
              <Spinner size={28} />
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
                    <div className="service-actions">
                      {service.connected ? (
                        <>
                          <button className="btn btn-secondary btn-sm" onClick={() => handleTest(service)}>
                            Test
                          </button>
                          <button className="btn btn-ghost btn-sm" onClick={() => openConnect(service)}>
                            Reconnect
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
            <div className="onboarding-actions">
              <button className="btn btn-ghost" onClick={() => setStep(0)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={() => setStep(2)}>
                {connectedCount > 0 ? `Continue (${connectedCount} connected)` : "Skip"}
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="onboarding-body">
            <h2>You&apos;re ready</h2>
            <p className="muted">
              OpenSignal will watch your connected data sources for buying intent, score target accounts, and help you
              launch personalized outreach campaigns.
            </p>
            <ul className="check-list">
              <li>Signal detection from Apollo, NewsAPI, SEC EDGAR and more</li>
              <li>AI scoring with DeepSeek</li>
              <li>Personalized email generation and sending</li>
              <li>CRM sync to HubSpot or Salesforce</li>
            </ul>
            <div className="onboarding-actions">
              <button className="btn btn-ghost" onClick={() => setStep(1)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={finish}>
                Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>

      <Modal
        open={connectTarget !== null}
        title={`Connect ${connectTarget?.name || ""}`}
        onClose={() => setConnectTarget(null)}
        footer={
          <>
            <button className="btn btn-ghost" onClick={() => setConnectTarget(null)}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleConnect} disabled={connecting}>
              {connecting ? "Saving…" : "Connect"}
            </button>
          </>
        }
      >
        {connectTarget && (
          <div className="connect-form">
            {(SERVICE_FIELDS[connectTarget.service] || []).map((field) => (
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
            ))}
            {(SERVICE_FIELDS[connectTarget.service] || []).length === 0 && (
              <p className="muted">This service is configured via environment variables. Use Test to verify it.</p>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}