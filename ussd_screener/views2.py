import json

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from .constants import LANG_DICT, API_PAYLOAD, WEIGHTS
from .models import Option, Page, Session, Survey
from .tasks import send_mail_to_admin, push_to_server
from .utils import (get_response, get_response_text, get_state_lga, get_text, get_usr_res,
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
    print(data)
    ssn_msisdn = data.get("session_msisdn")
    ssn_operation = data.get("session_operation")
    ssn_type = data.get("session_type")
    ssn_msg = data.get("session_msg")
    ssn_id = data.get("session_id")
    ssn_from = data.get("session_from")

    # user = get_ussd_user(ssn_msisdn)
    # survey = Survey.objects.get(service_code=ssn_from)
    # health_status = HealthStatus.objects.get(respondent=user)
    # session = log_survey_session(user, survey, ssn_id)
    # pages = session.survey.pages
    response = {}

    if ssn_operation == 'begin':
        # message, _, _ = get_response(pages, "0")
        response['session_operation'] = 'continue'
        response['session_type'] = 1
        response['session_id'] = ssn_id
        response['session_msg'] = "Welcome to eBanking.\nPlease select your payment channel.\n1) Card\n2) Bank Account\n3) Wallet"
        response['session_from'] = ssn_from.split('*')[1]

    return response


@csrf_exempt
def ussd_callback(request):
    response = process_request(request.GET)
    return JsonResponse(response)
