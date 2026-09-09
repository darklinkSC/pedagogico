from django.db import models
from datetime import datetime
from geral.models import GrupoTrabalho
from geral.models import Pessoa

#STATUS
STATUS = (("A", "Ativo"),("I", "Inativo"))

###
# TABELAS ER GED CONTROLE DE REGISTRO DE ATAS
###
class Local(models.Model):
    nome = models.CharField(u"Nome", max_length=200, null=False, blank=False)
    class Meta:
        db_table = "local"
        ordering = ['nome']
    def __str__(self):
        return self.nome


class Registro(models.Model):
    titulo = models.CharField(u"Titulo", max_length=200, null=False, blank=False)
    dataReuniao = models.DateField(u"Data Reunião", null=False, blank=False)
    duracao = models.TimeField(u"Duração", null=False, blank=False)
    descricao = models.CharField(u"Descrição", max_length=200, null=True, blank=False)
    versao = models.IntegerField(u"Versão", null=True, blank=False)
    dataCriacao = models.DateTimeField(u"Data Criação", null=True,blank=True, default=datetime.now)
    pauta = models.CharField(u"Pauta", max_length=200, null=True, blank=False)
    registroImportacao = models.IntegerField(u"Registro Importação", null=True, blank=False)
    status = models.CharField(u"Descrição", max_length=1, null=True, blank=False, choices=STATUS)
    grupoTrabalho = models.ForeignKey(GrupoTrabalho, on_delete=models.CASCADE,null=True,verbose_name='GrupoTrabalho')
    usuarioCriacao = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=True,verbose_name='UsuarioCriacao')
    local = models.ForeignKey(Local, on_delete=models.CASCADE,null=True,verbose_name='Local')
    class Meta:
        db_table = "ged_registro"
        ordering = ['titulo']
    def __str__(self):
        return self.titulo



class AnexosRegistro(models.Model):
    anexo = models.FileField(u"Anexo")
    dataAnexo = models.DateField(u"Data Reunião", null=False, blank=False,default=datetime.now)
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    class Meta:
        db_table = "ged_anexo"     


class Marcador(models.Model):
    descricao = models.CharField(u"Descrição", max_length=200, null=False, blank=False)
    grupoTrabalho = models.ForeignKey(GrupoTrabalho, on_delete=models.CASCADE,null=True,verbose_name='GrupoTrabalho')
    class Meta:
        db_table = "ged_marcadores"


class MarcadoresRegistro(models.Model):
    marcador = models.ForeignKey(Marcador, on_delete=models.CASCADE,null=True,verbose_name='Marcador')
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    class Meta:
        db_table = "ged_marcador_registro"


class Discussao(models.Model):
    descricao = models.CharField(u"Descrição", max_length=200, null=False, blank=False)
    dataCriacao = models.DateTimeField(u"Data Reunião", null=False, blank=False,default=datetime.now)
    usuarioCriacao = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=True,verbose_name='UsuarioCriacao')
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    class Meta:
        db_table = "ged_discussao"


class ParticipantesExterno(models.Model):
    nome = models.CharField(u"Nome", max_length=200, null=False, blank=False)
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    class Meta:
        db_table = "ged_participante_externo"


class ParticipantesReuniao(models.Model):
    participante = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=True,verbose_name='Participante')
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    status = models.CharField(u"Descrição", max_length=1, null=True, blank=False, choices=STATUS)
    class Meta:
        db_table = "ged_participante_reuniao"


class RetificacaoRegistro(models.Model):
    descricao = models.CharField(u"Descrição", max_length=200, null=False, blank=False)
    dataCriacao = models.DateTimeField(u"Data Reunião", null=False, blank=False,default=datetime.now)
    usuarioCriacao = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=True,verbose_name='UsuarioCriacao')
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE,null=True,verbose_name='Registro')
    versao = models.IntegerField(u"Versão", null=True, blank=False)
    class Meta:
        db_table = "ged_retificacao"