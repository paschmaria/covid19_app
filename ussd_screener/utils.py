from .constants import STATES
from .models import Session


def get_state_lga(index):
    state_dict = STATES[index]["state"]
    state = state_dict["name"]
    lgas = state_dict["locals"]

    return state, lgas

def log_survey_session(survey, id):
    session = Session.objects.create(
                    survey=survey,
                    session_id=id
                )
    return session
