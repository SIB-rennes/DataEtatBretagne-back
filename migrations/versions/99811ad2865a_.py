"""empty message

Revision ID: 99811ad2865a
Revises: 3c55e2610f54
Create Date: 2022-09-29 17:04:07.706585

"""
import logging

import pandas
from alembic import op
import sqlalchemy as sa
import wget
from flask import session
from sqlalchemy import orm

from app.models.refs.commune_crte import CommuneCrte

# revision identifiers, used by Alembic.
revision = '99811ad2865a'
down_revision = '3c55e2610f54'
branch_labels = None
depends_on = None

url_csv = "https://www.data.gouv.fr/fr/datasets/r/57ad19ea-9a54-45fa-802c-cf3ae71ea570"

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ref_commune_crte',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code_commune', sa.String(), nullable=False),
    sa.Column('code_crte', sa.String(), nullable=False),
    sa.Column('label_crte', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code_commune')
    )

    _insert_ref()

    op.alter_column('ref_siret', 'code_commune',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_foreign_key(None, 'ref_siret', 'ref_commune_crte', ['code_commune'], ['code_commune'])
    # ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('ref_siret_code_commune_fkey', 'ref_siret', type_='foreignkey')
    op.alter_column('ref_siret', 'code_commune',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_table('ref_commune_crte')
    # ### end Alembic commands ###


def _insert_ref():
    file = 'migrations/data/ref_crte.csv'
    wget.download(url_csv, out=file)

    session = orm.Session(bind=op.get_bind())
    data_frame = pandas.read_csv(file, usecols=["insee_com","lib_com","id_crte","lib_crte"], sep=",")
    try:
        for index, programme in data_frame.iterrows():
            commune = session.query(CommuneCrte).filter_by(**{'code_commune':programme['insee_com'] }).one_or_none()
            if commune is None:
                commune = CommuneCrte(code_commune=programme['insee_com'], code_crte=programme["id_crte"],
                                      label_crte=programme["lib_crte"])
                session.add(commune)
                session.commit()
            elif  _commune_in_dpt_crte(str(programme['insee_com']), programme["id_crte"]) :
                commune.code_crte = programme["id_crte"]
                commune.label_crte = programme["lib_crte"]
                session.commit()
            else:
                logging.getLogger('flask_migrate')\
                    .info('Ignore ligne %s commune %s in %s', index, programme['insee_com'], programme["id_crte"])
    except Exception as e:
        session.rollback()
        print(e)



def _commune_in_dpt_crte(code_insee, code_crte):
    '''
    Check si la commune est dans le département de la CRTE
    :param code_insee: code commune
    :param code_crte: code crte
    :return: true or flase
    '''
    return code_insee[0:2] == code_crte[8:10]


