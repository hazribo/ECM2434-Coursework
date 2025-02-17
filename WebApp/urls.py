from django.urls import path
from .views import register, user_login, user_logout, home, leaderboard
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path("leaderboard/", leaderboard, name='leaderboard'),

    path('', home, name='home'),
]
