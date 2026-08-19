import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { isSupabaseEnabled, supabase } from "../lib/supabase";
import { useToast } from "../components/Toast";

export default function ResetPassword() {
  const { exchange } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      if (!isSupabaseEnabled() || !supabase) {
        throw new Error("Password reset is not available in this configuration.");
      }
      const { error: updateError } = await supabase.auth.updateUser({ password });
      if (updateError) throw new Error(updateError.message);

      const { data } = await supabase.auth.getSession();
      if (!data.session) throw new Error("Session expired. Please request a new reset link.");

      await exchange(data.session.access_token);
      toast("Password updated", "success");
      const done = localStorage.getItem("onboarding_done") === "1";
      navigate(done ? "/dashboard" : "/onboarding", { replace: true });
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
        <h1 className="auth-title">Set a new password</h1>
        <p className="auth-sub">Choose a new password for your account</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="field">
            <label className="label" htmlFor="password">
              New password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="new-password"
              required
              minLength={8}
            />
          </div>
          <div className="field">
            <label className="label" htmlFor="confirm-password">
              Confirm password
            </label>
            <input
              id="confirm-password"
              type="password"
              className="input"
              value={confirm}
              onChange={(event) => setConfirm(event.target.value)}
              autoComplete="new-password"
              required
              minLength={8}
            />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Updating…" : "Update password"}
          </button>
        </form>

        <p className="auth-alt">
          <Link to="/login" className="link">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  );
}