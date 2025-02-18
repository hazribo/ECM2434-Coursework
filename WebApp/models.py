from django.contrib.auth.models import AbstractUser, User
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('player', 'Player'),
        ('game_keeper', 'Game Keeper'),
        ('developer', 'Developer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='player')

    score = models.IntegerField(default=0)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} Profile'



# class Score(models.Model):
    