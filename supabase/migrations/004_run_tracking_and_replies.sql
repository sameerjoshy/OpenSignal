-- 004: campaign run tracking + inbound reply classification

ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS last_run_at TIMESTAMPTZ;
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS run_log TEXT;

CREATE TABLE IF NOT EXISTS email_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_message_id UUID REFERENCES email_messages(id) ON DELETE SET NULL,
    from_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    body TEXT NOT NULL,
    classification VARCHAR(32) NOT NULL DEFAULT 'review',
    confidence NUMERIC,
    summary TEXT,
    suggested_reply TEXT,
    auto_reply_sent BOOLEAN NOT NULL DEFAULT FALSE,
    auto_reply_message_id UUID,
    status VARCHAR(32) NOT NULL DEFAULT 'classified',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_email_replies_user_id ON email_replies(user_id);
CREATE INDEX IF NOT EXISTS ix_email_replies_email_message_id ON email_replies(email_message_id);
