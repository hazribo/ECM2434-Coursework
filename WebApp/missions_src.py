from .models import UserMission, Mission
from time import time as getNow

def get_user_missions(profile):
    # get mission from a specific user profile
    user = profile.user
    missions = [user_mission for user_mission in UserMission.objects.filter(user=user)]
    return missions


_seconds_per_day = 0; #24 * 60 * 60
TimePeriodsToSeconds = {
    "monthly" : 30 * _seconds_per_day,  # 30 days p month * 24 hr per day * 60^2 seconds p hr
    "weekly"  :  7 * _seconds_per_day,
    "daily"   :  1 * _seconds_per_day
}


def tick_repeating_missions(profile):
    
    missions_to_tick = [
        uM for uM in UserMission.objects.filter(user=profile.user)
        if uM.mission.is_repeating and uM.completed
    ]

    timeNow = getNow()

    # for each mission that needs to be ticked
    for userMission in missions_to_tick:

        # if time since it has been completed > corresponding reset time
        timeSince = (timeNow - userMission.date_completed)
        if timeSince > TimePeriodsToSeconds[userMission.mission.mission_type]:

            # reset
            userMission.completed = False
            userMission.save()

            print(f"reset {userMission}")

    