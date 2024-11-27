# supply_chain/forms.py
from django import forms
from .models import Crop
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Crop
from django.contrib.auth.models import AbstractUser
from django.db import models

class CropForm(forms.ModelForm):
    price = forms.FloatField(label="Public Price", required=True)
    specific_user_price = forms.FloatField(label="Specific User Price", required=False)

    class Meta:
        model = Crop
        fields = ['name', 'quantity', 'visibility', 'price', 'specific_user_price']


class CropPriceUpdateForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['price']  # Only allow editing of the price field

class CustomUserCreationForm(UserCreationForm): 
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')



        


    
