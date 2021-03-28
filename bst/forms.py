from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordChangeView
from .models import Measurement


class MeasurementForm(forms.ModelForm):

    class Meta:
        model = Measurement
        fields = ['date', 'weight', 'chest', 'waist', 'biceps']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
         }