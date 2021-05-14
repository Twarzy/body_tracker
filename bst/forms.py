from django import forms
from .models import Measurement


class MeasurementForm(forms.ModelForm):

    class Meta:
        model = Measurement
        fields = ['date', 'weight', 'chest', 'waist', 'biceps']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
         }

class BmiForm(forms.Form):

    age = forms.IntegerField()
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=[('1', 'Male'), ('2', 'Female')])
    weight = forms.IntegerField(label='Weight in "kg"')
    height = forms.IntegerField(label='Height in "cm"')
