"""empty message

Revision ID: 7f7b5e38a2b6
Revises: 20230406_model_ref
Create Date: 2023-03-29 16:38:08.850997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20230406_table_audit'
down_revision = '20230406_model_ref'
branch_labels = None
depends_on = None


def upgrade():

    # ### commands auto generated by Alembic - please adjust! ###

    op.execute('CREATE SCHEMA if not exists audit')

    op.create_table('audit_update_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('data_type', sa.Enum('FINANCIAL_DATA', 'FRANCE_RELANCE', 'REFERENTIEL', name='datatype'), nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='audit'
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.drop_table('audit_update_data', schema='audit')

    sql_drop_type = "DROP TYPE datatype"
    op.execute(sql_drop_type)
    # ### end Alembic commands ###
