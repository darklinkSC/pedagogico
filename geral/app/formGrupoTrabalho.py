from django import forms
from django.forms import ModelForm, DateInput, EmailInput
from geral.models import GrupoTrabalho, ParticipantesGrupoTrabalho, Pessoa


class DateInput(DateInput):
    input_type = 'date'
    required = False


class GrupoTrabalhoForm(ModelForm):
    descricao = forms.CharField(label="Descrição",widget=forms.Textarea,required=False)
    class Meta:
        model = GrupoTrabalho
        fields = ["nome",
                  "descricao",
                  "portaria",
                  "dataExpiracao",
                  "status",
                  "publico",
                  "campus"]
        widgets = {'dataExpiracao':DateInput()}


class ParticipantesGrupoTrabalhoForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super (ParticipantesGrupoTrabalhoForm,self ).__init__(*args,**kwargs)
        self.fields['pessoa'].queryset = Pessoa.objects.filter(tipoPessoa='S')
    class Meta:
        model = ParticipantesGrupoTrabalho
        fields = ["pessoa","lider"]
    def setGrupoTrabalho(gp):
        setattr(model, 'grupoTrabalho' , gp)
        return self