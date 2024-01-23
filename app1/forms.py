from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Region,Account

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = ''
    class Meta:
        model = User
        fields = ('username','email', 'password1','password2')

class RegionForm(forms.ModelChoiceField):
    class Meta:
        model=Region
        fields=('Name')

class Edit_Account(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['profile_picture', 'homepage_picture'] 

    