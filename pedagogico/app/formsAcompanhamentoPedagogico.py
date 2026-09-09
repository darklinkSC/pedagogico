from datetime import date
from django import forms
from django.forms import ModelForm, DateInput, EmailInput, Textarea, ChoiceField
from pedagogico.models import AcompanhamentoPedagogicoAluno, TipoOcorrencia, ImportConselhoClasse
from pedagogico.app import viewAcompanhamentoPedagogico
from ckeditor.widgets import CKEditorWidget

ANO = (("2022-02-02","2022-02-02"))

class DateInput(DateInput):
    input_type = 'date'


class TextAreaInput(Textarea):
    input_type = 'textarea'
    label = "Atestado"


class AcompanhamentoPedagogicoAlunoForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super (AcompanhamentoPedagogicoAlunoForm,self ).__init__(*args,**kwargs)
        self.fields['tipoOcorrencia'].queryset = TipoOcorrencia.objects.filter(statusPublico='S')
        
    class Meta:
        model = AcompanhamentoPedagogicoAluno
        #descricao = forms.CharField(label="Ocorrência",widget=forms.Textarea,required=True)
        descricao = forms.CharField(label="Ocorrência",widget=CKEditorWidget(),required=True) 

        fields = ["tipoOcorrencia","descricao","dataAtendimento","dataConselho","anexo"]
        widgets = {'descricao':TextAreaInput(),  'dataAtendimento':DateInput(),'dataConselho':DateInput()}
        #widgets = {'dataAtendimento':DateInput(),'dataConselho':DateInput()}


class AcompanhamentoPedagogicoAlunoParecerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AcompanhamentoPedagogicoAlunoParecerForm, self).__init__(*args, **kwargs)
        self.fields['tipoOcorrencia'].queryset = TipoOcorrencia.objects.filter(statusPublico='S',parecer='S')

    class Meta:
        model = AcompanhamentoPedagogicoAluno
        #descricao = forms.CharField(label="Ocorrência", widget=forms.Textarea, required=True)
        descricao = forms.CharField(label="Ocorrência",widget=CKEditorWidget(),required=True) 

        fields = ["tipoOcorrencia", "descricao", "dataAtendimento"]
        widgets = {'descricao': TextAreaInput(), 'dataAtendimento': DateInput()}


class AcompanhamentoPedagogicoAlunoRestritoForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super (AcompanhamentoPedagogicoAlunoRestritoForm,self ).__init__(*args,**kwargs)
        self.fields['tipoOcorrencia'].queryset = TipoOcorrencia.objects.filter(statusPublico='N')
        
    class Meta:
        model = AcompanhamentoPedagogicoAluno
        #descricao = forms.CharField(label="Ocorrência",widget=forms.Textarea,required=True)
        descricao = forms.CharField(label="Ocorrência",widget=CKEditorWidget(),required=True) 

        fields = ["tipoOcorrencia","descricao","dataAtendimento","anexo"]
        widgets = {'descricao':TextAreaInput(),  'dataAtendimento':DateInput()}


class AcompanhamentoPedagogicoAlunoAtestadoForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super (AcompanhamentoPedagogicoAlunoAtestadoForm,self ).__init__(*args,**kwargs)
        self.fields['tipoOcorrencia'].queryset = TipoOcorrencia.objects.filter(statusPublico='S')

    class Meta:
        model = AcompanhamentoPedagogicoAluno
        #descricao = forms.CharField(label="Ocorrência",widget=forms.Textarea,required=True)
        descricao = forms.CharField(label="Ocorrência",widget=CKEditorWidget(),required=True) 

        fields = ["tipoOcorrencia","descricao", "dataAtendimento", "dataAtestadoInicio","dataAtestadoFim","anexo"]
        widgets = {'dataAtendimento':DateInput(), 'dataAtestadoInicio':DateInput(), 'dataAtestadoFim':DateInput(), 'descricao':TextAreaInput()}
        