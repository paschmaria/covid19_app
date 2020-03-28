from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from accounts.utils import get_ussd_user

from .models import Option, Page, Session, Survey
from .utils import get_state_lga, log_survey_session


def process_request(data):
    session_id = data.get("sessionId")
    service_code = data.get("serviceCode")
    phone_number = data.get("phoneNumber")
    text = data.get("text")

    survey = Survey.objects.get(service_code=service_code)
    session = log_survey_session(survey, session_id)
    user = get_ussd_user(phone_number)
    page = ""

    if text == "":
        response  = "CON Please select a language: \n"
        response += "1. English \n"
        response += "2. Yoruba \n"
        response += "3. Igbo \n"
        response += "4. Hausa"
    elif text == "1":
        user.language = 'English'
        user.save()

        response = "CON Your Language has been set to English. \n"
        response += "By continuing with this survey, you consent that the \
                    data collected would be used for the sole purposes of: \
                    understanding your risk profile for COVID-19, \
                    helping to facilitate testing if necessary, \
                    supporting the efforts of the government in overcoming this pandemic. \n"
        response += "1. I agree"
    elif text == "1*1":
        response  = "CON Do you currently live in Lagos: \n"
        response += "1. Yes \n"
        response += "2. No"
    elif text == "1*1*1":
        state, lgas = get_state_lga(24)
        user.state = state
        user.save()

        response = "CON Which LGA in Lagos State do you live? \n"
        for i in range(9):
            response += f"{lgas[i]['id']}. {lgas[i]['name']} \n"
        response += "99. Next"
    elif text == "1*1*1*1":
        state, lgas = get_state_lga(24)
        user.lga = lgas[1]['name']
        user.save()
            
    return response


@csrf_exempt
def ussd_callback(request):
    response = ""

    if request.method == 'POST':
        response = process_request(request.POST)

    return HttpResponse(response)