"""Add users and user-scoped data

Revision ID: 002_users
Revises: 001_initial
Create Date: 2026-06-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_users"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.add_column("reviews", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_reviews_user_id"), "reviews", ["user_id"], unique=False)
    op.create_foreign_key("fk_reviews_user_id", "reviews", "users", ["user_id"], ["id"])

    op.add_column("processing_jobs", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_processing_jobs_user_id"), "processing_jobs", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_processing_jobs_user_id",
        "processing_jobs",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_processing_jobs_user_id", "processing_jobs", type_="foreignkey")
    op.drop_index(op.f("ix_processing_jobs_user_id"), table_name="processing_jobs")
    op.drop_column("processing_jobs", "user_id")

    op.drop_constraint("fk_reviews_user_id", "reviews", type_="foreignkey")
    op.drop_index(op.f("ix_reviews_user_id"), table_name="reviews")
    op.drop_column("reviews", "user_id")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
