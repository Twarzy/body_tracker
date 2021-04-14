from django import forms
from .models import Measurement


class MeasurementForm(forms.ModelForm):

    class Meta:
        model = Measurement
        fields = ['date', 'weight', 'chest', 'waist', 'biceps']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
         }