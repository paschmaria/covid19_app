from accounts.models import HealthStatus
from accounts.utils import get_ussd_user

from ussd_screener.constants import LANG_DICT, WEIGHTS, HTG_SYMPTOMS
from ussd_screener.models import Survey
from ussd_screener.tasks import send_mail_to_admin, push_to_server
from ussd_screener.utils import (clean, get_response_text, get_location,
                                log_survey_session, log_response)


class USSDService:
    """
    Service class for managing entire USSD workflow

    :param int session_msisdn: User Phone number (in international format)
    :param str session_operation: USSD Operation category (one of begin, continue, end or abort)
    :param str session_type: USSD message content (one of 1, 2, 3, or 4) See https://docs.hollatags.com/ussd/inbound#inbound
    :param int session_msg: USSD message content (must be <= 160 chars)
    :param int session_id: User session ID
    :param str session_from: Originating USSD code
    :param str session_mno: Mobile Network Operator
    """

    def __init__(self, data):
        self.ssn_msisdn = data.get("session_msisdn")
        self.ssn_operation = data.get("session_operation")
        self.ssn_type = data.get("session_type")
        self.ssn_msg = data.get("session_msg")
        self.ssn_id = data.get("session_id")
        self.ssn_from = data.get("session_from")

        self.user = get_ussd_user(self.ssn_msisdn)
        self.survey = Survey.objects.get(service_code=self.ssn_from)
        self.health_status = HealthStatus.objects.get(respondent=self.user)
        self.session = log_survey_session(self.user, self.survey.id, self.ssn_id)
        self.pages = self.session.survey.pages

    def process_request(self):
        page_num = '' # page to be rendered
        # get id of the previous page
        prev_page_id = self.session.prev_page_id
        pp_id_list = prev_page_id.split('*')

        if self.ssn_operation == 'begin':
            page_num = "0"
            self.ssn_operation = 'continue'
            self.ssn_type = 1
        else:
            lang_id = pp_id_list[0]
            self.ssn_type = 1

            if prev_page_id == '0':
                # render consent buy-in
                if self.ssn_msg in LANG_DICT:
                    setattr(self.user, "language", LANG_DICT[self.ssn_msg])
                    self.user.save()

                page_num = clean(self.ssn_msg)
                self.ssn_operation = 'continue'
            elif prev_page_id == lang_id:
                # render State screen
                page_num = f"{lang_id}*1"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*1":
                if clean(self.ssn_msg) == '1':
                    # save User's State
                    state = get_location(24)
                    self.user.state = state
                    self.user.save()
                    # render LGA screen
                    page_num = f"{lang_id}*1*1"
                else:
                    # render fever screen
                    page_num = f"{lang_id}*2"

                self.ssn_operation = 'continue'
            elif (
                prev_page_id == f"{lang_id}*1*1" or
                prev_page_id == f"{lang_id}*1*1*99"
            ):
                # get LGAs
                _, lgas = get_location(24, lga=True)

                # if back option was selected
                if clean(self.ssn_msg) == "0":
                    page_num = f"{lang_id}*1*1"
                # if next option was selected
                elif clean(self.ssn_msg) == "99":
                    page_num = f"{lang_id}*1*1*99"
                else:
                    option = clean(self.ssn_msg)
                    if int(option) in range(1, 21):
                        lga = lgas[int(option)-1]['name']
                        self.user.lga = lga
                        self.user.save()
                        # render fever screen
                        page_num = f"{lang_id}*2"

                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*2":
                if clean(self.ssn_msg) == "1":
                    self.health_status.fever = True
                else:
                    self.health_status.fever = False
                
                self.health_status.save()
                # render cough screen
                page_num = f"{lang_id}*3"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*3":
                if clean(self.ssn_msg) == "1":
                    self.health_status.cough = True
                else:
                    self.health_status.cough = False

                self.health_status.save()
                # render aches screen
                page_num = f"{lang_id}*4"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*4":
                if clean(self.ssn_msg) == "1":
                    self.health_status.aches = True
                else:
                    self.health_status.aches = False
                
                self.health_status.save()
                # render difficulty in breathing screen
                page_num = f"{lang_id}*5"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*5":
                if clean(self.ssn_msg) == "1":
                    self.health_status.difficult_breath = True
                else:
                    self.health_status.difficult_breath = False

                self.health_status.save()
                # render sore throat screen
                page_num = f"{lang_id}*6"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*6":
                if clean(self.ssn_msg) == "1":
                    self.health_status.sore_throat = True
                else:
                    self.health_status.sore_throat = False

                self.health_status.save()
                # render primary contact screen
                page_num = f"{lang_id}*7"
                self.ssn_operation = 'continue'
            elif prev_page_id == f"{lang_id}*7":
                if clean(self.ssn_msg) == "1":
                    self.health_status.primary_contact = True
                else:
                    self.health_status.primary_contact = False

                self.health_status.save()
                # render secondary contact screen
                page_num = f"{lang_id}*8"
                self.ssn_operation = 'continue'
                
            elif prev_page_id == f"{lang_id}*8":
                if clean(self.ssn_msg) == "1":
                    self.health_status.secondary_contact = True
                else:
                    self.health_status.secondary_contact = False
                
                self.health_status.save()

                if self.health_status.risk_level == 'low':
                    # render low risk screen
                    page_num = f"{lang_id}*11"
                elif self.health_status.risk_level == 'medium':
                    # render medium risk screen
                    page_num = f"{lang_id}*10"
                else:
                    # render high risk screen
                    page_num = f"{lang_id}*9"
                    send_mail_to_admin.delay(
                        status_id=self.health_status.id)

                self.ssn_operation = 'end'
                self.ssn_type = 4
                push_to_server.delay(session_id=self.session.session_id)
        
        # save id of page being rendered as previous page
        self.session.prev_page_id = page_num
        self.session.save()
        # get page/screen and message
        message, page = self.get_message(
                            page_num
                        )
        # log previous user action
        self.log_response(page)
        return message

    def get_message(self, page_num):
        """Get USSD screen message"""

        # get instance of page using the page number
        page = self.pages.select_related(
                'parent'
            ).prefetch_related(
                'options', 'parent__options'
            ).get(page_num=page_num)
        # generate response from page text/extra text
        message = get_response_text(
            page.text,
            page.extra_text
        )

        # add page options to message
        for option in page.options.all():
            message += f"{option} \n"

        return message, page

    def log_response(self, page):
        parent = page.parent
        weight = 0

        # first, get previous page text and
        # chosen option, if available
        if parent:
            parent_text = parent.text.strip()
            parent_options = parent.options.all()
            option = clean(self.ssn_msg)
            
            if int(option) == 0:
                option_index = int(option)
            elif int(option) == 99:
                option_index = 10
            elif int(option) <= 10:
                option_index = int(option) - 1
            else:
                option_index = int(option) - 11

            parent_id = parent.page_num.split('*', 1)[-1]
            if parent_id in HTG_SYMPTOMS:
                symptom = HTG_SYMPTOMS[parent_id]
                weight = WEIGHTS[symptom]

            # get option chosen by user
            chosen_option = parent_options[option_index].text
            log_response(self.session.pk, parent_text, chosen_option, weight)

    def render_response(self):
        msg = self.process_request()
        response = {}
        response['session_operation'] = self.ssn_operation
        response['session_type'] = self.ssn_type
        response['session_id'] = self.ssn_id
        response['session_msg'] = msg
        response['session_from'] = self.ssn_from.split('*')[1]
        return response
