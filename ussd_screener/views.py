from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from .constants import LANG_DICT
from .models import Option, Page, Session, Survey
from .tasks import send_mail_to_admin
from .utils import (get_response, get_response_text, get_state_lga, get_text,
                    log_survey_session, update_status)


def get_health_status(condition, text_list, status, lang, pages):
    for i in range(4, 11):
        if i < 10:
            # if split text length equals symptom key
            if condition == i:
                update_status(text_list, status, str(i))
                response = get_response(
                                pages, f"{lang}*{i-1}"
                            )
                return response
        else:
            if (
                status.risk_level == "high" or
                status.risk_level == "very high"
            ):
                # send_mail_to_admin.delay(user_id=user.id)
                response = get_response(
                                pages, f"{lang}*{i-1}"
                            )
            elif status.risk_level == "medium":
                response = get_response(
                                pages, f"{lang}*{i}"
                            )
            else:
                response = get_response(
                                pages, f"{lang}*{i+1}"
                            )

            return response


def process_request(data):
    session_id = data.get("sessionId")
    service_code = data.get("serviceCode")
    phone_number = data.get("phoneNumber")
    text = data.get("text")

    user = get_ussd_user(phone_number)
    survey = Survey.objects.get(service_code=service_code)
    health_status = HealthStatus.objects.get(respondent=user)
    session = log_survey_session(user, survey, session_id)
    pages = session.survey.pages
    text_list = text.split("*")
    lang_id = text_list[0]
    response = ""

    if text == "":
        response = get_response(pages, "0")
        return response

    elif text in LANG_DICT:
        setattr(user, "language", LANG_DICT[text])
        user.save()
        response = get_response(
                        pages, text
                    )
        return response

    elif text == f"{lang_id}*1":
        response = get_response(
                        pages, text
                    )
        return response

    elif text == f"{lang_id}*1*1" or text == f"{lang_id}*1*1*99*0":
        state, lgas = get_state_lga(24)
        user.state = state
        user.save()
        response = get_response(
                        pages, f"{lang_id}*1*1"
                    )
        return response

    elif text == f"{lang_id}*1*1*99": # if next lga page was selected
        response = get_response(
                        pages, f"{lang_id}*1*1*99"
                    )
        return response

    elif get_text(text, 4) == f"{lang_id}*1*1*99":
        _, lgas = get_state_lga(24)
        option = text_list[-1]

        if option == "0":
            response = get_response(
                        pages, f"{lang_id}*1*1"
                    )
            return response

        elif option == "99":
            response = get_response(
                        pages, f"{lang_id}*1*1*99"
                    )
            return response

        else:
            prev_page_list = session.prev_page_id.split("*")

            if len(prev_page_list) > 1:
                diff = len(text_list) - len(prev_page_list)

                if diff >= 1:
                    diff = diff + 3
                    response = get_health_status(
                                    diff, text_list,
                                    health_status, lang_id, pages
                                )
                    return response

            else:
                for i in range(1, 21):
                    if i == int(option):
                        user.lga = lgas[int(option)-1]['name']
                        user.save()
                        session.prev_page_id = text
                        session.save()
                        response = get_response(
                            pages, f"{lang_id}*2"
                        )
                        return response

    elif get_text(text, 3) == f"{lang_id}*1*1":
        list_len = len(text_list)
        response = get_health_status(
                        list_len, text_list,
                        health_status, lang_id, pages
                    )
        return response

    elif text == f"{lang_id}*1*2":
        response = get_response(
                        pages, f"{lang_id}*2"
                    )
        return response

    elif get_text(text, 3) == f"{lang_id}*1*2":
        list_len = len(text_list)
        response = get_health_status(
                        list_len, text_list,
                        health_status, lang_id, pages
                    )
        return response

    return response


@csrf_exempt
def ussd_callback(request):
    response = ""
    if request.method == 'POST':
        response = process_request(request.POST)
    return HttpResponse(response)
