from django import forms
from django.forms import ModelForm, DateInput, EmailInput
from .models import Pessoa


class DateInput(DateInput):
    input_type = 'date'

class EmailInput(EmailInput):
    input_type = 'email'

class ServidorForm(ModelForm):
    email = forms.CharField(required=True)
    emailInstitucional = forms.CharField(label="Email Institucional",required=False)
    class Meta:
        model = Pessoa
        fields = ["nome",
                  "dataNascimento",
                  "telefone",
                  "user",
                  "celular",
                  "email",
                  "endereco",
                  "cep",
                  "cpf",
                  "rg",
                  "cidade",
                  "campus",
                  "emailInstitucional",
                  "status"]
        widgets = {'dataNascimento':DateInput(), 'emailInstitucional':EmailInput(), 'email':EmailInput()}