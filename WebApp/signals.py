from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import User

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    #Runs calc_login_streak() on user login:
    if isinstance(user, User):
        user.calc_login_streak()