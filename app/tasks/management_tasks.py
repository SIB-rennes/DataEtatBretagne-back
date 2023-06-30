import datetime
import logging

import sqlalchemy
from sqlalchemy import cast
from sqlalchemy.orm import lazyload

from app import db, celeryapp, mailapp
from app.models.preference.Preference import Preference

LOGGER = logging.getLogger()

celery = celeryapp.celery
mail = mailapp.mail

text_template = "Bonjour," \
                "{0} souhaite vous partager un tableau de bord via le service {1}." \
                "{1} est un projet interministériel piloté par le SGAR Bretagne (Préfecture de région)." \
                "Il vise au partage et à la réutilisation des données de l’État dont financières pour piloter les politiques publiques et valoriser les financements de l’État sur les territoires." \
                "" \
                "Pour y accéder, veuillez cliquer sur le lien {2} et vous connecter." \
                "Si vous n'avez pas de compte, vous pouvez faire une demande en suivant le lien {3}." \
                ""

html_template = """
 <h3>Bonjour,</h3>

<p>{0} souhaite vous partager un tableau de bord via le service {1}.</p>
<p>{1} est un projet interministériel piloté par le SGAR Bretagne (Préfecture de région). 
Il vise au partage et à la réutilisation des données de l’État dont financières pour piloter les politiques publiques et valoriser les financements de l’État sur les territoires.</p>
<p>Pour y accéder, veuillez cliquer sur ce <a href="{2}">lien</a> et vous connecter.</p>
<p>Si vous n'avez pas de compte, vous pouvez faire une demande en suivant ce <a href="{3}">lien</a></p>
"""

subject_budget = "Budget Data État Bretagne"
subject_france_relance = "France Relance Bretagne"


@celery.task(name='share_filter_user', bind=True)
def share_filter_user(self, preference_uuid, host_link):
    '''
    Task d'envoi de mail de notification de partage de filtre
    :param self:
    :param preference_uuid : uuid à partager
    :param host_link: host pour le partage du lien
    '''
    LOGGER.info(f'[SHARE][FILTER] Start preference {preference_uuid}')

    preference = db.session.query(Preference).options(lazyload(Preference.shares)).filter(cast(Preference.uuid, sqlalchemy.String) == preference_uuid).one_or_none()

    link_preference = f'{host_link}/?uuid={preference_uuid}'
    link_register = f'{host_link}/register'
    subject = get_subject(host_link)

    if (preference is not None and len(preference.shares) > 0):
        for share in preference.shares:
            if share.email_send == False:
                txt = text_template.format(preference.username,subject, link_preference, link_register)
                htm = html_template.format(preference.username,subject, link_preference, link_register)

                mail.send_email(subject, share.shared_username_email, txt, htm)

                share.email_send = True
                share.date_email_send = datetime.datetime.utcnow()
                db.session.commit()
                LOGGER.debug(f'[SHARE][FILTER] Send mail to {share.shared_username_email}')



def get_subject(link):
    if 'relance' in link:
        return subject_france_relance
    return subject_budget






