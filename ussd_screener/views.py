from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from .constants import LANG_DICT
from .models import Option, Page, Session, Survey
from .utils import (get_response, get_response_text, get_state_lga, get_text,
                    log_survey_session, update_status)


def process_request(data):
    session_id = data.get("sessionId")
    service_code = data.get("serviceCode")
    phone_number = data.get("phoneNumber")
    text = data.get("text")

    survey = Survey.objects.get(service_code=service_code)
    user = get_ussd_user(phone_number)
    health_status = HealthStatus.objects.get(respondent=user)
    session = log_survey_session(user, survey, session_id)
    pages = session.survey.pages
    text_list = text.split("*")
    page = ""
    response = ""
    # print(text_list, len(text_list))

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

    elif text == "1*1":
        response = get_response(
                        pages, text
                    )
        return response

    elif text == "1*1*1" or text == "1*1*1*99*0":
        state, lgas = get_state_lga(24)
        user.state = state
        user.save()
        page = pages.get(page_num="1*1*1")
        response  = get_response_text(page)

        for i in range(10):
            response += f"{lgas[i]['id']}. {lgas[i]['name']} \n"
        response += "99. Next"

        return response

    elif text == "1*1*1*99": # if next lga page was selected
        _, lgas = get_state_lga(24)
        page = pages.get(page_num="1*1*1")
        response  = get_response_text(page)

        for i in range(10, 20):
            response += f"{lgas[i]['id']}. {lgas[i]['name']} \n"
        response += "0. Back"

        return response

    elif get_text(text, 4) == "1*1*1*99":
        _, lgas = get_state_lga(24)
        option = text_list[-1]

        if option == "0":
            page = pages.get(page_num="1*1*1")
            response  = get_response_text(page)

            for i in range(10):
                response += f"{lgas[i]['id']}. {lgas[i]['name']} \n"
            response += "99. Next"

            return response
        elif option == "99":
            page = pages.get(page_num="1*1*1")
            response  = get_response_text(page)

            for i in range(10, 20):
                response += f"{lgas[i]['id']}. {lgas[i]['name']} \n"
            response += "0. Back"

            return response
        else:
            prev_page_list = session.prev_page_id.split("*")

            if len(prev_page_list) > 1:
                diff = len(text_list) - len(prev_page_list)

                if diff >= 1:
                    diff = diff + 3

                    for i in range(4, 12):
                        if i < 11:
                        # if split text length equals symptom key
                            if diff == i:
                                update_status(text_list, health_status, str(i))
                                response = get_response(
                                                pages, f"1*{i-1}"
                                            )
                                return response
                        else:
                            if (
                                health_status.risk_level == "high" or
                                health_status.risk_level == "very high"
                            ):
                                # send mail or sms
                                response = get_response(
                                                pages, f"1*{i-1}"
                                            )
                            elif health_status.risk_level == "medium":
                                response = get_response(
                                                pages, f"1*{i}"
                                            )
                            else:
                                response = get_response(
                                                pages, f"1*{i+1}"
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
                            pages, "1*2"
                        )
                        return response

    elif get_text(text, 3) == "1*1*1":
        for i in range(4, 12):
            if i < 11:
                # if split text length equals symptom key
                if len(text_list) == i:
                    update_status(text_list, health_status, str(i))
                    response = get_response(
                                    pages, f"1*{i-1}"
                                )
                    return response
            else:
                if (
                    health_status.risk_level == "high" or
                    health_status.risk_level == "very high"
                ):
                    # send mail or sms
                    response = get_response(
                                    pages, f"1*{i-1}"
                                )
                elif health_status.risk_level == "medium":
                    response = get_response(
                                    pages, f"1*{i}"
                                )
                else:
                    response = get_response(
                                    pages, f"1*{i+1}"
                                )

                return response
    
    elif text == "1*1*2":
        response = get_response(
                        pages, "1*2"
                    )
        return response

    elif get_text(text, 3) == "1*1*2":
        for i in range(4, 12):
            if i < 11:
                # if split text length equals symptom key
                if len(text_list) == i:
                    update_status(text_list, health_status, str(i))
                    response = get_response(
                                    pages, f"1*{i-1}"
                                )
                    return response
            else:
                if (
                    health_status.risk_level == "high" or
                    health_status.risk_level == "very high"
                ):
                    # send mail or sms
                    response = get_response(
                                    pages, f"1*{i-1}"
                                )
                elif health_status.risk_level == "medium":
                    response = get_response(
                                    pages, f"1*{i}"
                                )
                else:
                    response = get_response(
                                    pages, f"1*{i+1}"
                                )

                return response

    return response


@csrf_exempt
def ussd_callback(request):
    response = ""

    if request.method == 'POST':
        response = process_request(request.POST)

    return HttpResponse(response)
