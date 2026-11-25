"""create users

Revision ID: 0001
Revises:
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100)),
        sa.Column("education_level", sa.String(50)),
        sa.Column("target_role", sa.String(100)),
        sa.Column("experience_level", sa.String(50)),
        sa.Column("account_status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    # Supabase exposes public tables through its REST API. Enabling RLS with NO policies
    # blocks all access through that API. Our backend connects as the postgres role,
    # which bypasses RLS, so it keeps working.
    op.execute("ALTER TABLE public.users ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_table("users")