from django.db import models 
from datetime import datetime
from system.models import Campus
from geral.models import Pessoa
from ckeditor.fields import RichTextField

SIM_NAO = (("S","Sim"),("N","Não"))
ATIVO_INATIVO = (("A","Ativo"),("I","Inativo"))

###
# TABELAS ER SISTEMA INTEGRADO
###
### Curso tabela dos cursos 
class Curso(models.Model):
    nome = models.CharField(u"Nome", max_length=200, null=False, blank=False)
    sigla = models.CharField(u"Sigla", max_length=10, null=False, blank=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE,null=False,blank=False)
    class Meta:
        db_table = "curso"
        ordering = ['nome']
    def __str__(self):
        return self.nome


class Turma(models.Model):
    nome = models.CharField(u"Nome", max_length=200, null=False, blank=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,null=False,blank=False)
    periodo = models.IntegerField(u"Período / Fase", null=True, blank=True)
    class Meta:
        db_table = "turma"
        ordering = ['nome']
    def __str__(self):
        return self.nome
 

class UnidadeCurricular(models.Model): 
    nome = models.CharField(u"Nome", max_length=200, null=False, blank=False)
    sigla = models.CharField(u"Sigla", max_length=10, null=False, blank=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,null=False,blank=False)
    periodo = models.IntegerField(u"Período",null=True,blank=True)
    class Meta:
        db_table = "unidadeCurricular"
        ordering = ['nome']
    def __str__(self):
        return self.nome


class Matricula(models.Model):  
    aluno = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,blank=False,related_name='aluno_matricula')
    unidadeCurricular = models.ForeignKey(UnidadeCurricular, on_delete=models.CASCADE, null=False,blank=False)
    notaFinal = models.CharField(u"Nota Final", max_length=10, null=True, blank=True)
    notaParcial = models.CharField(u"Nota Parcial", max_length=10, null=True, blank=True)
    percentualFalta = models.CharField(u"Percentual Falta", max_length=10, null=True, blank=True)
    periodo = models.IntegerField(u"Período", null= True, blank=True)
    status = models.CharField(u"Situação",max_length=1, null=True,blank=True,choices=ATIVO_INATIVO)
    class Meta:
        db_table = "matricula"
        unique_together = (("aluno", "unidadeCurricular"))
    def __str__(self):
        return self.matricula

####
#
####

class ImportConselhoClasse(models.Model):
    matricula = models.CharField(max_length=50)
    dataImportacao = models.DateField(u"Data Importação", null=True,blank=True, default=datetime.now)
    unidadeCurricular = models.CharField(max_length=200)
    notas = models.CharField(max_length=50)
    faltas = models.CharField(max_length=50,null=True,default=0)
    class Meta:
        db_table = "import_conselho_classe"
    def __str__(self):
        return self.dataImportacao.__str__()


#####
# CLASSE PARA INFORMACOES EXTRAS DOS ALUNOS
#####
class InformacoesAlunos(models.Model):
    aluno = models.OneToOneField(Pessoa, primary_key=True, on_delete=models.CASCADE,null=False,blank=False)
    paevs = models.CharField(u"Recebe PAEVs", max_length=1, null=False, blank=False, choices=SIM_NAO)
    deficiencia = models.CharField(u"Possui Deficiência",max_length=1,choices=SIM_NAO,default='N')
    class Meta:
        db_table = "informacoesAlunos"
    def __str__(self):
        return self.aluno


class GrupoUnidadeCurricilarCurso(models.Model):
    unidadeCurricular = models.ForeignKey(UnidadeCurricular, on_delete=models.CASCADE,null=False,blank=False)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,null=False,blank=False)
    class Meta:
        db_table = "grupo_uc_curso"
        unique_together = (("curso", "unidadeCurricular"))


class TipoOcorrencia(models.Model):
    nome = models.CharField(u"Nome", max_length=1024, null=True, blank=False)
    statusPublico = models.CharField(u"Público", max_length=1, choices= SIM_NAO,null=True, blank=False)
    parecer = models.CharField(u"Parecer", max_length=1, choices=SIM_NAO, null=True, blank=False)
    class Meta:
        db_table = "tipo_ocorrencia"
    
    def __str__(self):
        return self.nome
        

class AcompanhamentoPedagogicoAluno(models.Model):
    aluno = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,related_name='aluno')
    atendimento = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,related_name='atendimento',verbose_name='Atendido Por')
    dataConselho = models.DateField(u"Data Conselho", null=True,blank=True)
    tipoOcorrencia = models.ForeignKey(TipoOcorrencia, on_delete=models.CASCADE,null=True,verbose_name='Tipo de Atendimento')
    dataOcorrencia = models.DateTimeField(u"Data Ocorrência", null=True,blank=True, default=datetime.now)
    dataAtestadoInicio = models.DateField(u"Inicio Atestado", null=True,blank=True)
    dataAtestadoFim = models.DateField(u"Final Atestado", null=True,blank=True)
    #descricao = models.CharField(u"Descrição", max_length=5120, null=True, blank=False)
    descricao = RichTextField(u"Descrição", null=True, blank=False)
    dataAtendimento = models.DateField(u"Data Atendimento", null=True,blank=True)
    anexo = models.FileField(u"Anexo", null=True,blank=True, upload_to='documents/acompanhamento/%Y/%m/%d/')
    status = models.CharField(u"Status", max_length=1, default='A', choices=(('A', 'Ativo'), ('E', 'Excluído')))
    motivoExclusao = models.TextField(u"Motivo da Exclusão", null=True, blank=True)
    excluidoPor = models.ForeignKey(
        Pessoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acompanhamentos_excluidos",
        verbose_name=u"Excluído por"
    )
    dataExclusao = models.DateTimeField(u"Data da Exclusão", null=True, blank=True)
    class Meta:
        db_table = "acompanhamento_pedagogico_aluno"
        permissions = (
            ('ocorrencia_publica', 'Atendimento de ocorrência pública'),
            ('ocorrencia_restrita', 'Atendimento de ocorrência restrita'),
        )

    def __str__(self):
        return self.aluno.nome


class AcompanhamentoPedagogicoTurma(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE,null=False,related_name='turma')
    atendido = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,related_name='atendido',verbose_name='Atendido Por')
    tipoOcorrencia = models.ForeignKey(TipoOcorrencia, on_delete=models.CASCADE,null=True,verbose_name='Ocorrência')
    dataOcorrencia = models.DateField(u"Data Ocorrência", null=True,blank=True, default=datetime.now)
    descricao = models.CharField(u"Descrição", max_length=5120, null=True, blank=False)
    dataAtendimento = models.DateField(u"Data Atendimento", null=True,blank=True)
    anexo = models.FileField(u"Anexo", null=True, blank=True, upload_to='documents/acompanhamento/%Y/%m/%d/')
    
    class Meta:
        db_table = "acompanhamento_pedagogico_turma"
        
    def __str__(self):
        return self.turma.nome


class AcompanhamentoPedagogicoServidor(models.Model):
    servidor = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,related_name='servidor')
    atendidoPor = models.ForeignKey(Pessoa, on_delete=models.CASCADE,null=False,related_name='atendidoPor')
    tipoOcorrencia = models.ForeignKey(TipoOcorrencia, on_delete=models.CASCADE,null=True,verbose_name='Ocorrência')
    dataOcorrencia = models.DateField(u"Data Ocorrência", null=True,blank=True, default=datetime.now)
    descricao = models.CharField(u"Descrição", max_length=1024, null=True, blank=False)
    unidadeCurricular = models.ForeignKey(UnidadeCurricular, on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        db_table = "acompanhamento_pedagogico_servidor"


########
# CLASSES USADAS PARA PROCESSO DE IMPORTAÇÃO
########
class ImportAluno(models.Model):
    matricula = models.CharField(max_length=50)
    nome = models.CharField(max_length=500)
    nacionalidade = models.CharField(max_length=200)
    estado = models.CharField(max_length=200)
    dataNascimento = models.DateField()
    rg = models.CharField(max_length=50)
    cpf = models.CharField(max_length=50)
    telefone = models.CharField(max_length=50)
    email = models.CharField(max_length=200)
    necessidadeEspcial = models.CharField(max_length=200)
    sexo = models.CharField(max_length=1)
    raca = models.CharField(max_length=50)
    ingresso = models.CharField(max_length=200)
    curso = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    check_aluno = models.CharField(max_length=1,null=True)
    class Meta:
        db_table = "import_aluno"


class ImportUnidadeCurricularesAluno(models.Model):
    matricula = models.CharField(max_length=50)
    nome = models.CharField(max_length=500)
    periodo = models.CharField(max_length=1)
    situacao = models.CharField(max_length=50)
    siglaUC = models.CharField(max_length=50)
    nomeUC = models.CharField(max_length=200)
    notaUC = models.CharField(max_length=50)
    frequencia = models.CharField(max_length=50)
    percentualFrenquencia = models.CharField(max_length=200)
    anp = models.CharField(max_length=200)
    check_aluno = models.CharField(max_length=1,null=True)
    class Meta:
        db_table = "import_uc_aluno"

##Tabelas relacionadas ao conselho de classe
class PeriodoConselho(models.Model):
    """
    Cadastros dinâmicos das etapas/etapas avaliativas.
    Exemplos: '1º Trimestre', '2º Trimestre', '1º Semestre', 'Conselho Final'.
    """
    nome = models.CharField(u"Periodo", max_length=100, null=False, blank=False)
    ordem = models.IntegerField(u"Ordem de Exibição", default=1, help_text="Ordem cronológica no ano")
    ativo = models.CharField(u"Ativo", max_length=1, choices=ATIVO_INATIVO, default="A")

    class Meta:
        db_table = "periodo_conselho"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class ConselhoClasse(models.Model):
    """
    Cada conselho realizado ganha um ID sequencial único próprio (PK).
    Turma, Ano e Período ficam registrados para histórico.
    """
    # id = models.AutoField(primary_key=True) -> O Django cria automaticamente!

    turma = models.ForeignKey(
        Turma,
        on_delete=models.PROTECT,  # Se alguém tentar excluir a turma, o banco não deixa apagar o histórico do conselho
        verbose_name="Turma"
    )
    ano = models.IntegerField(
        u"Ano Letivo",
        default=datetime.now().year
    )
    periodoConselho = models.ForeignKey(
        PeriodoConselho,
        on_delete=models.PROTECT,
        verbose_name="Período do Conselho"
    )
    dataConselho = models.DateField(
        u"Data de Realização",
        default=datetime.now
    )
    parecerGeral = RichTextField(
        u"Parecer Geral da Turma",
        null=True,
        blank=True
    )
    finalizado = models.CharField(
        u"Finalizado",
        max_length=1,
        choices=SIM_NAO,
        default="N"
    )
    responsavel = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="conselhos_realizados",
        verbose_name="Registrado por"
    )
    dataCadastro = models.DateTimeField(
        u"Data Cadastro",
        auto_now_add=True
    )
    status = models.CharField(u"Status", max_length=1, default='A', choices=(('A', 'Ativo'), ('E', 'Excluído')))

    class Meta:
        db_table = "conselho_classe"
        ordering = ['-ano', '-dataConselho', '-id']

    def __str__(self):
        return f"Conselho #{self.id} - {self.turma.nome} ({self.periodoConselho.nome}/{self.ano})"


class ConselhoClasseAluno(models.Model):
    """
    Parecer individual do aluno dentro de um Conselho específico.
    Vinculado por chave estrangeira ao ConselhoClasse (por ID) e ao Aluno.
    """
    conselho = models.ForeignKey(
        ConselhoClasse,
        on_delete=models.CASCADE,
        related_name="alunos_avaliados"
    )
    aluno = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="avaliacoes_conselho"
    )
    parecer = RichTextField(
        u"Parecer Individual",
        null=True,
        blank=True
    )
    # Vínculo com a ficha oficial do aluno (AcompanhamentoPedagogicoAluno)
    acompanhamentoGerado = models.OneToOneField(
        AcompanhamentoPedagogicoAluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origem_conselho",
        verbose_name="Registro na Ficha do Aluno"
    )

    class Meta:
        db_table = "conselho_classe_aluno"
        unique_together = (("conselho", "aluno"),)

    def __str__(self):
        return f"{self.aluno.nome} - Conselho #{self.conselho.id}"

class SessaoParecerTurma(models.Model):
    """
    Sessão de lançamento de pareceres de uma turma (sem exibição de notas).
    """
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    ano = models.IntegerField(u"Ano Letivo", default=datetime.now().year)
    periodoConselho = models.ForeignKey(
        PeriodoConselho,
        on_delete=models.PROTECT,
        verbose_name="Etapa / Período",
        null=True, blank=True
    )
    dataRegistro = models.DateField(u"Data de Registro", default=datetime.now)
    observacaoGeral = models.TextField(u"Observação Geral da Turma", null=True, blank=True)
    finalizado = models.CharField(u"Finalizado", max_length=1, choices=SIM_NAO, default="N")
    status = models.CharField(u"Status", max_length=1, default='A', choices=(('A', 'Ativo'), ('E', 'Excluído')))
    responsavel = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="sessoes_pareceres_criadas",
        verbose_name="Responsável"
    )
    criadoEm = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessao_parecer_turma"
        ordering = ['-ano', '-dataRegistro', '-id']

    def __str__(self):
        return f"Pareceres: {self.turma.nome} ({self.ano})"


class ItemParecerAluno(models.Model):
    """
    Parecer individual de cada aluno digitado nesta sessão.
    """
    sessao = models.ForeignKey(SessaoParecerTurma, on_delete=models.CASCADE, related_name="alunos_parecer")
    aluno = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="pareceres_recebidos")
    parecer = models.TextField(u"Parecer do Aluno", null=True, blank=True)
    acompanhamentoGerado = models.OneToOneField(
        AcompanhamentoPedagogicoAluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origem_sessao_parecer"
    )

    class Meta:
        db_table = "item_parecer_aluno"
        unique_together = (("sessao", "aluno"),)