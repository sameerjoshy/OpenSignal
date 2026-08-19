import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import Analytics from "./pages/Analytics";
import AuthCallback from "./pages/AuthCallback";
import CampaignDetail from "./pages/CampaignDetail";
import Campaigns from "./pages/Campaigns";
import ForgotPassword from "./pages/ForgotPassword";
import Learning from "./pages/Learning";
import Login from "./pages/Login";
import Onboarding from "./pages/Onboarding";
import Outcomes from "./pages/Outcomes";
import ResetPassword from "./pages/ResetPassword";
import SharedOutcomes from "./pages/SharedOutcomes";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Accounts from "./pages/Accounts";
import AccountDetail from "./pages/AccountDetail";
import Signals from "./pages/Signals";
import Settings from "./pages/Settings";
import CampaignBuilder from "./pages/CampaignBuilder";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/shared/:token" element={<SharedOutcomes />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/signals" element={<Signals />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/accounts/:id" element={<AccountDetail />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/campaigns/new" element={<CampaignBuilder />} />
          <Route path="/campaigns/:id" element={<CampaignDetail />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/outcomes" element={<Outcomes />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}