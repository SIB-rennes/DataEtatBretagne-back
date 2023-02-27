from app.mailapp.Mail import Mail

mail = None

def create_mail_app(_app=None):
    if 'SMTP' in _app.config :
        mail_config = _app.config['SMTP']
        return Mail(**mail_config)
    else :
        return Mail()
