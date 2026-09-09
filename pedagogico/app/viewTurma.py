from django.core.paginator import Paginator
from pedagogico.app.formsTurma import TurmaForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Max, Q

from geral.models import Pessoa, STATUS_ATIVO, STATUS_INATIVO, TIPO_PESSOA_ALUNO
from pedagogico.models import Turma, Matricula, UnidadeCurricular

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def listTurma(request):
    lista = Turma.objects.all()
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 10)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'listTurma.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def addTurma(request):
    form = TurmaForm()
    if(request.method == 'POST'):
        form = TurmaForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/pedagogico/listTurma')        
    elif(request.method == 'GET'):
        return render(request, "addTurma.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def updateTurma(request, id):
    turma = get_object_or_404(Turma, id=id)
    form = TurmaForm(instance=turma)
    
    if(request.method == 'POST'):
        form = TurmaForm(request.POST, instance=turma)
        if(form.is_valid()):
            turma = form.save(commit=False)
            form.save()
            return redirect('/pedagogico/listTurma')   
    elif(request.method == 'GET'):
        return render(request, "updateTurma.html", {'form':form, 'turma': turma})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def gerenciarAlunosTurma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    curso = turma.curso
    periodo = turma.periodo

    # 1. Alunos que atualmente estão nesta turma/período
    alunos_turma = Matricula.objects.filter(
        unidadeCurricular__curso=curso,
        periodo=periodo,
        status=STATUS_ATIVO
    ).values(
        'aluno__id', 'aluno__nome', 'aluno__matricula', 'aluno__email'
    ).annotate(id_max=Max('id')).order_by('aluno__nome')

    ids_atuais = [a['aluno__id'] for a in alunos_turma]

    # 2. Busca para adicionar novo aluno que não esteja na lista atual
    busca = request.GET.get('busca_aluno', '').strip()
    alunos_disponiveis = []
    if busca:
        alunos_disponiveis = Pessoa.objects.filter(
            tipoPessoa=TIPO_PESSOA_ALUNO,
            status=STATUS_ATIVO
        ).filter(
            Q(nome__icontains=busca) | Q(matricula__icontains=busca)
        ).exclude(id__in=ids_atuais)[:10]

    return render(request, "conselho/gerenciarTurma.html", {
        'turma': turma,
        'alunos_turma': alunos_turma,
        'alunos_disponiveis': alunos_disponiveis,
        'busca': busca,
    })


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def removerAlunoTurma(request, turma_id, aluno_id):
    turma = get_object_or_404(Turma, id=turma_id)
    aluno = get_object_or_404(Pessoa, id=aluno_id)

    # Inativa as matrículas do aluno nesta turma/período
    qtd = Matricula.objects.filter(
        aluno=aluno,
        unidadeCurricular__curso=turma.curso,
        periodo=turma.periodo,
        status=STATUS_ATIVO
    ).update(status=STATUS_INATIVO)

    messages.warning(request, f"Aluno {aluno.nome} foi removido da turma {turma.nome} ({qtd} disciplinas inativadas).")
    return redirect('pedagogico:gerenciarAlunosTurma', turma_id=turma.id)


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def adicionarAlunoTurma(request, turma_id, aluno_id):
    turma = get_object_or_404(Turma, id=turma_id)
    aluno = get_object_or_404(Pessoa, id=aluno_id)

    # Disciplinas daquela turma/fase
    disciplinas = UnidadeCurricular.objects.filter(
        curso=turma.curso,
        periodo=turma.periodo
    )

    if not disciplinas.exists():
        messages.error(request, f"Não existem Unidades Curriculares cadastradas no período {turma.periodo} para o curso {turma.curso.sigla}.")
        return redirect('pedagogico:gerenciarAlunosTurma', turma_id=turma.id)

    with transaction.atomic():
        for uc in disciplinas:
            matricula, created = Matricula.objects.get_or_create(
                aluno=aluno,
                unidadeCurricular=uc,
                defaults={
                    'periodo': turma.periodo,
                    'status': STATUS_ATIVO,
                    'notaFinal': '',
                    'percentualFalta': '0'
                }
            )
            if not created and matricula.status != STATUS_ATIVO:
                matricula.status = STATUS_ATIVO
                matricula.periodo = turma.periodo
                matricula.save()

    messages.success(request, f"Aluno {aluno.nome} adicionado com sucesso à turma {turma.nome}!")
    return redirect('pedagogico:gerenciarAlunosTurma', turma_id=turma.id)