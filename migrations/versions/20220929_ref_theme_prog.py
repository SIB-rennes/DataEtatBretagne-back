"""empty message

Revision ID: 20220929_ref_theme_label_prog
Revises: 0af544930fc5
Create Date: 2022-09-29 12:04:32.664941

"""
import logging
import pandas
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy import Column,String,Text

# revision identifiers, used by Alembic.
revision = '20220929_ref_theme_prog'
down_revision = '20220919_init_budget'
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class _Base(orm.DeclarativeBase):
    pass

class _CodeProgramme(_Base):
    __tablename__ = 'ref_code_programme'
    id = sa.Column(sa.Integer, primary_key=True)
    code: str = Column(String, unique=True, nullable=False)
    # FK
    theme = Column(sa.Integer, sa.ForeignKey('ref_theme.id'), nullable=True)

    label: str = Column(String)
    description: str = Column(Text)


class _Theme(_Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ref_theme'
    id = sa.Column(sa.Integer, primary_key=True)
    label: str = Column(String)
    description: str = Column(Text)



def upgrade():
    session = orm.Session(bind=op.get_bind())
    code_programme_file = f'migrations/data/{revision}/code_programme_theme.csv'
    df_programme = pandas.read_csv(code_programme_file, sep=",", usecols=['code_programme', 'titre_programme','theme'],
                                  dtype={'code_programme': str, 'titre_programme': str, 'theme': str})
    try:
        for index, programme in df_programme.iterrows():
            instance_programme = session.query(_CodeProgramme).filter_by(**{'code':programme['code_programme'] }).one_or_none()
            if str(programme['theme']) != 'nan' :
                instance_theme = session.query(_Theme).filter_by(**{'label':programme['theme'] }).one_or_none()
                if instance_theme is None :
                    instance_theme = _Theme(label=programme['theme'])
                    session.add(instance_theme)
                    session.flush()
            else :
                instance_theme = None

            if instance_programme is None:
                programme = _CodeProgramme(code = programme['code_programme'], label = programme['titre_programme'],
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
    op.execute("DELETE FROM ref_code_programme")
    op.execute("DELETE FROM ref_theme")
