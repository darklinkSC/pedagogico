from django import forms
from django.forms import ModelForm
from pedagogico.models import Turma 


class TurmaForm(ModelForm):
    class Meta:
        model = Turma
        fields = ["nome",
                  "curso"]




    