import logging

from sqlalchemy.orm import lazyload

from app import db, celeryapp, mailapp
from app.models.preference.Preference import Preference

LOGGER = logging.getLogger()

celery = celeryapp.celery
mail = mailapp.mail

text_template = "Bonjour," \
                "{0} cherche à vous partager une vue de l'outil {1}." \
                "Pour y accéder, veuillez suivre le lien {2} et vous connecter." \
                "" \
                "Si vous n'avez pas de compte, vous pouvez faire une demande en suivant le lien {3}." \
                ""

html_template = """
 <h3>Bonjour,</h3>

<p>{0} cherche à vous partager une vue de l'outil {1}.</p>
<p>Pour y accéder, veuillez cliquer sur le lien {2} et vous connecter.</p>
<p>Si vous n'avez pas de compte, vous pouvez faire une demande en suivant le lien {3}.</p>"""

subject = "Budget Data État Bretagne"

@celery.task(name='share_filter_user', bind=True)
def share_filter_user(self, preference_uuid, host_link):
    '''
    Task d'envoi de mail de notification de partage de filtre
    :param self:
    :param preference_uuid : uuid à partager
    :param host_link: host pour le partage du lien
    '''
    LOGGER.info(f'[SHARE][FILTER] Start preference {preference_uuid}')

    preference = db.session.query(Preference).options(lazyload(Preference.shares)).filter_by(uuid=preference_uuid).one_or_none()

    link_preference = f'{host_link}/?uuid={preference_uuid}'
    link_register = f'{host_link}/register'

    if (preference is not None and len(preference.shares) > 0):
        for share in preference.shares:
            if share.email_send == False:
                mail.send_email(subject, share.shared_username_email,
                                text_template.format(preference.username,subject,link_preference,link_register),
                                html_template.format(preference.username,subject, link_preference,link_register))
                share.email_send = True
                db.session.commit()
                LOGGER.debug(f'[SHARE][FILTER] Send mail to {share.shared_username_email}')







