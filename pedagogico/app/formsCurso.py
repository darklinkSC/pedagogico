from django import forms
from django.forms import ModelForm, DateInput, EmailInput
from pedagogico.models import Curso


class CursoForm(ModelForm):
    class Meta:
        model = Curso
        fields = ["nome",
                  "sigla",
                  "campus"]
        




    