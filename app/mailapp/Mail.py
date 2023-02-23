import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:
    def __init__(self, server, port, from_email, use_ssl, pwd=None):
        self.server = server
        self.port = port
        self.from_email = from_email
        self.use_ssl = use_ssl
        self.pwd = pwd

    def send_email(self, subject, recipients, template_text, template_html):
        if self.use_ssl:
            ssl_context = ssl.create_default_context()
            smtp = smtplib.SMTP_SSL(self.server, self.port, context=ssl_context)
        else:
            smtp = smtplib.SMTP(self.server, self.port)

        try :
            mail = self._prepare_message(subject, recipients, template_html, template_text)

            if (self.pwd is not None) :
                smtp.login(self.from_email, self.pwd)

            smtp.sendmail(self.from_email, recipients, mail.as_string())
            smtp.quit()
        except smtplib.SMTPException:
            logging.exception("Erreur envoi de mail")
        except Exception:
            logging.exception('Erreur')


    def _prepare_message(self, subject, recipient, template_html, template_text):
        '''
        Prepare mail MIME Multipart to send mail
        :param subject:     subject of email
        :param recipient: recipient of email
        :param template_html: html content
        :param template_text: text content
        :return:
        '''
        mail = MIMEMultipart('alternative')
        mail['Subject'] = subject
        mail['From'] = self.from_email
        mail['To'] = recipient

        html_content = MIMEText(template_html, 'html')
        text_content = MIMEText(template_text, 'plain')

        mail.attach(text_content)
        mail.attach(html_content)
        return mail
