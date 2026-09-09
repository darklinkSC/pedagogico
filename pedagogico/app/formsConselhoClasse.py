from django import forms
from django.forms import ModelForm, DateInput
from pedagogico.models import ConselhoClasse, PeriodoConselho
from ckeditor.widgets import CKEditorWidget

class DateInputCustom(DateInput):
    input_type = 'date'

class PeriodoConselhoForm(ModelForm):
    class Meta:
        model = PeriodoConselho
        fields = ['nome', 'ordem', 'ativo']


class ConselhoClasseNovoForm(ModelForm):
    class Meta:
        model = ConselhoClasse
        fields = ['turma', 'ano', 'periodoConselho', 'dataConselho']
        widgets = {
            'dataConselho': DateInputCustom(),
        }

    def __init__(self, *args, **kwargs):
        super(ConselhoClasseNovoForm, self).__init__(*args, **kwargs)
        # Filtra apenas períodos ativos para novas criações
        self.fields['periodoConselho'].queryset = PeriodoConselho.objects.filter(ativo='A')