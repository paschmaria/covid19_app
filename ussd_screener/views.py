from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from .constants import LANG_DICT, API_PAYLOAD, WEIGHTS
from .models import Option, Page, Session, Survey
from .tasks import send_mail_to_admin, push_to_server
from .utils import (get_response, get_response_text, get_state_lga, get_text, get_usr_res,
                    log_survey_session, log_response, update_status)

# FAD Analysis: Fear, Accusation and Doubt


def get_health_status(condition, text_list, session, status, lang, pages):
    for i in range(4, 11):
        if i < 10:
            if condition == i:
                text, symptom = update_status(text_list, status, str(i))
                response, p_text, p_options = get_response(
                                pages, f"{lang}*{i-1}"
                            )
                usr_res = get_usr_res(text, p_options)
                weight = WEIGHTS[symptom]
                log_response(session, p_text, usr_res, weight=weight) # health status
                return response
        else:
            text, symptom = update_status(text_list, status, str(i))
            if (
                status.risk_level == "high" 
            ):
                send_mail_to_admin.delay(status_id=status.id)
                response, p_text, p_options = get_response(
                                pages, f"{lang}*{i-1}"
                            )
            elif status.risk_level == "medium":
                response, p_text, p_options = get_response(
                                pages, f"{lang}*{i}"
                            )
            else:
                response, p_text, p_options = get_response(
                                pages, f"{lang}*{i+1}"
                            )

            usr_res = get_usr_res(text, p_options)
            weight = WEIGHTS[symptom]
            log_response(session, p_text, usr_res, weight=weight) # health status
            push_to_server.delay(session_id=session.session_id)
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
    # print(text_list)

    if text == "":
        # get first page
        response, _, _ = get_response(pages, "0")
        return response

    elif text in LANG_DICT:
        # set user's default language
        # render GDPR buy-in screen
        setattr(user, "language", LANG_DICT[text])
        user.save()
        response, p_text, p_options = get_response(
                                        pages, text
                                    )
        usr_res = get_usr_res(text, p_options)
        log_response(session, p_text, usr_res) # language
        return response

    elif text == f"{lang_id}*1":
        # render LGA screen
        response, p_text, p_options = get_response(
                        pages, text
                    )
        usr_res = get_usr_res(1, p_options)
        log_response(session, p_text, usr_res) # GDPR buyin
        return response

    elif text == f"{lang_id}*1*1" or text == f"{lang_id}*1*1*99*0":
        # set user LGA
        state, lgas = get_state_lga(24)
        user.state = state
        user.save()
        response, p_text, p_options = get_response(
                        pages, f"{lang_id}*1*1"
                    )
        usr_res = get_usr_res(1, p_options)
        log_response(session, p_text, usr_res) # State
        return response

    elif text == f"{lang_id}*1*1*99":
        # if next LGA screen was selected
        # render next LGA screen (11 - 20)
        response, p_text, p_options = get_response(
                        pages, text
                    )
        return response

    elif get_text(text, 4) == f"{lang_id}*1*1*99":
        # if user came from second LGA screen
        _, lgas = get_state_lga(24)
        option = text_list[-1]

        # if back option was selected
        if option == "0":
            response, p_text, p_options = get_response(
                        pages, f"{lang_id}*1*1"
                    )
            return response

        # if next option was selected
        elif option == "99":
            response, p_text, p_options = get_response(
                        pages, f"{lang_id}*1*1*99"
                    )
            return response

        else:
            # if any of the LGAs had been selected
            # get the previous page (fever screen)
            prev_page_list = session.prev_page_id.split("*")

            if len(prev_page_list) > 1:
                diff = len(text_list) - len(prev_page_list)

                # as the user goes further away from the fever screen,
                # render the subsequent screens
                if diff >= 1:
                    diff = diff + 3
                    response = get_health_status(
                                    diff, text_list, session,
                                    health_status, lang_id, pages
                                )
                    return response

            else:
                for i in range(1, 21):
                    # get selected LGA and render fever screen
                    if i == int(option):
                        lga = lgas[int(option)-1]['name']
                        user.lga = lga
                        # set fever screen as previous screen
                        session.prev_page_id = text
                        session.save()
                        response, p_text, p_options = get_response(
                            pages, f"{lang_id}*2"
                        )
                        log_response(session, p_text, lga) # LGA
                        return response

    elif get_text(text, 3) == f"{lang_id}*1*1":
        # if any of the LGAs had been selected
        # get the previous page (fever screen)
        prev_page_list = session.prev_page_id.split("*")

        if len(prev_page_list) > 1:
            list_len = len(text_list)
            condition = list_len - 1
            response = get_health_status(
                            condition, text_list, session,
                            health_status, lang_id, pages
                        )
            return response

        else:
            _, lgas = get_state_lga(24)
            option = text_list[-1]
            for i in range(1, 21):
                # get selected LGA and render fever screen
                if i == int(option):
                    lga = lgas[int(option)-1]['name']
                    user.lga = lga
                    user.save()
                    # set fever screen as previous screen
                    session.prev_page_id = text
                    session.save()
                    response, p_text, p_options = get_response(
                        pages, f"{lang_id}*2"
                    )
                    log_response(session, p_text, lga) # LGA
                    return response

    elif text == f"{lang_id}*1*2":
        response, p_text, p_options = get_response(
                        pages, f"{lang_id}*2"
                    )
        log_response(session, p_text, "No") # GDPR buyin
        return response

    elif get_text(text, 3) == f"{lang_id}*1*2":
        list_len = len(text_list)
        response = get_health_status(
                        list_len, text_list, session,
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
