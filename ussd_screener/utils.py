from .constants import STATES, SYMPTOMS
from .models import Session, SurveyResponse


def get_state_lga(index):
    state_dict = STATES[index]["state"]
    state = state_dict["name"]
    lgas = state_dict["locals"]

    return state, lgas

def log_survey_session(user, survey_id, id):
    try:
        session = Session.objects.select_related(
                    'survey'
                ).prefetch_related(
                    'survey__pages'
                ).get(
                    user=user,
                    session_id=id
                )
    except Session.DoesNotExist:
        session = Session.objects.create(
                    user=user,
                    survey_id=survey_id,
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
    parent_text = None
    parent_options = []
    # get text for question answered by user
    if page.parent:
         parent_text  = page.parent.text.split('CON')[1].strip()
         parent_options = page.parent.options.all()
    response = get_response_text(page)

    for option in page.options.all():
        response += f"{option} \n"

    return response, parent_text, parent_options

def update_status(text_list, obj, index):
    option = text_list[-1]
    # if option is 1
    if option == "1":
        setattr(obj, SYMPTOMS[index], True)
    # if option is 2
    elif option == "2":
        setattr(obj, SYMPTOMS[index], False)
    obj.save()
    return option, SYMPTOMS[index]

def log_response(
    session, text,
    response, weight=0
):
    """Log each survey response"""
    response = SurveyResponse(
        session = session, 
        question_text=text,
        response=response,
        weight=int(weight)
    )
    response.save()

def get_usr_res(id, options):
    res = options[int(id) - 1]
    res = res.text.split(".")[0]
    return res

def assessment_score(assessment):
    if assessment == "low":
        return 2
    elif assessment == "medium":
        return 3
    elif assessment == "high":
        return 4
    else:
        return 1
