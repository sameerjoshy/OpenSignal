import React from "react";

const PROOF_POINTS = [
  { icon: "◎", text: "Surfaces Tier-1 buyer intent signals across 8+ data sources" },
  { icon: "✉", text: "Personalized AI outbound that reads like a human, at scale" },
  { icon: "↩", text: "Auto-classified replies with follow-up timing built in" },
  { icon: "◉", text: "Pipeline forecasting, ROI and stakeholder-ready reporting" },
];

export default function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-panel-brand">
          <img className="app-logo" src="/logo.png" alt="Signal360" width="26" height="26" />
          <span className="logo-text">Signal360</span>
        </div>
        <div>
          <h2>Signal-based demand generation for revenue teams</h2>
          <p className="lead">
            Turn buyer intent into pipeline. Signal360 finds accounts showing buying signals, personalizes
            outreach, and measures the outcomes that matter.
          </p>
        </div>
        <div className="proof">
          {PROOF_POINTS.map((p) => (
            <div key={p.icon} className="proof-item">
              <span className="proof-icon">{p.icon}</span>
              <span>{p.text}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="auth-col">{children}</div>
    </div>
  );
}