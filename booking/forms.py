from django import forms

class AuthValidationForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()

class LocationValidationForm(forms.Form):
    id = forms.IntegerField()
    name = forms.CharField()
    capacity = forms.IntegerField()

class LocationAddValidationForm(forms.Form):
    name = forms.CharField()
    capacity = forms.IntegerField()

class RtValidationForm(forms.Form):
    id = forms.IntegerField()
    name = forms.CharField()

class RtAddValidationForm(forms.Form):
    name = forms.CharField()
