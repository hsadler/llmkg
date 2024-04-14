"""item name unique

Revision ID: f980d790e870
Revises: f5a8ba179a4e
Create Date: 2023-06-26 19:58:21.748965

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f980d790e870"
down_revision = "f5a8ba179a4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE item ADD CONSTRAINT item_name_unique UNIQUE (name);
    """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE item DROP CONSTRAINT item_name_unique;
    """
    )
