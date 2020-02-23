from django import forms

class AuthValidationForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()