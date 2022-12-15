"""empty message

Revision ID: ebff69f2663f
Revises: 2deb826b5cdb
Create Date: 2022-11-04 12:18:26.344119

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20221104_view_montant'
down_revision = '20221004_ref_cat_juridique'
branch_labels = None
depends_on = None


def upgrade():
    view_montant = "CREATE VIEW public.montant_par_commune AS " \
                   " SELECT SUM(dc.montant) as montant, rs.code_commune FROM data_chorus as dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) WHERE dc.montant >=0 GROUP BY rs.code_commune"

    view_theme = "CREATE VIEW public.montant_par_commune_type_theme AS " \
                 "SELECT SUM(dc.montant) AS montant, rs.code_commune, rcj.type AS type, rt.label as theme FROM data_chorus as dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) LEFT JOIN ref_code_programme AS rcp ON (rcp.code = dc.programme) LEFT JOIN ref_theme AS rt ON (rt.id = rcp.theme) LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) WHERE dc.montant >=0 GROUP BY (rs.code_commune,rcj.type, rt.label)"

    view_type = "CREATE VIEW public.montant_par_commune_type AS " \
                "SELECT SUM(dc.montant) AS montant, rs.code_commune, rcj.type as type FROM data_chorus as dc LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) WHERE dc.montant >=0 GROUP BY (rs.code_commune,rcj.type)"

    op.execute(view_montant)
    op.execute(view_theme)
    op.execute(view_type)


def downgrade():
    op.execute('DROP VIEW public.montant_par_commune_type')
    op.execute('DROP VIEW public.montant_par_commune_theme')
    op.execute('DROP VIEW public.montant_par_commune')
