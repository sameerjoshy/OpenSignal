import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Spinner from "../components/Spinner";
import EmptyState from "../components/EmptyState";
import { useToast } from "../components/Toast";
import type { DigestPreview, Learning } from "../types";

function InsightList({ title, items, empty }: { title: string; items: { label: string; detail: string; value: string }[]; empty: string }) {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{title}</h2>
      </div>
      <div className="card-body">
        {items.length === 0 ? (
          <EmptyState title={empty} description="Insights will accumulate as you run campaigns." />
        ) : (
          <ul className="insight-list">
            {items.map((item) => (
              <li key={item.label} className="insight-item">
                <div className="insight-head">
                  <div className="insight-label">{item.label}</div>
                  <span className="insight-tag">{item.value}</span>
                </div>
                <div className="insight-detail">{item.detail}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function LearningPage() {
  const [data, setData] = useState<Learning | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<DigestPreview | null>(null);
  const [sending, setSending] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    async function load() {
      setError(null);
      try {
        setData(await api.get<Learning>("/api/v1/analytics/learning"));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load insights");
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, []);

  async function loadPreview() {
    try {
      setPreview(await api.get<DigestPreview>("/api/v1/digest/preview"));
      toast("Preview ready", "success");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  }

  async function sendDigest() {
    setSending(true);
    try {
      const result = await api.post<{ ok: boolean; message: string }>("/api/v1/digest/send");
      toast(result.message, result.ok ? "success" : "error");
    } catch (err) {
      toast((err as Error).message, "error");
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="stack">
        <div className="alert alert-error">{error}</div>
      </div>
    );
  }

  if (!data) {
    return <EmptyState title="No insights yet" description="Insights will appear as you run campaigns." />;
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">What to do next</h2>
        </div>
        <div className="card-body">
          {data.recommendations.length === 0 ? (
            <EmptyState title="No recommendations yet" description="Send more campaigns to generate recommendations." />
          ) : (
            <ol className="recommendation-list">
              {data.recommendations.map((rec) => (
                <li key={rec.label} className="recommendation-item">
                  <div className="recommendation-title">{rec.label}</div>
                  <div className="recommendation-detail">{rec.detail}</div>
                  <span className="recommendation-tag">{rec.value}</span>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>

      <div className="card-grid">
        <InsightList title="Top-converting attributes" items={data.top_attributes} empty="No engaged accounts yet" />
        <InsightList title="Signal performance" items={data.signal_performance} empty="No signals yet" />
      </div>

      <div className="card-grid">
        <InsightList title="Email tactics" items={data.email_tactics} empty="No emails sent yet" />
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Why this matters</h2>
          </div>
          <div className="card-body">
            <p className="muted-note">
              Signal360 learns from every signal, email, and reply. Use these insights to prioritize Tier-1
              accounts, time your sends, and double down on what converts.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Weekly digest</h2>
          <div className="action-bar" style={{ margin: 0 }}>
            <button className="btn btn-secondary btn-sm" onClick={() => void loadPreview()}>
              Preview
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => void sendDigest()} disabled={sending}>
              {sending ? "Sending…" : "Email me weekly insights"}
            </button>
          </div>
        </div>
        <div className="card-body">
          {preview ? (
            <>
              <div className="timeline-title">{preview.subject}</div>
              <pre className="digest-pre">{preview.text}</pre>
            </>
          ) : (
            <p className="muted-note">
              Send a Friday wrap-up of your signals, pipeline value, and what Signal360 learned to your inbox.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}