from django import forms
from django.forms import ModelForm, DateInput
from pedagogico.models import SessaoParecerTurma, PeriodoConselho

class DateInputCustom(DateInput):
    input_type = 'date'

class SessaoParecerTurmaForm(ModelForm):
    class Meta:
        model = SessaoParecerTurma
        fields = ['turma', 'ano', 'periodoConselho', 'dataRegistro']
        widgets = {
            'dataRegistro': DateInputCustom(),
        }

    def __init__(self, *args, **kwargs):
        super(SessaoParecerTurmaForm, self).__init__(*args, **kwargs)
        self.fields['periodoConselho'].queryset = PeriodoConselho.objects.filter(ativo='A')