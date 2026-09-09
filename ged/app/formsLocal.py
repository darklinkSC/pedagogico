from django import forms
from django.forms import ModelForm
from ged.models import Local


class LocalForm(ModelForm):
    class Meta:
        model = Local
        fields = ["nome"]
        

