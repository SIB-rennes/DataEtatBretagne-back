"""empty message

Revision ID: 7f7b5e38a2b6
Revises: 20230406_model_ref
Create Date: 2023-03-29 16:38:08.850997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20230417_financial_cp'
down_revision = '20230406_model_ref'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('ALTER TABLE IF EXISTS data_chorus RENAME TO financial_ae')

    # suppression clé primaire n_ej n_poste_ej
    op.execute('ALTER TABLE financial_ae DROP CONSTRAINT data_chorus_pkey')
    op.execute('ALTER TABLE financial_ae ADD COLUMN ID SERIAL PRIMARY KEY')

    op.execute('ALTER TABLE financial_ae ADD CONSTRAINT  unique_ej_poste_ej UNIQUE (n_ej, n_poste_ej)')

    op.create_table('financial_cp',
                    sa.Column('n_dp', sa.String(), nullable=False),
                    sa.Column('id_ae', sa.Integer(), nullable=True),
                    sa.Column('n_ej', sa.String(), nullable=True),
                    sa.Column('n_poste_ej', sa.Integer(), nullable=True),
                    sa.Column('source_region', sa.String(), nullable=False),
                    sa.Column('programme', sa.String(), nullable=False),
                    sa.Column('domaine_fonctionnel', sa.String(), nullable=False),
                    sa.Column('centre_couts', sa.String(), nullable=False),
                    sa.Column('referentiel_programmation', sa.String(), nullable=False),
                    sa.Column('siret', sa.String(), nullable=True),
                    sa.Column('groupe_marchandise', sa.String(), nullable=False),
                    sa.Column('localisation_interministerielle', sa.String(), nullable=False),
                    sa.Column('fournisseur_paye', sa.String(), nullable=False),
                    sa.Column('date_base_dp', sa.DateTime(), nullable=True),
                    sa.Column('date_derniere_operation_dp', sa.DateTime(), nullable=True),
                    sa.Column('compte_budgetaire', sa.String(length=255), nullable=True),
                    sa.Column('contrat_etat_region', sa.String(length=255), nullable=True),
                    sa.Column('montant', sa.Float(), nullable=True),
                    sa.Column('annee', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['centre_couts'], ['ref_centre_couts.code'], ),
                    sa.ForeignKeyConstraint(['domaine_fonctionnel'], ['ref_domaine_fonctionnel.code'], ),
                    sa.ForeignKeyConstraint(['fournisseur_paye'], ['ref_fournisseur_titulaire.code'], ),
                    sa.ForeignKeyConstraint(['groupe_marchandise'], ['ref_groupe_marchandise.code'], ),
                    sa.ForeignKeyConstraint(['localisation_interministerielle'],
                                            ['ref_localisation_interministerielle.code'], ),
                    sa.ForeignKeyConstraint(['id_ae'], ['financial_ae.id'], ),
                    sa.ForeignKeyConstraint(['programme'], ['ref_code_programme.code'], ),
                    sa.ForeignKeyConstraint(['referentiel_programmation'], ['ref_programmation.code'], ),
                    sa.ForeignKeyConstraint(['siret'], ['ref_siret.code'], ),
                    sa.ForeignKeyConstraint(['source_region'], ['ref_region.code'], ),
                    sa.PrimaryKeyConstraint('n_dp')
                    )

    # siret peut être null
    op.execute("ALTER TABLE financial_ae ALTER COLUMN siret DROP NOT NULL")

    op.execute("ALTER TYPE datatype ADD VALUE 'FINANCIAL_DATA_AE'")
    op.execute("ALTER TYPE datatype ADD VALUE 'FINANCIAL_DATA_CP'")
    op.execute("COMMIT")


    # supression value FINANCIAL_DATA
    op.execute("ALTER TYPE datatype RENAME TO datatype_old")
    op.execute("CREATE TYPE datatype AS ENUM('FINANCIAL_DATA_AE', 'FINANCIAL_DATA_CP', 'FRANCE_RELANCE','REFERENTIEL')")

    op.execute("UPDATE audit.audit_update_data SET data_type = 'FINANCIAL_DATA_AE' WHERE data_type = 'FINANCIAL_DATA' ")
    op.execute("ALTER TABLE audit.audit_update_data ALTER COLUMN data_type TYPE datatype USING data_type::text::datatype;")
    op.execute( "DROP TYPE datatype_old")

    #ARRONDISSEMENT
    op.create_table('ref_arrondissement',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('code', sa.String(), nullable=False),
                    sa.Column('code_region', sa.String(), nullable=True),
                    sa.Column('code_departement', sa.String(), nullable=True),
                    sa.Column('label', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('code')
                    )

    with op.batch_alter_table('ref_commune', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code_arrondissement', sa.String(), nullable=True))
        batch_op.create_foreign_key(None, 'ref_arrondissement', ['code_arrondissement'], ['code'])

    op.execute("ALTER TABLE public.ref_commune RENAME COLUMN code_commune TO code")



def downgrade():
    op.drop_table('financial_cp')
    op.execute("ALTER TABLE public.ref_commune RENAME COLUMN code TO code_commune")

    op.execute("ALTER TABLE public.ref_commune DROP COLUMN code_arrondissement")
    op.drop_table('ref_arrondissement')


    op.execute('ALTER TABLE financial_ae DROP CONSTRAINT financial_ae_pkey')
    op.execute('ALTER TABLE financial_ae DROP COLUMN id')
    op.execute('ALTER TABLE IF EXISTS  financial_ae RENAME TO data_chorus')
