"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-28 18:15:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("place_of_living", sa.String(length=120), nullable=False),
        sa.Column("gender", sa.String(length=40), nullable=False),
        sa.Column("country_of_origin", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("photo_path", sa.String(length=500), nullable=False),
        sa.Column("classification_result", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_submissions_user_id", "submissions", ["user_id"], unique=False)
    op.create_index("ix_submissions_age", "submissions", ["age"], unique=False)
    op.create_index("ix_submissions_gender", "submissions", ["gender"], unique=False)
    op.create_index("ix_submissions_place", "submissions", ["place_of_living"], unique=False)
    op.create_index("ix_submissions_country", "submissions", ["country_of_origin"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_submissions_country", table_name="submissions")
    op.drop_index("ix_submissions_place", table_name="submissions")
    op.drop_index("ix_submissions_gender", table_name="submissions")
    op.drop_index("ix_submissions_age", table_name="submissions")
    op.drop_index("ix_submissions_user_id", table_name="submissions")
    op.drop_table("submissions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
