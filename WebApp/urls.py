from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path("leaderboard/", leaderboard, name='leaderboard'),
    path('', home, name='home'),
    path('profile/', redirect_to_profile, name='redirect_to_profile'),
    path('profile/<str:username>/', profile, name='profile'),
    path('about', about, name='about'),
    path('game', game, name='game'),
    path("search/", search, name = "user search")
]
