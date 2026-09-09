from django import forms
from django.forms import ModelForm, DateInput, Textarea
from django.forms.widgets import TimeInput
from ged.models import Registro


class DateInput(DateInput):
    input_type = 'date'


class TimeInput(TimeInput):
    input_type = 'time'


class TextAreaInput(Textarea):
    input_type = 'textarea'

class RegistroForm(ModelForm):
    class Meta:
        model = Registro
        fields = ["titulo",
                  "dataReuniao",
                  "duracao",
                  "descricao",
                  "pauta",
                  "local"]
        widgets = {'dataReuniao':DateInput(),'duracao':TimeInput(),'descricao':TextAreaInput(),'pauta':TextAreaInput()}