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
    # Check if the 'dir' column exists before trying to drop it
    # This is necessary for new databases that might already have s3_key
    op.add_column('document', sa.Column('s3_key', sa.String(255), nullable=True))
    
    # If the data migration is needed (copying from dir to s3_key),
    # you can do it here with a SQL statement
    # For now, we'll just set s3_key to a default value based on existing data
    op.execute("""
        UPDATE document 
        SET s3_key = CONCAT(CAST(id AS VARCHAR), '/', file_name)
        WHERE s3_key IS NULL
    """)
    
    # Make s3_key non-nullable
    op.alter_column('document', 's3_key', nullable=False)
    
    # Drop the dir column if it exists
    try:
        op.drop_column('document', 'dir')
    except:
        pass


def downgrade() -> None:
    # Re-add the dir column
    op.add_column('document', sa.Column('dir', sa.String(255), nullable=False))
    
    # Populate dir from s3_key for rollback
    op.execute("""
        UPDATE document 
        SET dir = SUBSTRING(s3_key, 1, POSITION('/' IN s3_key) - 1)
        WHERE dir IS NULL
    """)
    
    # Drop s3_key column
    op.drop_column('document', 's3_key')
