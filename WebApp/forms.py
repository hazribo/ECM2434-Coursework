from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.USER_TYPES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customised labels
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email Address'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['user_type'].label = 'Select user type'

        # Customised help text
        self.fields['username'].help_text = ''
        self.fields['email'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['user_type'].help_text = 'DEV SETTING - REMOVE FROM OFFICIAL RELEASE.'