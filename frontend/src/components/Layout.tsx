import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "./Toast";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/signals", label: "Signals", icon: "◎" },
  { to: "/accounts", label: "Accounts", icon: "◈" },
  { to: "/campaigns", label: "Campaigns", icon: "◉" },
  { to: "/analytics", label: "Analytics", icon: "◔" },
];

const TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/signals": "Signals",
  "/accounts": "Accounts",
  "/campaigns": "Campaigns",
  "/campaigns/new": "New Campaign",
  "/analytics": "Analytics",
  "/settings": "Settings",
  "/onboarding": "Onboarding",
};

export default function Layout() {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const location = useLocation();

  const title = TITLES[location.pathname] || "OpenSignal";

  async function handleSignOut() {
    await signOut();
    toast("Signed out", "info");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
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
          <h1 className="topbar-title">{title}</h1>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}