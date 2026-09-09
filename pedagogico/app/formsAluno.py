from django import forms
from django.forms import ModelForm, DateInput, EmailInput
from geral.models import Pessoa
from pedagogico.models import Matricula


class DateInput(DateInput):
    input_type = 'date'

class EmailInput(EmailInput):
    input_type = 'email'

class AlunoForm(ModelForm):
    matricula = forms.CharField(label="Matricula",max_length=20,required=True)
    class Meta:
        model = Pessoa
        fields = ["nome",
                  "telefone",
                  "celular",
                  "email",
                  "matricula",
                  "foto"]
    
    def clean_matricula(self):
        matricula = self.cleaned_data["matricula"]
    
        try:
            Pessoa.objects.get(matricula = matricula)
            raise forms.ValidationError("Matrícula já existe.")
        except Pessoa.DoesNotExist:
            pass 

        return matricula


class AlunoUpdateForm(ModelForm):
    matricula = forms.CharField(label="Matricula",max_length=20,required=True)
    class Meta:
        model = Pessoa
        fields = ["nome",
                  "telefone",
                  "celular",
                  "email",
                  "matricula",
                  "foto"]
    

class MatriculaForm(ModelForm):
    class Meta:
        model = Matricula
        fields = ["unidadeCurricular"]