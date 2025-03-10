from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.core.management import call_command
import json
from .models import *
from .forms import *
from .leaderboard_src import generate_leaderboard_image
from .search_src import search_for_username
from .friendsystem_src import *
from .missions_src import get_user_missions
from geopy.distance import geodesic

# Friend system code:
_IGNORE_PASSWORD_REQS = True
_NoSearchString = "NONE"

# returned by view function in order to not change the page
# active at all
def unchanged(request, *args, **kwargs):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def accept_req(request, accepter_id, accepted_id, **kwargs):
    record_friend_request_response(accepter_id, accepted_id, True)
    return unchanged(request)

def reject_req(request, rejecter_id, rejected_id, **kwargs):
    record_friend_request_response(rejecter_id, rejected_id, False)
    return unchanged(request)

# Helper functions for user roles/permissions:
def is_game_keeper_or_developer(user):
    return user.user_type in ['game_keeper', 'developer']
def is_developer(user):
    return user.user_type == 'developer'

# For adding/deleting missions (must be GK or Dev):
@login_required
@user_passes_test(is_game_keeper_or_developer)
def manage_missions(request):
    missions = Mission.objects.all()

    if request.method == "POST":
        # Handles adding or editing existing missions:
        mission_id = request.POST.get('mission_id')  # Get mission ID if editing
        if mission_id: # Editing existing mission:
            mission = get_object_or_404(Mission, id=mission_id)
            form = MissionForm(request.POST, instance=mission)
        else:  # Adding ew mission:
            form = MissionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('manage_missions')
    else:
        form = MissionForm()

    if request.method == "POST" and 'delete_mission_id' in request.POST:
        # Handles deleting missions:
        mission_id = request.POST['delete_mission_id']
        mission = get_object_or_404(Mission, id=mission_id)
        mission.delete()
        return HttpResponseRedirect(request.path)

    return render(request, 'WebApp/manage_missions.html', {
        'missions': missions,
        'form': form,
    })

# Location verification/saving:
ACCEPTABLE_DISTANCE = 50  # Allowed distance from mission location (can change to debug).
@csrf_exempt
@login_required
def verify_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mission_id = data.get('mission_id')
            user_lat = data.get('latitude')
            user_long = data.get('longitude')

            mission = Mission.objects.get(id=mission_id)
            today = timezone.now().date()

            # Get or create the UserMission
            user_mission, _ = UserMission.objects.get_or_create(
                user=request.user,
                mission=mission,
                date_completed=today
            )

            # If the mission does not require location verification:
            if not mission.requires_location:
                return redirect('/missions/')

            # If location is required but missing:
            if user_lat is None or user_long is None:
                return redirect('/missions/?status=location_failed')

            # Check if the user is within acceptable range
            mission_location = (mission.latitude, mission.longitude)
            user_location = (float(user_lat), float(user_long))
            distance = geodesic(mission_location, user_location).meters

            if distance <= ACCEPTABLE_DISTANCE:
                user_mission.completed = True
                user_mission.save()
                return redirect('/missions/?status=location_verified')
            else:
                return redirect(f'/missions/?status=too_far&distance={int(distance)}')

        except Exception as e:
            return redirect(f'/missions/?status=error&message={e}')

    return redirect('/missions/?status=invalid_request')

@login_required
def missions(request):
    today = timezone.now().date()

    # Generate default missions if none exist:
    if not Mission.objects.exists():
        call_command('generate_missions')

    # Handle POST request (on mission completion):
    if request.method == "POST":
        mission_id = request.POST.get("mission_id")
        mission = get_object_or_404(Mission, id=mission_id)

        # Get or create UserMission:
        user_mission, created = UserMission.objects.get_or_create(
            user=request.user,
            mission=mission,
            date_completed=today
        )

        # If the mission requires location, redirect to verify_location page
        if mission.requires_location and not user_mission.completed:
            return redirect('verify_location', mission_id=mission.id)

        # Toggle completion status for self-check missions
        if not mission.requires_location:
            user_mission.completed = not user_mission.completed
            user_mission.save()

            # Update user score
            profile = request.user.profile
            if user_mission.completed:
                profile.score += mission.points
            else:
                profile.score -= mission.points
            profile.save()

            return JsonResponse({
                "status": "success",
                "completed": user_mission.completed
            })

    # Ensure all missions are tracked in UserMission:
    all_missions = Mission.objects.all()
    user_missions = UserMission.objects.filter(user=request.user, date_completed=today)

    for mission in all_missions:
        UserMission.objects.get_or_create(user=request.user, mission=mission, date_completed=today)

    return render(request, 'WebApp/missions.html', {
        'missions': all_missions,
        'user_missions': user_missions,
        'status': request.GET.get('status'),
    })

@login_required
def verify_location(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)

    # Get or create UserMission
    user_mission, created = UserMission.objects.get_or_create(
        user=request.user,
        mission=mission,
        date_completed=request.user.profile.date_completed
    )

    # If the mission has already been completed, redirect back to the missions page
    if user_mission.completed:
        return redirect('missions')

    # Handle location verification logic:
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Validate the location (for simplicity, just check if the latitude and longitude match the mission's set values)
        if float(latitude) == mission.latitude and float(longitude) == mission.longitude:
            # Mark the mission as completed after successful location verification
            user_mission.completed = True
            user_mission.save()

            # Update the user's score
            profile = request.user.profile
            profile.score += mission.points
            profile.save()

            return redirect('missions')  # Redirect to the missions page after successful verification

        # If location does not match, provide an error message
        return render(request, 'WebApp/verify_location.html', {
            'mission': mission,
            'error': "Location does not match. Please try again."
        })

    return render(request, 'WebApp/verify_location.html', {'mission': mission})

def home(request):
    return render(request, 'WebApp/home.html')

def about(request):
    return render(request, 'WebApp/about.html')

@login_required
def game(request):
    username=request.user.username
        
    # Get data for provided username to display correct profile:
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(Profile, user=user)

    friend_list = get_friend_list(user_profile)

    user_missions = get_user_missions(user_profile)

    context = {
        'profile': user_profile,
        'friend_list' : friend_list,
        'user_missions': user_missions
    }
    return render(request, 'WebApp/game.html', context)

@login_required
def addfriend(request, idVal = None):
    send_friend_request(request.user.id, idVal)
    return unchanged(request);

def search(request):
    username = request.GET.get('username', _NoSearchString)
    matches = search_for_username(username)
    context = { 
        "search_name" : username,
        "results" : matches,
        "anyfound" : (len(matches) > 0)
    }
    return render(request, "WebApp/search.html", context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid() or _IGNORE_PASSWORD_REQS:
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page
    else:
        form = UserRegistrationForm()
    return render(request, 'WebApp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page
    else:
        form = AuthenticationForm()
    return render(request, 'WebApp/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def leaderboard(request): 
    if generate_leaderboard_image() is not None:
        # if fine and no error
        return render(request, 'WebApp/leaderboard.html')
    else:
        # if error, say so and redirect back home
        print("LEADERBOARD IMAGE GENERATION ERROR")
        return redirect('home')

@login_required
def profile(request, username=None):
    # No username provided; redirect to profile of user:
    if not username:
        if request.user.is_authenticated:
            return redirect('profile', username=request.user.username)
        else:
            # Redirect to login if the user is not authenticated:
            return redirect('login') 
        
    # Get data for provided username to display correct profile:
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(Profile, user=user)

    friend_request_list = get_friend_request_list(user_profile);
    friend_list = get_friend_list(user_profile)

    context = {
        'profile': user_profile,
        'req_list' : friend_request_list,
        'friend_list' : friend_list
    };

    return render(request, 'WebApp/profile.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'WebApp/profile_update.html', {'form': form})

def redirect_to_profile(request):
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    else:
        # redirect to login if not logged in - no profile to show:
        return redirect('login')

@user_passes_test(is_developer)
def developer_dashboard(request):
    return render(request, 'accounts/developer_dashboard.html')