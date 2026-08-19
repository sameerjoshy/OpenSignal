import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "./Toast";
import { useLiveMetrics } from "../hooks/useLiveMetrics";
import { useTheme } from "../hooks/useTheme";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/signals", label: "Signals", icon: "◎" },
  { to: "/accounts", label: "Accounts", icon: "◈" },
  { to: "/campaigns", label: "Campaigns", icon: "◉" },
  { to: "/analytics", label: "Analytics", icon: "◔" },
  { to: "/outcomes", label: "Outcomes", icon: "◈" },
  { to: "/learning", label: "Learning", icon: "✦" },
];

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/signals": "Signals",
  "/accounts": "Accounts",
  "/campaigns": "Campaigns",
  "/campaigns/new": "New Campaign",
  "/analytics": "Analytics",
  "/outcomes": "Outcomes",
  "/learning": "Learning",
  "/settings": "Settings",
  "/onboarding": "Onboarding",
};

const EVENT_ICON: Record<string, string> = {
  email_sent: "✉",
  email_event: "◔",
  account_scored: "◈",
  campaign_run: "◉",
  reply_classified: "↩",
};

function eventName(e: { type: string; payload: Record<string, unknown> }): string {
  const p = e.payload;
  if (p.company_name) return String(p.company_name);
  if (p.from_email) return String(p.from_email);
  if (p.to_email) return String(p.to_email);
  return e.type.replace(/_/g, " ");
}

export default function Layout() {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const location = useLocation();
  const { theme, toggle } = useTheme();
  const { events } = useLiveMetrics();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bellOpen, setBellOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const seenRef = useRef(0);

  const title = TITLES[location.pathname] || "OpenSignal";

  // Count events that arrived since the last time the bell was opened.
  useEffect(() => {
    if (events.length > seenRef.current) {
      setUnread(events.length - seenRef.current);
    }
  }, [events]);

  useEffect(() => {
    setDrawerOpen(false);
    setBellOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setDrawerOpen(false);
        setBellOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  async function handleSignOut() {
    await signOut();
    toast("Signed out", "info");
  }

  function openBell() {
    setBellOpen((open) => {
      const next = !open;
      if (next) {
        seenRef.current = events.length;
        setUnread(0);
      }
      return next;
    });
  }

  const recent = events.slice(-8).reverse();

  return (
    <div className="app-shell">
      <div className={`sidebar-backdrop${drawerOpen ? " show" : ""}`} onClick={() => setDrawerOpen(false)} />
      <aside className={`sidebar${drawerOpen ? " drawer-open" : ""}`}>
        <div className="sidebar-logo">
          <span className="logo-mark">◤</span>
          <span className="logo-text">OpenSignal</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
          <NavLink
            to="/settings"
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            <span className="nav-icon">⚙</span>
            Settings
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip">
            <div className="user-avatar">{(user?.full_name || user?.email || "U").slice(0, 1).toUpperCase()}</div>
            <div className="user-meta">
              <div className="user-name">{user?.full_name || user?.email}</div>
              <div className="user-plan">{user?.plan} plan</div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={handleSignOut} title="Sign out">
              ⎋
            </button>
          </div>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <button className="hamburger" onClick={() => setDrawerOpen(true)} aria-label="Open menu">
            ☰
          </button>
          <h1 className="topbar-title">{title}</h1>
          <div className="bell-wrap">
            <button className="bell" onClick={openBell} aria-label="Notifications">
              🔔
              {unread > 0 && <span className="bell-dot" />}
            </button>
            {bellOpen && (
              <div className="bell-pop">
                <div className="bell-pop-head">
                  <span>Live activity</span>
                  <span className="muted">{events.length} events</span>
                </div>
                <div className="bell-pop-list">
                  {recent.length === 0 ? (
                    <div className="bell-empty">No activity yet — send emails or score accounts and it streams here.</div>
                  ) : (
                    recent.map((event, idx) => (
                      <div key={`${event.type}-${idx}`} className="bell-pop-item">
                        <span className="bell-icon">{EVENT_ICON[event.type] ?? "•"}</span>
                        <div className="bell-text">
                          <strong>{eventName(event)}</strong>
                          <div className="muted">{event.type.replace(/_/g, " ")}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <button className="theme-toggle" onClick={toggle} title="Toggle dark mode">
            {theme === "dark" ? "☀" : "☾"}
          </button>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}