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


@csrf_exempt
def ussd_callback(request):
    ussd_data = USSDService(request.GET)
    response = ussd_data.render_response()
    return JsonResponse(response)
