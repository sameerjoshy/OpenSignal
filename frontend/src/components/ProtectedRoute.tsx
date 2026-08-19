import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Spinner from "./Spinner";

export default function ProtectedRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="page-loading">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const onboardingDone = localStorage.getItem("onboarding_done") === "1";
  const isOnboarding = location.pathname === "/onboarding";
  if (!onboardingDone && !isOnboarding) {
    return <Navigate to="/onboarding" state={{ from: location }} replace />;
  }
  if (onboardingDone && isOnboarding) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}