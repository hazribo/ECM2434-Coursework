
import django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.core.management import call_command
# json for status responses:
import json
# Import necessary local files:
from .models import *
from .forms import *
from .leaderboard_src import *
from .search_src import search_for_username
from .friendsystem_src import *
from .missions_src import get_user_missions, tick_repeating_missions
from .shop_src import get_shop_items, user_buy, get_inventory_items, shop_init
# geopy for location views:
from geopy.distance import geodesic
from time import time as getNow
# image for photo saving:
from PIL import Image
import base64
from io import BytesIO
from django.core.files.base import ContentFile
from os import remove

# ------------------------------------------------------
# Helper Functions for Permissions:
# ------------------------------------------------------

def is_game_keeper_or_developer(user):
    return user.user_type in ['game_keeper', 'developer']
def is_developer(user):
    return user.user_type == 'developer'

# ------------------------------------------------------
# Basic render request functions for home/about:
# ------------------------------------------------------

def home(request):
    return render(request, 'WebApp/home.html')

def about(request):
    return render(request, 'WebApp/about.html')

def policy(request):
    return render(request, 'WebApp/policy.html')

def alert(request, message):
    return render(request, "WebApp/alert.html", {"message" : message})

# ------------------------------------------------------
# User Authentication:
# ------------------------------------------------------

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
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

# ------------------------------------------------------
# Friends System:
# ------------------------------------------------------

def unchanged(request, *args, **kwargs):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# Handles user accepting friend request:
def accept_req(request, accepter_id, accepted_id, **kwargs):
    print(f"Accept Request: {accepter_id} is accepting {accepted_id}")
    record_friend_request_response(accepter_id, accepted_id, True)
    return unchanged(request)

# Handles user rejecting friend request:
def reject_req(request, rejecter_id, rejected_id, **kwargs):
    print(f"Reject Request: {rejecter_id} is rejecting {rejected_id}")
    record_friend_request_response(rejecter_id, rejected_id, False)
    return unchanged(request)

# Handles user sending friend request (requires login):
@login_required
def addfriend(request, idVal = None):
    send_friend_request(request.user.id, idVal)
    return unchanged(request);

# ------------------------------------------------------
# Missions Code:
# ------------------------------------------------------

# Gets current time/date:
def getTimeNow(): 
    return getNow()

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

# Mission management:
@login_required
def missions(request):
    username=request.user.username
    ACCEPTABLE_DISTANCE = 100 # Acceptable distance from mission location - feel free to edit to debug.
    # Generate default missions if none exist:
    if not Mission.objects.exists():
        call_command('generate_missions')
        
    # Get data for provided username to display correct profile:
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(Profile, user=user)
    team = user_profile.team
    tick_repeating_missions(user_profile);

    # Handle POST request (on mission completion):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mission_id = data.get("mission_id")
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            mission = get_object_or_404(Mission, id=mission_id)
            user_mission, created = UserMission.objects.get_or_create(user=request.user, mission=mission)

            # Checks if mission is location-based:
            if mission.requires_location:
                # Error handling - no location data:
                if latitude is None or longitude is None:
                    return JsonResponse({"status": "error", "message": "Location data is missing."})
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                except ValueError:
                    return JsonResponse({"status": "error", "message": "Invalid location coordinates."})
                
                # Calculate distance from target location:
                mission_location = (mission.latitude, mission.longitude)
                user_location = (latitude, longitude)
                distance = geodesic(mission_location, user_location).meters
                print(f"Mission Location: {mission_location}, User Location: {user_location}, Distance: {distance}")

                if distance <= ACCEPTABLE_DISTANCE:
                    # As long as in range, mission completed...
                    user_mission.completed = True
                    user_mission.date_completed = getTimeNow();
                    user_mission.save()
                    # ...and points awarded:
                    profile = request.user.profile
                    profile.score += mission.points
                    if team:
                        team.score += mission.points
                    profile.save()
                # Return completion status for location_verified:
                return JsonResponse({"status": "success", "requires_location": True, "location_verified": user_mission.completed, "distance": distance})

            # Handle self-check missions (such as recycling):
            else:
                user_mission.completed = not user_mission.completed
                if (user_mission.completed):
                    user_mission.date_completed = getTimeNow();
                user_mission.save()

                # Award points to user on self-submission:
                profile = request.user.profile
                if user_mission.completed:
                    profile.score += mission.points
                    profile.credits += 1
                else:
                    profile.score -= mission.points
                    profile.credits -= 1
                
                profile.save()
                # Return state of user_mission.completed:
                return JsonResponse({"status": "success", "requires_location": False, "completed": user_mission.completed})
        # Send error if JSON format incorrect:
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."})

    # Ensure all missions are tracked in UserMission:
    all_missions = Mission.objects.all()
    user_missions = UserMission.objects.filter(user=request.user)

    # Get/Create missions in user's missions list:
    for mission in all_missions:
        UserMission.objects.get_or_create(user=request.user, mission=mission)

    # Render missions.html, along with all user's mission data:
    return render(request, 'WebApp/missions.html', {'missions': all_missions, 'user_missions': user_missions})

@login_required
def save_photo(request):
    if request.method == "POST":
        try:
            # Parse JSON request body:
            data = json.loads(request.body)
            image_data = data.get('image_data')  
            mission_id = data.get('mission_id')
            # Error; in case of no image data present:
            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'No image data received'})

            # Extract the base64 string:
            format, imgstr = image_data.split(';base64,')
            imgdata = base64.b64decode(imgstr)
            # Convert image to a file-like object:
            image_file = ContentFile(imgdata, name=f"{request.user.username}_mission_{mission_id}.jpg")
            # Open image with PIL:
            image = Image.open(BytesIO(imgdata))
            image.verify()  # Verifies no corrupted image.

            # Get the user's profile:
            profile = Profile.objects.get(user=request.user)

            # Get the mission:
            try:
                mission = Mission.objects.get(id=mission_id)
            # Error; no mission exists with given mission_id:
            except Mission.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid mission ID'})

            # Save photo to MissionPhoto model:
            MissionPhoto.objects.create(profile=profile, mission=mission, image=image_file)
            return JsonResponse({'status': 'success', 'message': 'Photo saved successfully'})

        # Catch-all for all other possible errors:
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# ------------------------------------------------------
# GDPR page code:
# ------------------------------------------------------
def _get_user_data(request):
    user = request.user
    user_profile = get_object_or_404(Profile, user=user)

    return user, user_profile

@login_required
def datareq(request, username):
    _GDPR_RETURN_FILE_NAME = "userdata"
    _, profile = _get_user_data(request)
    
    userData = profile.get_GDPR_data()

    # proper way, force file download
    response = HttpResponse(userData, content_type="application/text charset=utf-8");
    response["Content-Disposition"] = f"attatchment; filename={_GDPR_RETURN_FILE_NAME}.txt"

    return response

# ------------------------------------------------------
# Shop page code:
# ------------------------------------------------------
@login_required
def buy_shop(request, itemname):
    
    _, profile = _get_user_data(request)

    if user_buy(profile, itemname):
        # enough 
        return unchanged(request)
    else:
        # not enough credits
        return alert(request, "not enough credits");
    

@login_required
def shop(request):

    shop_init()

    _, profile = _get_user_data(request)

    context = {
        "shop_items" : get_shop_items(),
        "player_credits" :  profile.credits,
        "inventory" : get_inventory_items(profile)
    }
    return render(request, "WebApp/shop.html", context)

# ------------------------------------------------------
# Game page code:
# ------------------------------------------------------

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
        'user_missions': user_missions,
        "player_credits" : user_profile.credits
    }
    return render(request, 'WebApp/game.html', context)

# ------------------------------------------------------
# Search results view:
# ------------------------------------------------------

def search(request):
    _NoSearchString = "NONE"
    username = request.GET.get('username', _NoSearchString)
    matches = search_for_username(username)
    context = { 
        "search_name" : username,
        "results" : matches,
        "anyfound" : (len(matches) > 0)
    }
    return render(request, "WebApp/search.html", context)

# ------------------------------------------------------
# Leaderboard view:
# ------------------------------------------------------

def leaderboard(request):
    # Get all leaderboard visual data:
    leaderboard_type = request.GET.get('type', 'users')
    limit = request.GET.get('range', '10')
    range_map = {"10": 10, "50": 50, "100": 100, "all": None}
    limit = range_map.get(limit, 10)
    # Retrieve data from profile/team scores db:
    data = get_leaderboard_data(leaderboard_type, limit)
    # Return data to leaderboard.html:
    return render(request, 'WebApp/leaderboard.html', data)

# ------------------------------------------------------
# User profiles:
# ------------------------------------------------------

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

    # Get all mission-related photos attached to the requested profile:
    mission_photos = MissionPhoto.objects.filter(profile=user_profile)

    # Get the friend / friend request list for this profile:
    friend_request_list = get_friend_request_list(user_profile);
    friend_list = get_friend_list(user_profile)
    # Debug - print these:
    print(friend_request_list)
    print(friend_list)

    base = None

    pathTemp = finders.find("gbc3.png")
    staticPath = pathTemp[:len(pathTemp) - 8]

    score = user_profile.score





    # if score > 50:
    #     path = "gbc3.png"
    #     bt1 = "Bean Happiness: 6/6"
    #     bt2 = "Your bean is at full happiness!"

    if score > 40:
        path = "BPsix.png"
        # bt1 = "Bean Happiness: 5/6"
        bt2 = "Get 10 more points for max happiness!"

    elif score > 30:
        path = "BPfive.png"
        # bt1 = "Bean Happiness: 4/6"
        bt2 = "Get 20 more points for max happiness!"

    elif score > 20:
        path = "BPfour.png"
        # bt1 = "Bean Happiness: 3/6"
        bt2 = "Get 30 more points for max happiness!"

    elif score > 10:
        path = "BPthree.png"
        # bt1 = "Bean Happiness: 2/6"
        bt2 = "Get 40 more points for max happiness!"

    elif score > 5:
        path = "BPtwo.png"
        # bt1 = "Bean Happiness: 1/6"
        bt2 = "Get 45 more points for max happiness!"

    else:
        path = "BPone.png"
        # bt1 = "Bean Happiness: 0/6"
        bt2 = "Get 50 more points for max happiness!"
    # if (user_profile.score )
    # print(user_profile.score, path)

    base = Image.open(staticPath + path)

    user_profile.render_bean_with_accessories(base) \
        .save(buffer := BytesIO(), "png")
    bean_str = base64.b64encode(buffer.getvalue())  \
        .decode('utf-8')

    context = {
        'profile': user_profile,
        'req_list' : friend_request_list,
        'friend_list' : friend_list,
        'mission_photos': mission_photos,
        "bean_str" : bean_str,
        # "bean_text_1" : bt1
        "bean_text_2" : bt2
    };

    return render(request, 'WebApp/profile.html', context)

# Profile update form request:
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

# Redirects user to their profile or login page if not logged in:
def redirect_to_profile(request):
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    else:
        # redirect to login if not logged in - no profile to show:
        return redirect('login')
    
# ------------------------------------------------------
# Teams Code:
# ------------------------------------------------------

@login_required
def manage_teams(request):
    # Initialise user, team, user_team:
    user = request.user
    teams = Team.objects.all()
    user_team = Team.objects.filter(members=user).first()

    if request.method == "POST":
        # Get action type, team_id:
        action = request.POST.get("action")
        team_id = request.POST.get("team_id")
        
        # Team creation handling:
        if action == "create":
            name = request.POST.get("name")
            if name:
                # Create team, add user to team:
                team = Team.objects.create(name=name, team_owner=user)
                team.add_member(user)
                return redirect("teams")
        # Team joining handling:
        elif action == "join" and team_id:
            team = get_object_or_404(Team, id=team_id)
            team.add_member(user)
            return redirect("teams")
        # Team leaving handling:
        elif action == "leave" and user_team:
            user_team.remove_member(user)
            user_team = None
            return redirect("teams")

    return render(request, "WebApp/teams.html", {"teams": teams, "user_team": user_team})
