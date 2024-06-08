"""create item table

Revision ID: f5a8ba179a4e
Revises:
Create Date: 2023-06-26 17:00:02.605604

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f5a8ba179a4e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION "uuid-ossp";
        CREATE TABLE item (
            id SERIAL PRIMARY KEY,
            uuid UUID DEFAULT uuid_generate_v4(),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name VARCHAR(50),
            price NUMERIC(10, 2)
        );
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS item;
        DROP EXTENSION IF EXISTS "uuid-ossp";
    """
    )
