import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      await api.post("/api/v1/auth/forgot-password", { email });
      setMessage("If that email is registered, a reset link has been sent.");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <img className="app-logo" src="/logo.png" alt="Signal360" width="26" height="26" />
          <span className="logo-text">Signal360</span>
        </div>
        <h1 className="auth-title">Reset password</h1>
        <p className="auth-sub">Enter your email to receive a reset link</p>

        {message && <div className="alert alert-info">{message}</div>}
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="field">
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="input"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Sending…" : "Send reset link"}
          </button>
        </form>

        <p className="auth-alt">
          <Link to="/login" className="link">Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}