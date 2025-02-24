from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Profile
from .forms import UserRegistrationForm, ProfileUpdateForm
from .leaderboard_src import generate_leaderboard_image
from .search_src import search_for_username

def home(request):
    return render(request, 'WebApp/home.html')

def about(request):
    return render(request, 'WebApp/about.html')

@login_required
def game(request):
    return render(request, 'WebApp/game.html')

_NoSearchString = "NONE"
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
    return render(request, 'WebApp/profile.html', {'profile': user_profile})

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

def is_developer(user):
    return user.user_type == 'developer'

@user_passes_test(is_developer)
def developer_dashboard(request):
    return render(request, 'accounts/developer_dashboard.html')