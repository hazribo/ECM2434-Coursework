from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    # User management:
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    # Default pages:
    path('', home, name='home'),
    path('about', about, name='about'),
    path('game', game, name='game'),
    path("leaderboard/", leaderboard, name='leaderboard'),
    # Profile:
    path('profile/', redirect_to_profile, name='redirect_to_profile'),
    path('profile/<str:username>/', profile, name='profile'),
    path("profile/<str:username>/accept/<str:accepter_id>/<str:accepted_id>", accept_req),
    path("profile/<str:username>/reject/<str:rejecter_id>/<str:rejected_id>", reject_req),
    path('profile_update', profile_update, name='profile_update'),
    # Search urls:
    path('search/', search, name = "user search"),
    path("search/<str:idVal>/", addfriend, name='addfriend'),
    # Mission urls:
    path('missions/', missions, name='missions'),
    path('manage_missions/', manage_missions, name='manage_missions'),
    path('save_photo', save_photo, name='save_photo'),
    # Teams:
    path("teams/", manage_teams, name="teams"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
