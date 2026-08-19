import { useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "./Toast";
import { useLiveMetrics } from "../hooks/useLiveMetrics";
import { useTheme } from "../hooks/useTheme";

const NAV_GROUPS: { label: string; items: { to: string; label: string; icon: string }[] }[] = [
  {
    label: "Overview",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: "▦" },
      { to: "/analytics", label: "Analytics", icon: "◔" },
      { to: "/outcomes", label: "Outcomes", icon: "◈" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { to: "/signals", label: "Signals", icon: "◎" },
      { to: "/accounts", label: "Accounts", icon: "◈" },
      { to: "/campaigns", label: "Campaigns", icon: "◉" },
      { to: "/learning", label: "Learning", icon: "✦" },
    ],
  },
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

const QUICK_ACTIONS = [
  { label: "New campaign", icon: "◉", to: "/campaigns/new", hint: "n" },
];

export default function Layout() {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggle } = useTheme();
  const { events } = useLiveMetrics();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bellOpen, setBellOpen] = useState(false);
  const [cmdOpen, setCmdOpen] = useState(false);
  const [cmdQuery, setCmdQuery] = useState("");
  const [cmdSel, setCmdSel] = useState(0);
  const cmdRef = useRef<HTMLInputElement>(null);
  const [unread, setUnread] = useState(0);
  const seenRef = useRef(0);

  const title =
    TITLES[location.pathname] ||
    (location.pathname.startsWith("/accounts/")
      ? "Account details"
      : location.pathname.startsWith("/campaigns/")
        ? "Campaign details"
        : "OpenSignal");

  const cmdItems = useMemo(() => {
    const nav = NAV_GROUPS.flatMap((g) => g.items.map((item) => ({ ...item, hint: "" })));
    const items = [...nav, ...QUICK_ACTIONS];
    const q = cmdQuery.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) => item.label.toLowerCase().includes(q) || item.to.includes(q));
  }, [cmdQuery]);

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
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCmdOpen((open) => !open);
        setCmdQuery("");
        setCmdSel(0);
        return;
      }
      if (e.key === "Escape") {
        setDrawerOpen(false);
        setBellOpen(false);
        setCmdOpen(false);
      }
      if (cmdOpen && e.key === "ArrowDown") {
        e.preventDefault();
        setCmdSel((s) => Math.min(s + 1, cmdItems.length - 1));
      }
      if (cmdOpen && e.key === "ArrowUp") {
        e.preventDefault();
        setCmdSel((s) => Math.max(s - 1, 0));
      }
      if (cmdOpen && e.key === "Enter" && cmdItems[cmdSel]) {
        e.preventDefault();
        navigate(cmdItems[cmdSel].to);
        setCmdOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cmdOpen, cmdItems, cmdSel, navigate]);

  useEffect(() => {
    if (cmdOpen) {
      setCmdSel(0);
      setTimeout(() => cmdRef.current?.focus(), 20);
    }
  }, [cmdOpen]);

  async function handleSignOut() {
    try {
      await signOut();
      toast("Signed out", "info");
    } catch {
      toast("Could not sign out. Check your connection.", "error");
    }
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
      {cmdOpen && (
        <div className="cmd-overlay" onClick={() => setCmdOpen(false)}>
          <div className="cmd-palette" onClick={(e) => e.stopPropagation()}>
            <div className="cmd-input-row">
              <span className="nav-icon">⌕</span>
              <input
                ref={cmdRef}
                className="cmd-input"
                placeholder="Jump to a page or action…"
                value={cmdQuery}
                onChange={(e) => {
                  setCmdQuery(e.target.value);
                  setCmdSel(0);
                }}
              />
              <kbd>esc</kbd>
            </div>
            <div className="cmd-list">
              {cmdItems.length === 0 ? (
                <div className="bell-empty">No matches</div>
              ) : (
                cmdItems.map((item, idx) => (
                  <div
                    key={item.to}
                    className={`cmd-item${idx === cmdSel ? " sel" : ""}`}
                    onClick={() => {
                      navigate(item.to);
                      setCmdOpen(false);
                    }}
                    onMouseEnter={() => setCmdSel(idx)}
                  >
                    <span className="cmd-icon">{item.icon}</span>
                    <span>{item.label}</span>
                    {item.hint && <span className="cmd-hint">{item.hint}</span>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <div className={`sidebar-backdrop${drawerOpen ? " show" : ""}`} onClick={() => setDrawerOpen(false)} />
      <aside className={`sidebar${drawerOpen ? " drawer-open" : ""}`}>
        <div className="sidebar-logo">
          <span className="logo-mark">◤</span>
          <span className="logo-text">OpenSignal</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_GROUPS.map((group) => (
            <div key={group.label}>
              <div className="nav-section">{group.label}</div>
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
                >
                  <span className="nav-icon" aria-hidden="true">{item.icon}</span>
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
          <div className="nav-section">Workspace</div>
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
            <button className="btn btn-ghost btn-sm signout-btn" onClick={handleSignOut} title="Sign out" aria-label="Sign out">
              ⎋
              <span className="signout-text">Sign out</span>
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
          <button className="btn btn-secondary btn-sm" onClick={() => setCmdOpen(true)} title="Search & jump (⌘K)">
            <span>⌕</span> Search
            <kbd>⌘K</kbd>
          </button>
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
          <button className="theme-toggle" onClick={toggle} title="Toggle dark mode" aria-label="Toggle dark mode">
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