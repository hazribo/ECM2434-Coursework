from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customised labels:
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email Address'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['user_type'].label = 'Select user type'

        # Customised help text:
        self.fields['username'].help_text = ''
        self.fields['email'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['user_type'].help_text = 'DEV SETTING - REMOVE FROM OFFICIAL RELEASE.'

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customised labels:
        self.fields['bio'].label = 'Bio'
        self.fields['profile_picture'].label = 'Profile Picture'

        # Customised help text:
        self.fields['bio'].help_text = 'Write a short bio about yourself.'
        self.fields['profile_picture'].help_text = 'Upload a profile picture.'