"""reconcile schema with models

Brings the 0001 initial schema in line with the current SQLAlchemy models:
adds campaign A/B + run-log columns, campaign_account.contact_email,
email message variant column + indexes, and the email_replies table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaign_accounts", sa.Column("contact_email", sa.String(255), nullable=True))

    op.add_column(
        "campaigns",
        sa.Column("ab_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("campaigns", sa.Column("ab_won", sa.String(8), nullable=True))
    op.add_column("campaigns", sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("campaigns", sa.Column("run_log", sa.Text(), nullable=True))

    op.add_column("email_messages", sa.Column("variant", sa.String(8), nullable=False, server_default="A"))
    op.create_index("ix_email_messages_user_id", "email_messages", ["user_id"])
    op.create_index("ix_email_messages_campaign_id", "email_messages", ["campaign_id"])
    op.create_index("ix_email_messages_account_id", "email_messages", ["account_id"])

    op.create_table(
        "email_replies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "email_message_id",
            sa.Uuid(),
            sa.ForeignKey("email_messages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("from_email", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("classification", sa.String(32), nullable=False, server_default="review"),
        sa.Column("confidence", sa.Numeric(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("suggested_reply", sa.Text(), nullable=True),
        sa.Column("auto_reply_sent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("auto_reply_message_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="classified"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_email_replies_user_id", "email_replies", ["user_id"])
    op.create_index("ix_email_replies_email_message_id", "email_replies", ["email_message_id"])


def downgrade() -> None:
    op.drop_index("ix_email_replies_email_message_id", table_name="email_replies")
    op.drop_index("ix_email_replies_user_id", table_name="email_replies")
    op.drop_table("email_replies")

    op.drop_index("ix_email_messages_account_id", table_name="email_messages")
    op.drop_index("ix_email_messages_campaign_id", table_name="email_messages")
    op.drop_index("ix_email_messages_user_id", table_name="email_messages")
    op.drop_column("email_messages", "variant")

    op.drop_column("campaigns", "run_log")
    op.drop_column("campaigns", "last_run_at")
    op.drop_column("campaigns", "ab_won")
    op.drop_column("campaigns", "ab_enabled")

    op.drop_column("campaign_accounts", "contact_email")