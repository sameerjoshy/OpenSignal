-- OpenSignal: Supabase migration 001 - initial schema
-- Apply via: supabase db push  (or paste into the Supabase SQL editor)

-- ============================================================
-- EXTENSIONS
-- ============================================================
create extension if not exists "pgcrypto";

-- ============================================================
-- USERS
-- ============================================================
create table if not exists users (
  id                uuid primary key default gen_random_uuid(),
  email             text not null unique,
  full_name         text,
  password_hash     text,
  supabase_auth_id  text unique,
  plan              text not null default 'free',
  is_active         boolean not null default true,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

-- ============================================================
-- SERVICE CREDENTIALS (API keys stored encrypted by the backend)
-- ============================================================
create table if not exists service_credentials (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  service           text not null,
  encrypted_key     text not null,
  config            jsonb,
  is_active         boolean not null default true,
  validated_at      timestamptz,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  unique (user_id, service)
);

-- ============================================================
-- ACCOUNTS (companies being tracked)
-- ============================================================
create table if not exists accounts (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  company_name      text not null,
  domain            text,
  industry          text,
  employee_count    integer,
  revenue           numeric,
  location          text,
  website           text,
  score             numeric,
  tier              integer,
  score_rationale   text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  unique (user_id, company_name)
);
create index if not exists idx_accounts_user on accounts(user_id);
create index if not exists idx_accounts_score on accounts(user_id, score desc);

-- ============================================================
-- SIGNALS (buying-intent signals from all sources)
-- ============================================================
create table if not exists signals (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  account_id        uuid not null references accounts(id) on delete cascade,
  source            text not null,
  signal_type       text not null,
  title             text not null,
  description       text,
  url               text,
  raw_data          jsonb,
  detected_at       timestamptz not null default now(),
  created_at        timestamptz not null default now()
);
create index if not exists idx_signals_user_account on signals(user_id, account_id);
create index if not exists idx_signals_detected on signals(account_id, detected_at desc);

-- ============================================================
-- SIGNAL SCORES (Bedrock Claude scoring log)
-- ============================================================
create table if not exists signal_scores (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  account_id        uuid not null references accounts(id) on delete cascade,
  signal_id         uuid references signals(id) on delete set null,
  score             numeric not null,
  tier              integer not null,
  model_used        text,
  rationale         text,
  scored_at         timestamptz not null default now()
);
create index if not exists idx_signal_scores_account on signal_scores(account_id);

-- ============================================================
-- CAMPAIGNS
-- ============================================================
create table if not exists campaigns (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  name              text not null,
  description       text,
  status            text not null default 'draft',
  tier_filters      jsonb,
  channels          jsonb,
  cadence           jsonb,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create index if not exists idx_campaigns_user on campaigns(user_id);

-- ============================================================
-- CAMPAIGN ACCOUNTS (targets routed by tier)
-- ============================================================
create table if not exists campaign_accounts (
  id                uuid primary key default gen_random_uuid(),
  campaign_id       uuid not null references campaigns(id) on delete cascade,
  account_id        uuid not null references accounts(id) on delete cascade,
  status            text not null default 'pending',
  tier              integer,
  score             numeric,
  error             text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  unique (campaign_id, account_id)
);
create index if not exists idx_ca_campaign on campaign_accounts(campaign_id);

-- ============================================================
-- EMAIL TEMPLATES (sequence step templates)
-- ============================================================
create table if not exists email_templates (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  name              text not null,
  subject           text not null,
  body              text not null,
  sequence_step     integer not null default 1,
  is_default        boolean not null default false,
  created_at        timestamptz not null default now()
);

-- ============================================================
-- EMAIL MESSAGES
-- ============================================================
create table if not exists email_messages (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references users(id) on delete cascade,
  campaign_id         uuid references campaigns(id) on delete set null,
  campaign_account_id uuid references campaign_accounts(id) on delete set null,
  account_id          uuid references accounts(id) on delete set null,
  subject             text not null,
  body_text           text not null,
  body_html           text,
  status              text not null default 'draft',
  from_email          text,
  to_email            text not null,
  provider            text,
  message_id          text,
  sequence_step       integer not null default 1,
  sent_at             timestamptz,
  opened_at           timestamptz,
  clicked_at          timestamptz,
  replied_at          timestamptz,
  created_at          timestamptz not null default now()
);
create index if not exists idx_em_campaign on email_messages(campaign_id);
create index if not exists idx_em_account on email_messages(account_id);
create index if not exists idx_em_status on email_messages(status);

-- ============================================================
-- EMAIL EVENTS (opens, clicks, bounces, replies...)
-- ============================================================
create table if not exists email_events (
  id                uuid primary key default gen_random_uuid(),
  email_message_id  uuid not null references email_messages(id) on delete cascade,
  event_type        text not null,
  occurred_at       timestamptz not null default now(),
  metadata          jsonb
);
create index if not exists idx_ee_message on email_events(email_message_id);
create index if not exists idx_ee_type on email_events(event_type);

-- ============================================================
-- CRM SYNCS (HubSpot / Salesforce lead & deal creation)
-- ============================================================
create table if not exists crm_syncs (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references users(id) on delete cascade,
  campaign_id       uuid references campaigns(id) on delete set null,
  account_id        uuid references accounts(id) on delete set null,
  service           text not null,
  status            text not null default 'pending',
  object_type       text,
  external_id       text,
  error_message     text,
  synced_at         timestamptz,
  created_at        timestamptz not null default now()
);
create index if not exists idx_crm_user on crm_syncs(user_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- Note: the backend connects with the database superuser and bypasses
-- RLS. These policies protect against any direct client-side access.
-- ============================================================
alter table users enable row level security;
alter table service_credentials enable row level security;
alter table accounts enable row level security;
alter table signals enable row level security;
alter table signal_scores enable row level security;
alter table campaigns enable row level security;
alter table campaign_accounts enable row level security;
alter table email_templates enable row level security;
alter table email_messages enable row level security;
alter table email_events enable row level security;
alter table crm_syncs enable row level security;

create policy "Users can access own data"
  on users for all
  using (auth.uid()::text = supabase_auth_id or auth.uid() = id);

create policy "Users can access own service credentials"
  on service_credentials for all
  using (auth.uid() = user_id);

create policy "Users can access own accounts"
  on accounts for all
  using (auth.uid() = user_id);

create policy "Users can access own signals"
  on signals for all
  using (auth.uid() = user_id);

create policy "Users can access own signal scores"
  on signal_scores for all
  using (auth.uid() = user_id);

create policy "Users can access own campaigns"
  on campaigns for all
  using (auth.uid() = user_id);

create policy "Users can access own campaign accounts"
  on campaign_accounts for all
  using (auth.uid() in (select user_id from campaigns where id = campaign_id));

create policy "Users can access own email templates"
  on email_templates for all
  using (auth.uid() = user_id);

create policy "Users can access own email messages"
  on email_messages for all
  using (auth.uid() = user_id);

create policy "Users can access own email events"
  on email_events for all
  using (auth.uid() in (select user_id from email_messages where id = email_message_id));

create policy "Users can access own crm syncs"
  on crm_syncs for all
  using (auth.uid() = user_id);

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_users_updated before update on users
  for each row execute function set_updated_at();
create trigger trg_credentials_updated before update on service_credentials
  for each row execute function set_updated_at();
create trigger trg_accounts_updated before update on accounts
  for each row execute function set_updated_at();
create trigger trg_campaigns_updated before update on campaigns
  for each row execute function set_updated_at();
create trigger trg_ca_updated before update on campaign_accounts
  for each row execute function set_updated_at();