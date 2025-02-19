"""initial

Revision ID: 3a74ffff8d72
Revises:
Create Date: 2024-08-18 11:40:55.909202

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3a74ffff8d72"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "parcel_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_parcel_type_id"), "parcel_type", ["id"], unique=False)
    op.create_table(
        "parcel",
        sa.Column("id", sa.BIGINT(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("value_in_dollars", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("owner", sa.String(length=50), nullable=False),
        sa.Column("time_created", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["parcel_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parcel_id"), "parcel", ["id"], unique=False)
    op.create_index(op.f("ix_parcel_owner"), "parcel", ["owner"], unique=False)

    op.execute(
        "INSERT INTO parcel_type(id, name) VALUES (1, 'одежда'), (2, 'электроника'), (3, 'разное')"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM parcel_type WHERE id IN (1, 2, 3)")
    op.drop_index(op.f("ix_parcel_owner"), table_name="parcel")
    op.drop_index(op.f("ix_parcel_id"), table_name="parcel")
    op.drop_table("parcel")
    op.drop_index(op.f("ix_parcel_type_id"), table_name="parcel_type")
    op.drop_table("parcel_type")
    # ### end Alembic commands ###
