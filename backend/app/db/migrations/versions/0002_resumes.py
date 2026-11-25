"""resumes and resume details

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CHILD_TABLES = ["resume_skills", "resume_projects", "resume_experiences", "resume_education"]


def _child_table(name: str, *specific: sa.Column) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("resume_id", sa.Uuid(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *specific,
        sa.Column("source_type", sa.String(20), nullable=False, server_default="ai_extracted"),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(f"ix_{name}_resume_id", name, ["resume_id"])


def _text(name: str, length: int, required: bool = False) -> sa.Column:
    return sa.Column(
        name,
        sa.String(length),
        nullable=False,
        **({} if required else {"server_default": ""}),
    )


def upgrade() -> None:
    op.create_table(
        "resumes",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("status_message", sa.String(300)),
        sa.Column("extracted_text", sa.Text()),
        sa.Column(
            "extraction_warnings",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    _child_table(
        "resume_skills",
        _text("name", 100, True), _text("category", 50), _text("evidence", 300),
    )
    _child_table(
        "resume_projects",
        _text("name", 150, True), _text("description", 1500), _text("technologies", 300),
    )
    _child_table(
        "resume_experiences",
        _text("company", 150, True), _text("role", 150), _text("description", 1500),
    )
    _child_table(
        "resume_education",
        _text("institution", 150, True), _text("degree", 150), _text("field", 150),
    )

    # Block Supabase's public REST API from these tables (backend connects as postgres, which bypasses RLS).
    for table in ["resumes", *CHILD_TABLES]:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table in reversed(CHILD_TABLES):
        op.drop_table(table)
    op.drop_table("resumes")