from django import forms
from django.forms import ModelForm
from pedagogico.models import TipoOcorrencia


class TipoOcorrenciaForm(ModelForm):
    class Meta:
        model = TipoOcorrencia
        fields = ["nome",
                  "statusPublico",
                  "parecer"]
