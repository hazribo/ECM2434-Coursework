from .models import UserMission

def get_user_missions(profile):
    # get mission from a specific user profile
    user = profile.user
    missions = [user_mission for user_mission in UserMission.objects.filter(user=user)]
    return missions