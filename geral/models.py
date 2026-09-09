from django.db import models
from django.forms import ModelForm
from system.models import Cidade
from system.models import Campus
from django.contrib.auth.models import User

## VAR GLOBAIS 
STATUS = (("A", "Ativo"),("I", "Inativo"))
TIPO_PESSOA = (("S", "Servidor"),("A", "Aluno"),("O","Outros"))
SIM_NAO = (("S","Sim"),("N","Não"))

TIPO_PESSOA_SERVIDOR = "S"
TIPO_PESSOA_ALUNO = "A"
STATUS_ATIVO = "A"
STATUS_INATIVO = "I"

###
# TABELAS ER SISTEMA INTEGRADO
###
### Pessoa - Tabela com dados dos servidores
class Pessoa(models.Model):  
    nome = models.CharField(u"Nome", max_length=200, null=False,blank=False)
    dataNascimento = models.DateField(u"Data de Nascimento", null=True,blank=True)
    telefone = models.CharField(max_length=20,null=True,blank=True)
    celular = models.CharField(max_length=20,null=True,blank=True)
    email = models.EmailField(max_length=200, blank=False,null=True)
    endereco = models.CharField(u"Endereço",max_length=1000,null=True,blank=True)
    cep = models.CharField(u"CEP",max_length=8,null=True,blank=True)
    cpf = models.CharField(u"CPF",max_length=20,null=True,blank=True)
    rg = models.CharField(u"RG",max_length=50,null=True,blank=True)
    emailInstitucional = models.EmailField(u"Email Institucional",max_length=200,null=True,blank=True)
    status = models.CharField(max_length=1, choices=STATUS,null=True,blank=True)
    tipoPessoa = models.CharField(max_length=1, choices=TIPO_PESSOA,null=True,blank=True)
    matricula = models.CharField(max_length=100,null=True,blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE,null=True,blank=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    foto = models.FileField(u"Foto", null=True,blank=True, upload_to='documents/foto/%Y/%m/%d/')

    class Meta:
        db_table = "pessoa"
        ordering = ['nome']
    def __str__(self):
        return self.nome

#### GRUPO TRABALHO ####
class GrupoTrabalho(models.Model):
    nome = models.CharField(u"Nome", null=False, blank=False, max_length=200)
    descricao = models.CharField(u"Descrição", blank=True, max_length=1024)
    portaria = models.CharField(u"Portaria", blank=True, max_length=20)
    dataCriacao = models.DateField(u"Data de Criação", auto_now_add=True)
    dataExpiracao = models.DateField(u"Data Expiração")
    status = models.CharField(u"Status", max_length=1, choices=STATUS)
    publico = models.CharField(u"Grupo Publico", max_length=1, choices=SIM_NAO)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE,null=True,blank=True)
    
    class Meta:
        db_table = "grupo_trabalho"
        ordering = ['nome']
    def __str__(self):
        return self.nome

#### PARTICIPANTES GRUPO TRABALHO ####
class ParticipantesGrupoTrabalho(models.Model):
    lider = models.CharField(u"Lider do Grupo", choices=SIM_NAO, max_length=1)
    grupoTrabalho = models.ForeignKey(GrupoTrabalho, on_delete=models.CASCADE,null=False)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False)
    
    class Meta:
        db_table = "participantes_grupo_trabalho"
        unique_together = (("grupoTrabalho", "pessoa"))
        ordering = ['pessoa']
    def __str__(self):
        return self.nome,self.grupoTrabalho.nome,self.pessoa.nome
