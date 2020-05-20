import html2text
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from accounts.models import HealthStatus
from core.celery import app
from ussd_screener.constants import API_PAYLOAD
from ussd_screener.models import Session
from ussd_screener.utils import assessment_score


# instantiate html2text
h = html2text.HTML2Text()
h.ignore_links = True


@app.task
def send_mail_to_admin(status_id):
    status = HealthStatus.objects.get(id=status_id)
    subject = "Positive Case Detected!"
    context = {'status': status}
    html_message = render_to_string('emails/send_admin_mail.html', context)
    message = h.handle(html_message)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL], fail_silently=False, html_message=html_message)


@app.task
def push_to_server(session_id):
    payload = API_PAYLOAD
    session = Session.objects.get(session_id=session_id)
    responses = session.survey_responses.all()
    user = session.user
    h_status = user.health_status
    risk = h_status.risk_level

    for res in responses:
        res_dict = {}
        res_dict['question'] = res.question_text
        res_dict['response'] = res.response
        res_dict['score'] = res.weight
        payload["assessmentResponses"].append(res_dict)
        
    payload["assessmentResult"] = assessment_score(risk)
    payload["phoneNumber"] = str(user.phone_number)
    payload["symptoms"] = [i.name for i in h_status._meta.get_fields() if getattr(h_status, i.name) == True]

    headers = {
        "Content-Type": "application/json",
        "token": settings.API_TOKEN
    }

    r = requests.post(
        f"{settings.BASE_API_URL}{settings.ASSESSMENT_ENDPOINT}",
        data=payload,
        headers=headers
    )
    print(r.text)
