"""empty message

Revision ID: 13945f856f25
Revises: 20230517_loc_interminis
Create Date: 2023-05-19 17:44:05.969502

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20230519_montant_ae'
down_revision = '20230517_loc_interminis'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('montant_financial_ae',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_financial_ae', sa.Integer(), nullable=False),
    sa.Column('montant', sa.Float(), nullable=True),
    sa.Column('annee', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_financial_ae'], ['financial_ae.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    sql_insert_montant = 'INSERT INTO montant_financial_ae (id_financial_ae, montant, annee, created_at, updated_at) ' \
                         '(SELECT id, montant, annee, created_at, updated_at FROM financial_ae)'

    op.execute(sql_insert_montant)

    # UPDATE VIEW
    op.execute('DROP VIEW public.montant_par_niveau_bop_annee_type')
    op.execute('DROP VIEW public.montant_par_commune_type')
    op.execute('DROP VIEW public.montant_par_commune_type_theme')
    op.execute('DROP VIEW public.montant_par_commune')


    sql_tmp_sum_montant = "SELECT sum(mae.montant) AS montant, fae.id, fae.siret, fae.programme FROM montant_financial_ae mae JOIN financial_ae fae ON (fae.id = mae.id_financial_ae) GROUP BY fae.id, fae.siret, fae.programme"

    view_montant = "CREATE OR REPLACE VIEW public.montant_par_commune AS " \
                   "SELECT SUM(dc.montant) as montant, rs.code_commune FROM ("+sql_tmp_sum_montant+") AS dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) GROUP BY rs.code_commune"

    view_theme = "CREATE OR REPLACE VIEW public.montant_par_commune_type_theme AS " \
                  "SELECT SUM(dc.montant) AS montant, rs.code_commune, rcj.type AS type, rt.label as theme FROM ("+sql_tmp_sum_montant+") as dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) LEFT JOIN ref_code_programme AS rcp ON (rcp.code = dc.programme) LEFT JOIN ref_theme AS rt ON (rt.id = rcp.theme) LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) GROUP BY (rs.code_commune,rcj.type, rt.label)"

    view_type = "CREATE OR REPLACE VIEW public.montant_par_commune_type AS " \
                 "SELECT SUM(dc.montant) AS montant, rs.code_commune, rcj.type as type FROM ("+sql_tmp_sum_montant+") as dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) GROUP BY (rs.code_commune,rcj.type)"

    sql_tmp_sum_montant_group_annee = "SELECT sum(mae.montant) AS montant, fae.id, fae.siret, fae.programme, fae.annee FROM montant_financial_ae mae JOIN financial_ae fae ON (fae.id = mae.id_financial_ae) GROUP BY fae.id, fae.annee, fae.siret, fae.programme"


    view_programme_annee_type = "CREATE OR REPLACE VIEW  public.montant_par_niveau_bop_annee_type AS (" \
                                "SELECT SUM(dc.montant) AS montant, 'commune' as niveau, rs.code_commune as code, dc.programme, dc.annee, rcj.type as TYPE 	FROM ("+sql_tmp_sum_montant_group_annee+") as dc " \
                                "LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) GROUP BY (rs.code_commune, dc.programme, dc.annee, rcj.type) " \
                                "UNION (" \
                                "SELECT SUM(dc.montant) AS montant, 'epci' as niveau, rc.code_epci as code, dc.programme, dc.annee, rcj.type as TYPE FROM ("+sql_tmp_sum_montant_group_annee+") as dc " \
                                "LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) " \
	                            "LEFT JOIN ref_commune AS  rc ON (rc.code = rs.code_commune) " \
	                            "LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) " \
		                        "GROUP BY (rc.code_epci, dc.programme,dc.annee, rcj.type)) " \
                                "UNION (" \
                                "SELECT SUM(dc.montant) AS montant, 'departement' as niveau, rc.code_departement as code, dc.programme, dc.annee, rcj.type as type FROM ("+sql_tmp_sum_montant_group_annee+") as dc " \
                                "LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) " \
		                        "LEFT JOIN ref_commune AS  rc ON (rc.code = rs.code_commune) " \
		                        "LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) "\
			                    "GROUP BY (rc.code_departement, dc.programme, dc.annee, rcj.type)))"

    op.execute(view_montant)
    op.execute(view_theme)
    op.execute(view_type)
    op.execute(view_programme_annee_type)
    with op.batch_alter_table('financial_ae', schema=None) as batch_op:
        batch_op.drop_column('montant')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('financial_ae', schema=None) as batch_op:
        batch_op.add_column(sa.Column('montant', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))

    op.drop_table('montant_financial_ae')
    # ### end Alembic commands ###
