from .models import USSDUser


def get_ussd_user(phone_number):
    user, _ = USSDUser.objects.get_or_create(
                    phone_number=phone_number
                )

    return user