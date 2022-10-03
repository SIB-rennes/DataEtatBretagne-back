"""empty message

Revision ID: 3c55e2610f54
Revises: 0af544930fc5
Create Date: 2022-09-29 12:04:32.664941

"""
import pandas
from alembic import op
from sqlalchemy import orm

from app.models.refs.code_programme import CodeProgramme
from app.models.refs.theme import Theme

# revision identifiers, used by Alembic.
revision = '3c55e2610f54'
down_revision = '0af544930fc5'
branch_labels = None
depends_on = None


def upgrade():
    session = orm.Session(bind=op.get_bind())
    file = f'migrations/data/{revision}/code_programme_theme.csv'
    df_programme = pandas.read_csv(file, sep=",", usecols=['code_programme', 'titre_programme','theme'],
                                  dtype={'code_programme': str, 'titre_programme': str, 'theme': str})
    try:
        for index, programme in df_programme.iterrows():
            instance_programme = session.query(CodeProgramme).filter_by(**{'code':programme['code_programme'] }).one_or_none()
            if str(programme['theme']) != 'nan' :
                instance_theme = session.query(Theme).filter_by(**{'label':programme['theme'] }).one_or_none()
                if instance_theme is None :
                    instance_theme = Theme(label=programme['theme'])
                    session.add(instance_theme)
                    session.flush()
            else :
                instance_theme = None

            if instance_programme is None:
                programme = CodeProgramme(code = programme['code_programme'], label = programme['titre_programme'],
                                          theme = instance_theme.id if instance_theme is not None  else None)
                session.add(programme)
            else :
                instance_programme.theme = instance_theme.id if instance_theme is not None  else None
                instance_programme.label =  programme['titre_programme']

            session.commit()
    except Exception as e:
        session.rollback()
        print(e)

def downgrade():
    # op.execute("DELETE FROM ref_code_programme")
    op.execute("DELETE FROM ref_theme")
