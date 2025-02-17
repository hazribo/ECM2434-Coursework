from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from .leaderboard_src import generate_leaderboard_image

def home(request):
    return render(request, 'WebApp/home.html')

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
    







def is_developer(user):
    return user.user_type == 'developer'

@user_passes_test(is_developer)
def developer_dashboard(request):
    return render(request, 'accounts/developer_dashboard.html')