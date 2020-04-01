from .constants import STATES, SYMPTOMS
from .models import Session


def get_state_lga(index):
    state_dict = STATES[index]["state"]
    state = state_dict["name"]
    lgas = state_dict["locals"]

    return state, lgas

def log_survey_session(user, survey, id):
    session, _ = Session.objects.get_or_create(
                    user=user,
                    survey=survey,
                    session_id=id
                )
    return session

def get_text(text, part):
    text = text.split("*")
    return "*".join(text[:part])

def get_response_text(page):
    response  = f"{page.text} \n"
    response += "" if page.extra_text == "" else f"{page.extra_text} \n"
    return response

def get_response(obj, page_num):
    page = obj.get(page_num=page_num)
    response = get_response_text(page)

    for option in page.options.all():
        response += f"{option} \n"

    return response

def update_status(text_list, obj, index):
    # if option is 1
    if text_list[-1] == "1":
        setattr(obj, SYMPTOMS[index], True)
    # if option is 2
    elif text_list[-1] == "2":
        setattr(obj, SYMPTOMS[index], False)
    obj.save()
