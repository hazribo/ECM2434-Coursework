from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from .forms import UserRegistrationForm
from .leaderboard_src import generate_leaderboard_image

def home(request):
    return render(request, 'WebApp/home.html')

def about(request):
    return render(request, 'WebApp/about.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create new profile:
            Profile.objects.create(user=user)
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
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'WebApp/profile.html', {'profile': user_profile})

def is_developer(user):
    return user.user_type == 'developer'

@user_passes_test(is_developer)
def developer_dashboard(request):
    return render(request, 'accounts/developer_dashboard.html')