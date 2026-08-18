-- 002: add contact_email to campaign_accounts (email-list import feature)

ALTER TABLE campaign_accounts ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255);
