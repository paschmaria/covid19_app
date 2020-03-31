from .constants import STATES
from .models import Session


def get_state_lga(index):
    state_dict = STATES[index]["state"]
    state = state_dict["name"]
    lgas = state_dict["locals"]

    return state, lgas

def log_survey_session(user, survey, id):
    session = Session.objects.create(
                    user=user,
                    survey=survey,
                    session_id=id
                )
    return session

def get_list(text_list, index, option=None):
    pages = []

    if option is not None:
        if text_list[:-1] != option:
            return pages

    if text_list[:4] == ["1","1","1", "99"]:
        for i in range(11, 21):
            text_list[index] = str(i)
            text = "*".join(text_list)
            pages.append(text)
    elif text_list[:3] == ["1","1","1"]:
        for i in range(1, 11):
            text_list[index] = str(i)
            text = "*".join(text_list)
            pages.append(text)
    return pages
