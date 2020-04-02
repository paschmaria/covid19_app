import html2text
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from accounts.models import USSDUser
from core.celery import app


# instantiate html2text
h = html2text.HTML2Text()
h.ignore_links = True

@app.task
def send_mail_to_admin(user_id):
    user = USSDUser.objects.get(id=user_id)
    subject = "Positive Case Detected!"
    context = {'user': user}
    html_message = render_to_string('emails/send_admin_mail.html', context)
    message = h.handle(html_message)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL], fail_silently=False, html_message=html_message)