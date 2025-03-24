from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils.timezone import now, localtime
from datetime import timedelta

# TODO make seperate section for daily / other missions in missions.html

# ------------------------------------------------------
# USER CLASS - HANDLES LOGIN DATA, ACCOUNT TYPE...
# ------------------------------------------------------
class User(AbstractUser):
    USER_TYPES = (
        ('player', 'Player'),
        ('game_keeper', 'Game Keeper'),
        ('developer', 'Developer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='player')

    # For login streaks:
    login_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def calc_login_streak(self):
        today = localtime(now()).date()

        # Already logged in today - return as usual.
        if self.last_login_date == today:
            #print(f"No streak increase: {self.login_streak}")
            return
        
        # Continue streak if logged in on a consecutive day.
        elif self.last_login_date == today - timedelta(days=1):
            self.login_streak += 1
            # Reward user for logging in for a week straight:
            if self.login_streak == 7:
                #print(f"\nReward given. (Streak: {self.login_streak})\n") 
                self.reward_user()
                return

        # Reset streak if neither of the above are true.
        else:
            self.login_streak = 1
            #print(f"Streak reset: {self.login_streak}")  

        self.last_login_date = today
        self.save()

    def reward_user(self):
        profile, created = Profile.objects.get_or_create(user=self)
        #print(f"Rewarding user {self.username}, previous score: {profile.score}")
        profile.score += 100   # Placeholder; should probably assign a badge/other reward.
        profile.save()
        self.login_streak = 0
        #print(f"New score: {profile.score}, streak reset to {self.login_streak}")
        return
    
# ------------------------------------------------------
# TEAM CLASS - HANDLES USER TEAMS
# ------------------------------------------------------
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    team_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="led_teams")
    members = models.ManyToManyField(User, related_name="teams", blank=True)
    score = models.IntegerField(default=0)

    # Join the team:
    def add_member(self, user):
        if user not in self.members.all():
            self.members.add(user)
            user.profile.team = self
            print(self.members.all())
            print(user.profile.team)
            self.update_team()

    # Remove a member from your team:
    def remove_member(self, user):
        if user in self.members.all():
            self.members.remove(user)
            user.profile.team = None
            self.save()
            self.update_team()

    # Update the cumulative team score and DB:
    def update_team(self):
        self.score = sum(member.profile.score for member in self.members.all())
        self.save()

    def __str__(self):
        return self.name
    
# ------------------------------------------------------
# PROFILE CLASS - HANDLES USER PROFILES & RELATED DATA
# ------------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    friend_requests = models.ManyToManyField(User, related_name = "friend_requests")
    friend_list = models.ManyToManyField(User, related_name = "friend_list")

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")

    def __str__(self):
        return f'{self.user.username} Profile'
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# ------------------------------------------------------
# MISSION CLASSES - HANDLES ALL MISSION TYPES / SCENARIOS
# ------------------------------------------------------
class Mission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=10)
    requires_location = models.BooleanField(default=False)  # To differentiate between location/honour-system missions
    latitude = models.FloatField(null=True, blank=True)     # Holds location data (v)
    longitude = models.FloatField(null=True, blank=True)    # for location missions.

    mtypes = (
        ("one time", "one time"),
        ("daily", "daily"),
        ("weekly", "weekly"),
        ("repar", "repearing at arbitrary intervals")
    )

    mission_type = models.CharField(choices=mtypes, max_length = 40, default="one time")

    is_repeating = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class UserMission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = \
        models.PositiveBigIntegerField(default=0)
        # models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.mission.name}"
    
# For users uploading photos after a location-required mission:
class MissionPhoto(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mission_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.profile.user.username} - Mission: {self.mission.name}"
    