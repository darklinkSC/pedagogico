from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from datetime import timedelta
from datetime import datetime

from geral.models import TIPO_PESSOA_ALUNO, TIPO_PESSOA_SERVIDOR
from geral.models import Pessoa
from pedagogico.models import Turma, Matricula, Curso, AcompanhamentoPedagogicoTurma, InformacoesAlunos, TipoOcorrencia

from pedagogico.app.formsAcompanhamentoPedagogicoTurma import AcompanhamentoPedagogicoTurmaForm

from django.db.models import Q, Count

from django.views.generic import UpdateView

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def acompanhamentoPedagogicoTurma(request):
    # 1. Buscamos as combinações únicas de Sigla e Período diretamente das Matrículas
    # Usamos o 'unidadeCurricular__curso__sigla' e 'periodo' para montar nossa "Turma Virtual"
    queryset = Matricula.objects.values(
        'unidadeCurricular__curso__id', 
        'unidadeCurricular__curso__nome', 
        'unidadeCurricular__curso__sigla', 
        'periodo'
    ).distinct().order_by('-unidadeCurricular__curso__sigla', 'periodo')

    # 3. Transformamos o QuerySet em uma lista de objetos/dicionários formatados
    # para facilitar o uso no HTML e na URL
    lista_turmas = []
    for item in queryset:
        curso_id = item['unidadeCurricular__curso__id']
        sigla = item['unidadeCurricular__curso__sigla']
        periodo = item['periodo']
        curso = item['unidadeCurricular__curso__nome']
        lista_turmas.append({
            'sigla_periodo': f"{sigla}-{periodo}",
            'sigla': sigla,
            'curso': curso,
            'curso_id': curso_id,
            'periodo':periodo
        })

    # 4. Paginação (Mantendo seus padrões de 50 por página)
    paginas = Paginator(lista_turmas, 50)
    page = request.GET.get('page')
    lista = paginas.get_page(page)

    return render(request, "acompanhamentoPedagogicoTurma.html", {
        'lista': lista,
        'tipoPessoa': 'Turmas (Sigla-Período)'
    })



@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAcompanhamentoPedagogicoTurma(request, id):
    turma = get_object_or_404(Turma, id=id)
    
    lista = AcompanhamentoPedagogicoTurma.objects.filter(turma=turma).order_by('-id')
        
    return render(request, 'listAcompanhamentoPedagogicoTurma.html', {'lista':lista, 'turma':turma})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addOcorrenciaTurma(request, id):
    form = AcompanhamentoPedagogicoTurmaForm()
    if(request.method == 'POST'):
        form = AcompanhamentoPedagogicoTurmaForm(request.POST, request.FILES)
        if(form.is_valid()):
            turma = get_object_or_404(Turma, id=id)
            user = request.user 

            atendido = get_object_or_404(Pessoa,user=user)

            form.instance.turma = turma
            form.instance.atendido = atendido
            
            form.save()
            return listAcompanhamentoPedagogicoTurma(request,id)
    elif(request.method == 'GET'):
        return render(request, "addOcorrenciaTurma.html", {'form':form,'idTurma':id})    


from django.db.models import Max

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listarAcompanhamentoPedagogicoTurma(request, curso_id, periodo):
    # 1. Busca o curso ou retorna 404 se não existir
    curso_obj = get_object_or_404(Curso, id=curso_id)
    
    # 2. Busca as matrículas filtrando pelo ID do curso e o número do período
    # O values/annotate faz o GROUP BY por aluno no MySQL
    lista_alunos = Matricula.objects.filter(
        unidadeCurricular__curso_id=curso_id,
        periodo=periodo,
        status='A'
    ).values(
        'aluno__id', 
        'aluno__nome', 
        'aluno__email', 
        'aluno__telefone',
        'aluno__matricula'
    ).annotate(id_max=Max('id')).order_by('aluno__nome')

    return render(request, "listarTurma.html", {
        'lista': lista_alunos,
        'curso': curso_obj,
        'periodo': periodo,
        'total': lista_alunos.count(),
    })