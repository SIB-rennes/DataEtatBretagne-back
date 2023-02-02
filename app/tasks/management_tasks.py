import logging

from sqlalchemy.orm import lazyload

from app import db, celeryapp, mailapp
from app.models.preference.Preference import Preference

LOGGER = logging.getLogger()

celery = celeryapp.celery
mail = mailapp.mail

text_template = "Bonjour" \
                "{0} cherche à vous partager une vue de l'outil {1}" \
                "Pour y accéder, veuillez suivre le lien {2} et vous connecter" \
                "" \
                "Si vous n'avez pas de compte, vous pouvez faire une demande directement sur le site." \
                ""

html_template = """
 <h1>Bonjour</h1>

<p>{0} cherche à vous partager une vue de l'outil {1}</p>
<p>Pour y accéder, veuillez cliquer sur le <a href='{2}'>lien</a> et vous connecter</p>
<p>Si vous n'avez pas de compte, vous pouvez faire une demande en suivant le lien <i>Demander un compte</i> du site.</p>
                          """


@celery.task(name='share_filter_user', bind=True)
def share_filter_user(self, subject, preference_uuid):
    '''
    Task d'envoi de mail de notification de partage de filtre
    :param self:
    :param subject : sujet du mail
    :param preference_uuid : uuid à partager
    '''
    LOGGER.info(f'[SHARE][FILTER] Start preference {preference_uuid}')

    preference = db.session.query(Preference).options(lazyload(Preference.shares)).filter_by(uuid=preference_uuid).one_or_none()

    if (preference is not None and len(preference.shares) > 0):
        for share in preference.shares:
            if share.email_send == False:
                mail.send_email(subject, share.shared_username_email, text_template.format(share.shared_username_email.split("@")[0]),
                                html_template.format(share.shared_username_email.split("@")[0]))
                share.email_send = True
                db.session.commit()
                LOGGER.debug(f'[SHARE][FILTER] Send mail to {share.shared_username_email}')







