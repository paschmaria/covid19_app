import json

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from ussd_screener.constants import LANG_DICT, API_PAYLOAD, WEIGHTS
from ussd_screener.models import Option, Page, Session, Survey
from ussd_screener.services import USSDService
from ussd_screener.tasks import send_mail_to_admin, push_to_server
from ussd_screener.utils import (get_response, get_response_text, get_location, get_text, get_usr_res,
                    log_survey_session, log_response, update_status)


def process_request(data):
    """
    session_msisdn (int): User Phone number (in international format)
    session_operation (str): USSD Operation category (one of begin, continue, end or abort)
    session_type (str): USSD message content (one of 1, 2, 3, or 4) See https://docs.hollatags.com/ussd/inbound#inbound
    session_msg (int): USSD message content (must be <= 160 chars)
    session_id (int): User session ID
    session_from (str): Originating USSD code
    session_mno (str): Mobile Network Operator
    """
    ssn_msisdn = data.get("session_msisdn")
    ssn_operation = data.get("session_operation")
    ssn_type = data.get("session_type")
    ssn_msg = data.get("session_msg")
    ssn_id = data.get("session_id")
    ssn_from = data.get("session_from")

    user = get_ussd_user(ssn_msisdn)
    survey = Survey.objects.get(service_code=ssn_from)
    health_status = HealthStatus.objects.get(respondent=user)
    session = log_survey_session(user, survey.id, ssn_id)
    pages = session.survey.pages
    response = {}

    if ssn_operation == 'begin':
        message, _, _ = get_response(pages, "0")
        response['session_operation'] = 'continue'
        response['session_type'] = 1
        response['session_id'] = ssn_id
        response['session_msg'] = message
        response['session_from'] = ssn_from.split('*')[1]
    elif ssn_operation == 'continue':
        response['session_operation'] = 'continue'
        response['session_type'] = 1
        response['session_id'] = ssn_id
        print(pages)

        setattr(user, "language", LANG_DICT[ssn_msg])
        user.save()
        message, p_text, p_options = get_response(
                                        pages, ssn_msg
                                    )
        usr_res = get_usr_res(ssn_msg, p_options)
        log_response(session, p_text, usr_res) # language

        response['session_msg'] = message
        response['session_from'] = ssn_from.split('*')[1]
    else:
        response['session_operation'] = "end"
        response['session_type'] = 4
        response['session_id'] = ssn_id
        response['session_msg'] = "Thank you."

    return response


@csrf_exempt
def ussd_callback(request):
    print(request.GET)
    ussd_data = USSDService(request.GET)
    response = ussd_data.render_response()
    return JsonResponse(response)
