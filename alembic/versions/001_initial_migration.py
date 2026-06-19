"""Replace dir with s3_key in documents table.

Revision ID: 001_initial_migration
Revises: 
Create Date: 2026-06-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=150), nullable=False),
    )

    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.Date(), nullable=False),
    )

    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("s3_key", sa.String(length=255), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("project.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    op.create_table(
        "user_project",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id"), primary_key=True),
        sa.Column("role", sa.String(length=10), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_project")
    op.drop_table("document")
    op.drop_table("project")
    op.drop_table("user")
