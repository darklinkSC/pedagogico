from django import forms
from django.forms import ModelForm, DateInput, EmailInput
from pedagogico.models import UnidadeCurricular 


class UnidadeCurricularForm(ModelForm):
    class Meta:
        model = UnidadeCurricular
        fields = ["nome",
                  "sigla",
                  "curso"]




    