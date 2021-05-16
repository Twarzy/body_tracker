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

    age = forms.IntegerField(min_value=2, max_value=150)
    gender = forms.TypedChoiceField(widget=forms.RadioSelect,
                                    choices=[('1', 'Male'), ('2', 'Female')])
    weight = forms.IntegerField(label='Weight in "kg"', min_value=1)
    height = forms.IntegerField(label='Height in "cm"', min_value=1)
