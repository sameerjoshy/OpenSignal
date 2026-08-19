import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { isSupabaseEnabled, supabase } from "../lib/supabase";

export default function AuthCallback() {
  const { exchange } = useAuth();
  const navigate = useNavigate();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const { access_token, refresh_token, type } = parseHash(window.location.hash);

    async function handle() {
      try {
        if (type === "recovery") {
          // Password reset magic link. Establish a Supabase session so the
          // ResetPassword page can set a new password.
          if (isSupabaseEnabled() && supabase && access_token) {
            await supabase.auth.setSession({
              access_token,
              refresh_token: refresh_token ?? "",
            });
          }
          navigate("/reset-password", { replace: true });
          return;
        }
        if (access_token) {
          // Exchange the Supabase access token for an app JWT.
          await exchange(access_token);
          const done = localStorage.getItem("onboarding_done") === "1";
          navigate(done ? "/dashboard" : "/onboarding", { replace: true });
          return;
        }
        navigate("/login", { replace: true });
      } catch {
        navigate("/login", { replace: true });
      }
    }

    void handle();
    window.location.hash = "";
  }, [exchange, navigate]);

  return (
    <div className="page-loading">
      <span className="spinner" style={{ width: 32, height: 32 }} />
      <p className="auth-sub">Completing sign in…</p>
    </div>
  );
}

function parseHash(hash: string): { access_token?: string; refresh_token?: string; type?: string } {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  return {
    access_token: params.get("access_token") || undefined,
    refresh_token: params.get("refresh_token") || undefined,
    type: params.get("type") || undefined,
  };
}