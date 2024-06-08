"""subjects-and-related-subjects

Revision ID: 7f65c979d7b2
Revises: f980d790e870
Create Date: 2024-04-16 22:57:40.122167

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7f65c979d7b2"
down_revision = "f980d790e870"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE subject (
            id SERIAL PRIMARY KEY,
            uuid UUID DEFAULT uuid_generate_v4(),
            name VARCHAR(50) UNIQUE NOT NULL
        );
        CREATE TABLE subject_relation (
            subject_name VARCHAR(50) NOT NULL,
            related_subject_name VARCHAR(50) NOT NULL,
            CONSTRAINT relation_unique UNIQUE (subject_name, related_subject_name)
        );
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS subject;
        DROP TABLE IF EXISTS subject_relation;
    """
    )
