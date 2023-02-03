from app.mailapp.Mail import Mail

mail = None

def create_mail_app(_app=None):
    mail_config = _app.config['SMTP']

    mail = Mail(**mail_config)

    return mail