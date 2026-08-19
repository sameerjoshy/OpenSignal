-- A/B testing: campaign toggle + per-message variant tag
alter table campaigns
  add column if not exists ab_enabled boolean not null default false,
  add column if not exists ab_won varchar(8) null;

alter table email_messages
  add column if not exists variant varchar(8) not null default 'A';
