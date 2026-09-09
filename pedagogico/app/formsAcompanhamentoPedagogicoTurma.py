from django import forms
from django.forms import ModelForm, DateInput, EmailInput, Textarea
from pedagogico.models import AcompanhamentoPedagogicoTurma, TipoOcorrencia
from pedagogico.app import viewAcompanhamentoPedagogicoTurma

class DateInput(DateInput):
    input_type = 'date'


class TextAreaInput(Textarea):
    input_type = 'textarea'
    label = "Atestado"


class AcompanhamentoPedagogicoTurmaForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super (AcompanhamentoPedagogicoTurmaForm,self ).__init__(*args,**kwargs)
        self.fields['tipoOcorrencia'].queryset = TipoOcorrencia.objects.filter(statusPublico='S')
        
    class Meta:
        model = AcompanhamentoPedagogicoTurma
        descricao = forms.CharField(label="Ocorrência",widget=forms.Textarea,required=True)

        fields = ["tipoOcorrencia","descricao","dataAtendimento","anexo"]
        widgets = {'descricao':TextAreaInput(),  'dataAtendimento':DateInput()}