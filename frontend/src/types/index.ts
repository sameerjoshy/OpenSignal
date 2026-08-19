export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  plan: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ServiceStatus {
  service: string;
  name: string;
  description: string;
  free_tier_note: string;
  connected: boolean;
  source: "user" | "env" | "none";
  validated_at?: string | null;
}

export interface ServiceTestResult {
  service: string;
  ok: boolean;
  message: string;
  quota?: Record<string, unknown> | null;
}

export interface Account {
  id: string;
  company_name: string;
  domain?: string | null;
  industry?: string | null;
  employee_count?: number | null;
  revenue?: number | null;
  location?: string | null;
  website?: string | null;
  score?: number | null;
  tier?: number | null;
  score_rationale?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Signal {
  id: string;
  account_id: string;
  source: string;
  signal_type: string;
  title: string;
  description?: string | null;
  url?: string | null;
  detected_at: string;
  created_at: string;
  account_name?: string | null;
  account_tier?: number | null;
  account_score?: number | null;
}

export interface Campaign {
  id: string;
  name: string;
  description?: string | null;
  status: "draft" | "active" | "paused" | "completed" | "archived";
  tier_filters?: Record<string, unknown> | null;
  channels?: Record<string, unknown> | null;
  cadence?: Record<string, unknown> | null;
  last_run_at?: string | null;
  run_log?: string | null;
  created_at: string;
  updated_at: string;
  account_count?: number;
  sent_count?: number;
  open_count?: number;
  click_count?: number;
  reply_count?: number;
}

export interface CampaignAccount {
  id: string;
  campaign_id: string;
  account_id: string;
  contact_email?: string | null;
  status: string;
  tier?: number | null;
  score?: number | null;
  error?: string | null;
  created_at: string;
  account?: Account | null;
}

export interface EmailMessage {
  id: string;
  campaign_id?: string | null;
  account_id?: string | null;
  subject: string;
  body_text: string;
  status: string;
  from_email?: string | null;
  to_email: string;
  provider?: string | null;
  sequence_step: number;
  sent_at?: string | null;
  opened_at?: string | null;
  clicked_at?: string | null;
  replied_at?: string | null;
  created_at: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  sequence_step: number;
  is_default: boolean;
  created_at: string;
}

export interface CrmSync {
  id: string;
  campaign_id?: string | null;
  account_id?: string | null;
  service: string;
  status: string;
  object_type?: string | null;
  external_id?: string | null;
  error_message?: string | null;
  synced_at?: string | null;
  created_at: string;
}

export interface MetricPoint {
  label: string;
  value: number;
}

export interface FunnelStep {
  label: string;
  value: number;
}

export interface Analytics {
  total_signals: number;
  total_accounts: number;
  total_campaigns: number;
  emails_sent: number;
  emails_opened: number;
  emails_clicked: number;
  emails_replied: number;
  active_campaigns: number;
  signals_this_week: number;
  top_sources: MetricPoint[];
  signals_by_tier: MetricPoint[];
  funnel: FunnelStep[];
  weekly_activity: MetricPoint[];
}

export interface Outcomes {
  pipeline_value: number;
  pipeline_by_tier: MetricPoint[];
  accounts_scored: number;
  signals_detected: number;
  deals_estimate: number;
  time_saved_hours: number;
  labor_value: number;
  reply_rate: number;
  open_rate: number;
  click_rate: number;
  industry_reply_rate: number;
  engagement_lift_pct: number;
  cost_per_meeting: number;
  monthly_forecast: number;
  forecast_growth_pct: number;
  note: string;
}

export interface InsightItem {
  label: string;
  detail: string;
  value: string;
}

export interface Learning {
  top_attributes: InsightItem[];
  signal_performance: InsightItem[];
  email_tactics: InsightItem[];
  recommendations: InsightItem[];
}

export interface EmailReply {
  id: string;
  from_email: string;
  subject?: string | null;
  body: string;
  classification: string;
  confidence?: number | null;
  summary?: string | null;
  suggested_reply?: string | null;
  auto_reply_sent: boolean;
  status: string;
  created_at: string;
  company_name?: string | null;
  original_subject?: string | null;
}

export interface LiveEvent {
  type: string;
  payload: Record<string, unknown>;
}