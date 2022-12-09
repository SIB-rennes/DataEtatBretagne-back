"""empty message

Revision ID: 19d9cc2d92b1
Revises: 20221104_view_montant
Create Date: 2022-12-09 11:11:53.890226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20221209_view_montant'
down_revision = '20221104_view_montant'
branch_labels = None
depends_on = None


def upgrade():
    view_programme_annee_type = "CREATE VIEW public.montant_par_niveau_bop_annee_type AS (	SELECT SUM(dc.montant) AS montant, 'commune' as niveau, rs.code_commune as code, dc.programme, date_part('year', dc.date_modification_ej) as annee, rcj.type as type 	FROM data_chorus as dc 	LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) 	LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) 		WHERE dc.montant >= 0 		GROUP BY (rs.code_commune, dc.programme, date_part('year', dc.date_modification_ej), rcj.type)		) UNION (						SELECT SUM(dc.montant) AS montant, 'epci' as niveau, rc.code_epci as code, dc.programme, date_part('year', dc.date_modification_ej) as annee, rcj.type as type 	FROM data_chorus as dc 	LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) 	LEFT JOIN ref_commune AS  rc ON (rc.code_commune = rs.code_commune) 	LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) 		WHERE dc.montant >= 0 		GROUP BY (rc.code_epci, dc.programme, date_part('year', dc.date_modification_ej), rcj.type)	)	UNION(				SELECT SUM(dc.montant) AS montant, 'departement' as niveau, rc.code_departement as code, dc.programme, date_part('year', dc.date_modification_ej) as annee, rcj.type as type 	FROM data_chorus as dc 	LEFT JOIN ref_siret AS  rs ON (rs.code = dc.siret) 	LEFT JOIN ref_commune AS  rc ON (rc.code_commune = rs.code_commune) 	LEFT JOIN ref_categorie_juridique AS rcj ON (rcj.code = rs.categorie_juridique) 		WHERE dc.montant >= 0 		GROUP BY (rc.code_departement, dc.programme, date_part('year', dc.date_modification_ej), rcj.type)	)"
    op.execute(view_programme_annee_type)


def downgrade():
    op.execute('DROP VIEW public.view_programme_annee_type')
