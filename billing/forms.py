from django import forms
from .models import Patient
from django import forms
from .models import Claim

class PatientForm(forms.ModelForm):
    class Meta:
        model  = Patient
        fields = [
            'full_name', 'guardian_name', 'gender',
            'date_of_birth', 'phone', 'address', 'blood_group'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address':       forms.Textarea(attrs={'rows': 2}),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = '__all__'