from django.urls import path, re_path

from . import views
from .app import viewAluno 
from .app import viewCurso
from .app import viewTipoOcorrencia
from .app import viewUnidadeCurricular
from .app import viewAcompanhamentoPedagogico
from .app import viewAcompanhamentoPedagogicoTurma
from .app import viewTurma
from .app import viewConselhoClasse
from .app import viewParecerTurma
from wkhtmltopdf.views import PDFTemplateView

app_name="pedagogico"

urlpatterns = [
    #path('geral/listServidor', views.listServidor, name='listServidor'),
    path('pedagogico/importAluno/', views.importAluno, name="importAluno"),
    path('pedagogico/importUnidadeCurricular/', views.importUnidadeCurricular, name="importUnidadeCurricular"),
    path('pedagogico/importConselhoClasse/', views.importConselhoClasse, name="importConselhoClasse"),
    path('pedagogico/converterBaseAlunos/', views.converterBaseAluno, name='converterBaseAlunos'),
    path('pedagogico/converterBaseCurso/', views.converterBaseCurso, name='converterBaseCurso'),
    path('pedagogico/converterBaseUnidadeCurricular/', views.converterBaseUnidadeCurricular, name='converterBaseUnidadeCurricular'),
    path('pedagogico/converterBaseMatricula/', views.converterBaseMatricula, name='converterBaseMatricula'),
    path('pedagogico/importarDados/', views.importarDados, name='importarDados'),
    path('pedagogico/listAlunosImportados/', views.listAlunosImportados, name='listAlunosImportados'), 
    path('pedagogico/listMatriculasImportadas/', views.listMatriculasImportadas, name='listMatriculasImportadas'),
    #### ALUNOS #####
    path('pedagogico/listAluno/', viewAluno.listAluno, name='listAluno'),
    path('pedagogico/addAluno/', viewAluno.addAluno, name='addAluno'),
    path('pedagogico/updateAluno/<int:id>', viewAluno.updateAluno, name='updateAluno'),
    path('pedagogico/addMatricula/<int:id>', viewAluno.addMatricula, name='addMatricula'), 
    #### CURSOS ####
    path('pedagogico/listCurso/', viewCurso.listCurso, name='listCurso'),
    path('pedagogico/addCurso/', viewCurso.addCurso, name='addCurso'),
    path('pedagogico/updateCurso/<int:id>', viewCurso.updateCurso, name='updateCurso'),
    #### TIPO DE OCORRENCIA ####
    path('pedagogico/listTipoOcorrencia/', viewTipoOcorrencia.listTipoOcorrencia, name='listTipoOcorrencia'),
    path('pedagogico/addTipoOcorrencia/', viewTipoOcorrencia.addTipoOcorrencia, name='addTipoOcorrencia'),
    path('pedagogico/updateTipoOcorrencia/<int:id>', viewTipoOcorrencia.updateTipoOcorrencia, name='updateTipoOcorrencia'),
    #### UNIDADE CURRICULARES ####
    path('pedagogico/listUnidadeCurricular/', viewUnidadeCurricular.listUnidadeCurricular, name='listUnidadeCurricular'),
    path('pedagogico/addUnidadeCurricular/', viewUnidadeCurricular.addUnidadeCurricular, name='addUnidadeCurricular'),
    path('pedagogico/updateUnidadeCurricular/<int:id>', viewUnidadeCurricular.updateUnidadeCurricular, name='updateUnidadeCurricular'),
    #### TURMAS ####
    path('pedagogico/listTurma/', viewTurma.listTurma, name='listTurma'),
    path('pedagogico/addTurma/', viewTurma.addTurma, name='addTurma'),
    path('pedagogico/updateTurma/<int:id>', viewTurma.updateTurma, name='updateTurma'),
    #### ACOMPANHAMENTO PEDAGOGICO #####
    path('pedagogico/acompanhamentoPedagogico', viewAcompanhamentoPedagogico.acompanhamentoPedagogico, name='acompanhamentoPedagogico'),
    path('pedagogico/acompanhamentoPedagogicoServidor', viewAcompanhamentoPedagogico.acompanhamentoPedagogicoServidor, name='acompanhamentoPedagogicoServidor'),
    path('pedagogico/listAcompanhamentoPedagogico/<int:id>', viewAcompanhamentoPedagogico.listAcompanhamentoPedagogico, name='listAcompanhamentoPedagogico'),
    path('pedagogico/listAcompanhamentoPedagogicoDetalhado/<int:id>', viewAcompanhamentoPedagogico.listAcompanhamentoPedagogicoDetalhado, name='listAcompanhamentoPedagogicoDetalhado'),
    path('pedagogico/addOcorrenciaAluno/<int:id>', viewAcompanhamentoPedagogico.addOcorrenciaAluno, name='addOcorrenciaAluno'),
    path('pedagogico/updateParecerAluno/<int:id>', viewAcompanhamentoPedagogico.updateParecerAluno, name='updateParecerAluno'),
    path('pedagogico/addParecerAluno/<int:id>', viewAcompanhamentoPedagogico.addParecerAluno, name='addParecerAluno'),
    path('pedagogico/salvarNotaParcial/<int:id>/<int:id_uc>/', viewAcompanhamentoPedagogico.salvarNotaParcial, name='salvarNotaParcial'),
    path('pedagogico/addOcorrenciaAlunoRestrito/<int:id>', viewAcompanhamentoPedagogico.addOcorrenciaAlunoRestrito, name='addOcorrenciaAlunoRestrito'),
    path('pedagogico/addAtestadoAluno/<int:id>', viewAcompanhamentoPedagogico.addAtestadoAluno, name='addAtestadoAluno'), 
    path('pedagogico/ultimosAtendimentos/', viewAcompanhamentoPedagogico.ultimosAtendimentos, name='ultimosAtendimentos'), 
    path('pedagogico/updateSimPAEVS/<int:id>', viewAcompanhamentoPedagogico.updateSimPAEVS, name='updateSimPAEVS'),
    path('pedagogico/updateNaoPAEVS/<int:id>', viewAcompanhamentoPedagogico.updateNaoPAEVS, name='updateNaoPAEVS'),
    path('pedagogico/listAlunosComPaevs/', viewAcompanhamentoPedagogico.listAlunosComPaevs, name='listAlunosComPaevs'),
    path('pedagogico/listAlunosComNecessidades/', viewAcompanhamentoPedagogico.listAlunosComDeficiencia, name='listAlunosComNecessidades'),
    path('pedagogico/listAlunosAtestado/', viewAcompanhamentoPedagogico.listAlunosAtestado, name='listAlunosAtestado'), 
    path('pedagogico/chartAcompanhamento/', viewAcompanhamentoPedagogico.chartAcompanhamentoOcorrencia, name='chartAcompanhamento'), 
    path('pedagogico/acompanhamentoPedagogicoTurma', viewAcompanhamentoPedagogicoTurma.acompanhamentoPedagogicoTurma, name='acompanhamentoPedagogicoTurma'),
    path('pedagogico/listAcompanhamentoPedagogicoTurma/<int:id>', viewAcompanhamentoPedagogicoTurma.listAcompanhamentoPedagogicoTurma, name='listAcompanhamentoPedagogicoTurma'),
    path('pedagogico/addOcorrenciaTurma/<int:id>', viewAcompanhamentoPedagogicoTurma.addOcorrenciaTurma, name='addOcorrenciaTurma'),
    path('pedagogico/listCursoConselhoClasse/', viewConselhoClasse.listCursoConselhoClasse, name='listCursoConselhoClasse'),
    path('pedagogico/listTurmaConselhoClasse/<int:id>', viewConselhoClasse.listTurmaConselhoClasse, name='listTurmaConselhoClasse'), 
    path('pedagogico/listUnidadeCurricularConselhoClasse/<int:curso_id>/<int:periodo>', viewConselhoClasse.listUnidadeCurricularConselhoClasse, name='listUnidadeCurricularConselhoClasse'), 
    path('pedagogico/listAlunosConselhoClasse/<int:id>', viewConselhoClasse.listAlunosConselhoClasse, name='listAlunosConselhoClasse'), 
    path('pedagogico/listAlunoPorUCConselhoClasse/<int:curso_id>/<int:periodo>', viewConselhoClasse.listAlunoPorUCConselhoClasse, name='listAlunoPorUCConselhoClasse'),     
    path('pedagogico/listAlunoConselhoClasse/<int:id_aluno>/<int:id_curso>/<int:periodo>', viewConselhoClasse.listAlunoConselhoClasse, name='listAlunoConselhoClasse'),
    path('pedagogico/printAcompanhamentoPedagogico/<int:id>/<int:id_atendimento>', viewAcompanhamentoPedagogico.printAcompanhamentoPedagogico, name='printAcompanhamentoPedagogico'),
    path('pedagogico/printRelatorioAcompanhamentoPedagogico/<int:id>/<int:id_ocorrencia>', viewAcompanhamentoPedagogico.printRelatorioAcompanhamentoPedagogico, name='printRelatorioAcompanhamentoPedagogico'),
    path('pedagogico/converterBaseTurma/', views.converterBaseTurma, name='converterBaseTurma'),
    path('pedagogico/turma/<int:turma_id>/gerenciar/', viewTurma.gerenciarAlunosTurma, name='gerenciarAlunosTurma'),
    path('pedagogico/turma/<int:turma_id>/removerAluno/<int:aluno_id>/', viewTurma.removerAlunoTurma, name='removerAlunoTurma'),
    path('pedagogico/turma/<int:turma_id>/adicionarAluno/<int:aluno_id>/', viewTurma.adicionarAlunoTurma, name='adicionarAlunoTurma'),
    path('pedagogico/acompanhamento/<int:id>/excluir/', viewAcompanhamentoPedagogico.excluirAcompanhamentoPedagogico, name='excluirAcompanhamentoPedagogico'),
    path('pedagogico/updateSimDeficiencia/<int:id>', viewAcompanhamentoPedagogico.updateSimDeficiencia, name='updateSimDeficiencia'),
    path('pedagogico/updateNaoDeficiencia/<int:id>', viewAcompanhamentoPedagogico.updateNaoDeficiencia, name='updateNaoDeficiencia'),

    # Conselho de Classe
    path('pedagogico/conselhos/', viewConselhoClasse.listagemConselhos, name='listagemConselhos'),
    path('pedagogico/conselho/novo/', viewConselhoClasse.criarConselho, name='criarConselho'),
    path('pedagogico/conselho/<int:id>/', viewConselhoClasse.painelConselho, name='painelConselho'),
    path('pedagogico/conselho/<int:id>/excluir/', viewConselhoClasse.excluirConselhoClasse, name='excluirConselhoClasse'),
    # Pareceres
    path('pedagogico/pareceres/', viewParecerTurma.listagemPareceres, name='listagemPareceres'),
    path('pedagogico/pareceres/novo/', viewParecerTurma.criarSessaoParecer, name='criarSessaoParecer'),
    path('pedagogico/pareceres/<int:id>/', viewParecerTurma.painelParecerTurma, name='painelParecerTurma'),
    path('pedagogico/pareceres/<int:id>/excluir/', viewParecerTurma.excluirSessaoParecer, name='excluirSessaoParecer'),
    ##### TESTES PARA IA #####
    path('pedagogico/chat-ia/', views.chat_ia_view, name='chat_ia'),
    # Rota para o salvamento definitivo no banco
    path('salvar-atraso-ia/', views.salvar_atraso_ia, name='salvar_atraso_ia'),
    ##### Professores acessarem o atestado ######
    path('pedagogico/atestados/', views.lista_alunos_atestado, name='lista_atestados_professores'),
    ##### Troca de ano ######
    path('pedagogico/atualizarStatusTrocaAno/', views.atualizarStatusTrocaAno, name='atualizarStatusTrocaAno'),
    ##### Listar Turmas ######
    path('pedagogico/listarTurma/<int:curso_id>/<int:periodo>/', viewAcompanhamentoPedagogicoTurma.listarAcompanhamentoPedagogicoTurma, name='listarTurma')
]
