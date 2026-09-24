import pdfkit
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from datetime import timedelta
from datetime import datetime, date
from django.contrib import messages

from geral.models import TIPO_PESSOA_ALUNO, TIPO_PESSOA_SERVIDOR, STATUS_ATIVO
from geral.models import Pessoa 
from pedagogico.models import Matricula, Curso, AcompanhamentoPedagogicoAluno, InformacoesAlunos, TipoOcorrencia, UnidadeCurricular, ImportConselhoClasse, Turma

from pedagogico.app.formsAcompanhamentoPedagogico import AcompanhamentoPedagogicoAlunoForm
from pedagogico.app.formsAcompanhamentoPedagogico import AcompanhamentoPedagogicoAlunoParecerForm
from pedagogico.app.formsAcompanhamentoPedagogico import AcompanhamentoPedagogicoAlunoRestritoForm
from pedagogico.app.formsAcompanhamentoPedagogico import AcompanhamentoPedagogicoAlunoAtestadoForm

from django.db.models import Q, Count
from django.http import HttpResponse

from django.views.generic import UpdateView

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def acompanhamentoPedagogico(request):
    return acompanhamentoPedagogicoTipoPessoa(request, TIPO_PESSOA_ALUNO)


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def acompanhamentoPedagogicoServidor(request):
    return acompanhamentoPedagogicoTipoPessoa(request, TIPO_PESSOA_SERVIDOR)


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def acompanhamentoPedagogicoTipoPessoa(request, tipoPessoa):
    lista = Pessoa.objects.filter(tipoPessoa=tipoPessoa)

    tipoPessoaDescricao = ''
    if tipoPessoa == TIPO_PESSOA_ALUNO :
        tipoPessoaDescricao = 'Alunos'
    else:
        tipoPessoaDescricao = 'Servidores'
    

    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 50)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'acompanhamentoPedagogico.html', {'lista':lista, 'tipoPessoa':tipoPessoaDescricao})


@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
@login_required(login_url="/login/")
def listAcompanhamentoPedagogico(request, id):
    aluno = get_object_or_404(Pessoa, id=id)
    info_aluno, _ = InformacoesAlunos.objects.get_or_create(
        aluno_id=id,
        defaults={'paevs': 'N', 'deficiencia': 'N'}
    )
    acompanhamentos = AcompanhamentoPedagogicoAluno.objects.filter(
        aluno=aluno
    ).exclude(status='E').select_related('tipoOcorrencia', 'atendimento').order_by('-dataAtendimento', '-id')

    tipo_filtro = request.GET.get('tipo_atendimento')
    if tipo_filtro:
        acompanhamentos = acompanhamentos.filter(tipoOcorrencia_id=tipo_filtro)

    tipos_ocorrencia = TipoOcorrencia.objects.all().order_by('nome')

    return render(request, "listAcompanhamentoPedagogico.html", {
        'aluno': aluno,
        'info_aluno': info_aluno,
        'acompanhamentos': acompanhamentos,
        'tipos_ocorrencia': tipos_ocorrencia,
        'detalhado': False,  # <--- Marca como Simplificado
    })


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.delete_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAcompanhamentoPedagogico(request, id):
    aluno = get_object_or_404(Pessoa, id=id)

    # 1. Recupera ou cria as informações de PAEVS e Deficiência do aluno
    info_aluno, _ = InformacoesAlunos.objects.get_or_create(
        aluno_id=id,
        defaults={'paevs': 'N', 'deficiencia': 'N'}
    )

    # 2. Verifica a permissão de ocorrência restrita
    pode_ver_restrito = (
            request.user.is_superuser or
            request.user.has_perm('pedagogico.atendimento_de_ocorrencia_restrita') or
            request.user.has_perm('pedagogico.view_acompanhamentopedagogicoalunorestrito') or
            request.user.user_permissions.filter(name__icontains='restrita').exists() or
            request.user.groups.filter(permissions__name__icontains='restrita').exists()
    )

    # 3. Busca os acompanhamentos ativos (soft delete)
    acompanhamentos = AcompanhamentoPedagogicoAluno.objects.filter(
        aluno=aluno
    ).exclude(status='E').select_related('tipoOcorrencia', 'atendimento').order_by('-dataAtendimento', '-id')

    # 4. Se NÃO tem permissão, esconde o que NÃO é público (statusPublico='N')
    if not pode_ver_restrito:
        acompanhamentos = acompanhamentos.exclude(tipoOcorrencia__statusPublico='N')

    # Filtro opcional do combobox
    tipo_filtro = request.GET.get('tipo_atendimento')
    if tipo_filtro:
        acompanhamentos = acompanhamentos.filter(tipoOcorrencia_id=tipo_filtro)

    # Combobox de busca (também oculta tipos restritos para quem não pode ver)
    tipos_ocorrencia = TipoOcorrencia.objects.all().order_by('nome')
    if not pode_ver_restrito:
        tipos_ocorrencia = tipos_ocorrencia.exclude(statusPublico='N')

    return render(request, "listAcompanhamentoPedagogico.html", {
        'aluno': aluno,
        'info_aluno': info_aluno,          # Agora definida e enviada corretamente
        'acompanhamentos': acompanhamentos,
        'tipos_ocorrencia': tipos_ocorrencia,
        'restrito': pode_ver_restrito,     # Controla a visibilidade do botão no template
        'detalhado': False,
    })


@login_required(login_url="/login/")
def listAcompanhamentoPedagogicoDetalhado(request, id):
    aluno = get_object_or_404(Pessoa, id=id)

    # 1. Recupera ou cria as informações de PAEVS e Deficiência do aluno
    info_aluno, _ = InformacoesAlunos.objects.get_or_create(
        aluno_id=id,
        defaults={'paevs': 'N', 'deficiencia': 'N'}
    )
    pode_ver_restrito = (
            request.user.is_superuser or
            request.user.has_perm('pedagogico.atendimento_de_ocorrencia_restrita') or
            request.user.has_perm('pedagogico.view_acompanhamentopedagogicoalunorestrito') or
            request.user.user_permissions.filter(name__icontains='restrita').exists() or
            request.user.groups.filter(permissions__name__icontains='restrita').exists()
    )

    # 2. Busca acompanhamentos ativos (soft delete)
    acompanhamentos = AcompanhamentoPedagogicoAluno.objects.filter(
        aluno=aluno
    ).exclude(status='E').select_related('tipoOcorrencia', 'atendimento').order_by('-dataAtendimento', '-id')

    # 3. FILTRO CORRETO USANDO statusPublico:
    # Se NÃO tiver a permissão, oculta as ocorrências que NÃO são públicas (statusPublico='N')
    if not pode_ver_restrito:
        acompanhamentos = acompanhamentos.exclude(tipoOcorrencia__statusPublico='N')

    # Filtro opcional do combobox
    tipo_filtro = request.GET.get('tipo_atendimento')
    if tipo_filtro:
        acompanhamentos = acompanhamentos.filter(tipoOcorrencia_id=tipo_filtro)

    # O combobox também esconde tipos restritos para quem não pode ver
    tipos_ocorrencia = TipoOcorrencia.objects.all().order_by('nome')
    if not pode_ver_restrito:
        tipos_ocorrencia = tipos_ocorrencia.exclude(statusPublico='N')

    return render(request, "listAcompanhamentoPedagogico.html", {
        'aluno': aluno,
        'info_aluno': info_aluno,
        'acompanhamentos': acompanhamentos,
        'tipos_ocorrencia': tipos_ocorrencia,
        'restrito': pode_ver_restrito,
        'detalhado': True,
    })


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAcompanhamentoPedagogicoExibicao(request, id, tipoExibicao):
    pessoa = get_object_or_404(Pessoa, id=id)
    ### CONSEGUINDO INFORMACAO DO CURSO ###
    matriculas = Matricula.objects.filter(aluno=pessoa,status=STATUS_ATIVO)
    curso = Curso
    for matricula in matriculas:
        curso = matricula.unidadeCurricular.curso
    
    ### CONSEGUINDO INFORMACOES ADICIONAIS DO ALUNO ###
    infos = InformacoesAlunos.objects.filter(aluno=pessoa)
    infoAluno = InformacoesAlunos
    for info in infos:
        infoAluno = info

    ### Tipos de Ocorrencia ###
    listTipoOcorrencia = TipoOcorrencia.objects.all()

    ''' 
        Realizando a busca e filtrando na tabela
    '''
    buscaTipoOcorrrencia = request.GET.get('tipoOcorrencia')
    if buscaTipoOcorrrencia:
        lista = AcompanhamentoPedagogicoAluno.objects.filter(aluno=pessoa, tipoOcorrencia__id__exact=buscaTipoOcorrrencia).order_by('-id')
    else:
        lista = AcompanhamentoPedagogicoAluno.objects.filter(aluno=pessoa).order_by('-id')

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 20)
    page = request.GET.get('page')
    lista = paginas.get_page(page)

    return render(request, 'listAcompanhamentoPedagogico.html', {'lista': lista, 'listaMatricula': matriculas, 'aluno': pessoa, 'curso': curso,
                                                                 'infoAluno': infoAluno, 'tipoExibicao': tipoExibicao, 'listTipoOcorrencia': listTipoOcorrencia})



@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def template(request):
    return HttpResponse("<h1>Hello World</h1>")


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def printAcompanhamentoPedagogico(request, id, id_atendimento):
    pessoa = get_object_or_404(Pessoa, id=id)

    ### CONSEGUINDO INFORMACAO DO CURSO ###
    matriculas = Matricula.objects.filter(aluno=pessoa, status=STATUS_ATIVO)
    curso = Curso
    for matricula in matriculas:
        curso = matricula.unidadeCurricular.curso

    ### CONSEGUINDO INFORMACOES ADICIONAIS DO ALUNO ###
    infos = InformacoesAlunos.objects.filter(aluno=pessoa)
    infoAluno = InformacoesAlunos
    for info in infos:
        infoAluno = info

    ### Acompanhamento Pedagogico ###
    acompanhamentoPedagogico = get_object_or_404(AcompanhamentoPedagogicoAluno, id=id_atendimento)

    if acompanhamentoPedagogico.tipoOcorrencia.parecer == "S":
        #conselhoClasse = ImportConselhoClasse.objects.filter(matricula=pessoa.matricula,dataImportacao=acompanhamentoPedagogico.dataConselho,notas__gt=0)
        conselhoClasse = Matricula.objects.filter(aluno=pessoa,notaFinal__gt=0)
        return render(request, 'printAcompanhamentoPedagogicoParecer.html',
                  {'acompanhamentoPedagogico': acompanhamentoPedagogico, 'lista': conselhoClasse, 'aluno': pessoa, 'curso': curso,'infoAluno': infoAluno})
    else:
        return render(request, 'printAcompanhamentoPedagogico.html',
                      {'acompanhamentoPedagogico': acompanhamentoPedagogico, 'lista': matriculas, 'aluno': pessoa,
                       'curso': curso, 'infoAluno': infoAluno})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def printRelatorioAcompanhamentoPedagogico(request, id, id_ocorrencia):
    pessoa = get_object_or_404(Pessoa, id=id)
    ### CONSEGUINDO INFORMACAO DO CURSO ###
    matriculas = Matricula.objects.filter(aluno=pessoa, status=STATUS_ATIVO)
    curso = Curso
    for matricula in matriculas:
        curso = matricula.unidadeCurricular.curso

    ### CONSEGUINDO INFORMACOES ADICIONAIS DO ALUNO ###
    infos = InformacoesAlunos.objects.filter(aluno=pessoa)
    infoAluno = InformacoesAlunos
    for info in infos:
        infoAluno = info

    print("Opcao",id_ocorrencia)

    if id_ocorrencia != 0:
       lista = AcompanhamentoPedagogicoAluno.objects.filter(aluno=pessoa, tipoOcorrencia__id__exact=id_ocorrencia).order_by('-id')
    else:
       lista = AcompanhamentoPedagogicoAluno.objects.filter(aluno=pessoa).order_by('-id')

    return render(request, 'printRelatorioAcompanhamentoPedagogico.html',
                  {'lista': lista, 'aluno': pessoa, 'curso': curso, 'infoAluno': infoAluno})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addOcorrenciaAluno(request, id):
    form = AcompanhamentoPedagogicoAlunoForm()
    if(request.method == 'POST'):
        form = AcompanhamentoPedagogicoAlunoForm(request.POST, request.FILES)
        if(form.is_valid()):
            aluno = get_object_or_404(Pessoa, id=id)
            user = request.user 

            atendido = get_object_or_404(Pessoa,user=user)

            form.instance.aluno = aluno
            form.instance.atendimento = atendido
            
            form.save()
            return listAcompanhamentoPedagogico(request,id)
    elif(request.method == 'GET'):
        return render(request, "addOcorrenciaAluno.html", {'form':form,'idPessoa':id,'restrito':False})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_turma', login_url='/geral/paginaSemPermissao')
def updateParecerAluno(request, id):
    parecer = get_object_or_404(AcompanhamentoPedagogicoAluno, id=id)
    form = AcompanhamentoPedagogicoAlunoForm(instance=parecer)

    if (request.method == 'POST'):
        form = AcompanhamentoPedagogicoAlunoForm(request.POST, instance=parecer)
        if (form.is_valid()):
            parecer = form.save(commit=False)
            form.save()
            return listAcompanhamentoPedagogico(request,parecer.aluno.id)
    elif (request.method == 'GET'):
        return render(request, "updateParecerAluno.html", {'form': form, 'parecer': parecer})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addParecerAluno(request, id):
    aluno = get_object_or_404(Pessoa, id=id)
    ### CONSEGUINDO INFORMACAO DO CURSO ###
    data = date.today()
    ano = data.strftime('%Y')
    conselhoClasse = Matricula.objects.filter(aluno=aluno).order_by('unidadeCurricular')

    return render(request, "addParecerAluno.html", {'idPessoa': id, 'restrito': False, 'conselhoClasse':conselhoClasse, 'aluno':aluno})

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def salvarNotaParcial(request, id, id_uc):
    aluno = get_object_or_404(Pessoa, id=id)
    uc = get_object_or_404(UnidadeCurricular, id=id_uc)

    notaParcial = request.POST.get('notaParcial')

    matriculas = Matricula.objects.filter(aluno=aluno, unidadeCurricular=uc, status=STATUS_ATIVO)

    for matricula in matriculas:
        matricula.notaParcial = notaParcial
        matricula.save()

    return addParecerAluno(request, id)


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.ocorrencia_restrita', login_url='/geral/paginaSemPermissao')
def addOcorrenciaAlunoRestrito(request, id):
    form = AcompanhamentoPedagogicoAlunoRestritoForm()
    if(request.method == 'POST'):
        form = AcompanhamentoPedagogicoAlunoRestritoForm(request.POST, request.FILES)
        if(form.is_valid()):
            aluno = get_object_or_404(Pessoa, id=id)
            user = request.user 

            atendido = get_object_or_404(Pessoa,user=user)

            form.instance.aluno = aluno
            form.instance.atendimento = atendido
            
            form.save()
            return listAcompanhamentoPedagogico(request,id)
    elif(request.method == 'GET'):
        return render(request, "addOcorrenciaAluno.html", {'form':form,'idPessoa':id,'restrito':True})  


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addAtestadoAluno(request, id):
    form = AcompanhamentoPedagogicoAlunoAtestadoForm()
    if(request.method == 'POST'):
        form = AcompanhamentoPedagogicoAlunoAtestadoForm(request.POST, request.FILES)
        if(form.is_valid()):
            aluno = get_object_or_404(Pessoa, id=id)
            user = request.user 

            atendido = get_object_or_404(Pessoa,user=user)
            
            form.instance.aluno = aluno
            form.instance.atendimento = atendido
            
            form.save()
            return listAcompanhamentoPedagogico(request,id)
    elif(request.method == 'GET'):
        return render(request, "addAtestadoAluno.html", {'form':form,'idPessoa':id}) 


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def ultimosAtendimentos(request):
    listaTipoOcorrencia = TipoOcorrencia.objects.all()
    lista = AcompanhamentoPedagogicoAluno.objects.all().order_by('-id')
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    buscaTipoOcorrrencia = request.GET.get('tipoOcorrencia')
    if busca:
        lista = lista.filter(Q(aluno__nome__icontains = busca))

    if buscaTipoOcorrrencia:
        lista = lista.filter(Q(tipoOcorrencia__id__exact = buscaTipoOcorrrencia))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista,20)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'ultimosAcompanhamentos.html', {'lista':lista, 'listTipoOcorrencia':listaTipoOcorrencia})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def updateSimPAEVS(request, id):
    return updatePAEVS(request, id, 'S')


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def updateNaoPAEVS(request, id):
    return updatePAEVS(request, id, 'N')


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def updatePAEVS(request, id, opcao):
    
    pessoa = get_object_or_404(Pessoa, id=id)
    info = InformacoesAlunos(aluno=pessoa,paevs=opcao)
    #info.aluno = pessoa
    #info.paevs = opcao
    info.save()

    return listAcompanhamentoPedagogico(request, id)


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAlunosComPaevs(request):
    lista = InformacoesAlunos.objects.filter(paevs="S")
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(aluno__nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista,20)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'listAlunosComPaevs.html', {'lista':lista})
    

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAlunosAtestado(request):
    listTipoOcorrencia = TipoOcorrencia.objects.all()
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    buscaDe = request.GET.get('dataDe')
    buscaAte = request.GET.get('dataAte')
    buscaTipoOcorrrencia = request.GET.get('tipoOcorrencia')
    detalhado = request.GET.get('detalhado')
    minimo = request.GET.get('minimo')

    imprimir = request.GET.get('imprimir')

    lista = None
    query_string = None

    if buscaDe and buscaAte :
        queryset = AcompanhamentoPedagogicoAluno.objects.filter(dataOcorrencia__range=(buscaDe, buscaAte))

        if buscaTipoOcorrrencia:
            queryset = queryset.filter(tipoOcorrencia__id=buscaTipoOcorrrencia)
       
        if detalhado != "S" :
            lista = queryset.values('aluno__nome', 'aluno__id').annotate(contagem=Count('aluno__nome')).order_by('aluno__nome')   
            if minimo:
                try:
                    minimo = int(minimo)
                    lista = lista.filter(contagem__gte=minimo)
                except (ValueError,TypeError):
                    pass
        else:
            lista = queryset.order_by('aluno__nome')


        '''
            Criando paginação
        '''
        #Mantendo a consulta para paginação
        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        if 'imprimir' in query_params:
            del query_params['imprimir']

        query_string = query_params.urlencode()

        if imprimir == 'S':
            tipo_ocorrencia_obj = None
            if buscaTipoOcorrrencia:
                try:
                    tipo_ocorrencia_obj = TipoOcorrencia.objects.get(id=buscaTipoOcorrrencia)
                except TipoOcorrencia.DoesNotExist:
                    pass

            context = {
                'lista': lista, # Envia a lista completa
                'detalhado': detalhado,
                'buscaDe': buscaDe,
                'buscaAte': buscaAte,
                'tipo_ocorrencia_obj': tipo_ocorrencia_obj,
                'minimo': minimo,
            }
            
            return render(request, 'relatorios/printAlunosAtestado.html', context)
        else: 
            paginas = Paginator(lista, 20)
            page = request.GET.get('page')
            lista_paginada = paginas.get_page(page)

            # 2. Renderiza o template original com a lista paginada
            return render(request, 'listAlunosAtestado.html', {
                'lista': lista_paginada, # Envia a lista PAGINADA
                'listTipoOcorrencia': listTipoOcorrencia, 
                'minimo': minimo, 
                'detalhado': detalhado, 
                'query_string': query_string
            })
    else:
        return render(request, 'listAlunosAtestado.html', {'listTipoOcorrencia':listTipoOcorrencia})
        


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def chartAcompanhamentoOcorrencia(request):
    listTipoOcorrencia = TipoOcorrencia.objects.all()

    ''' 
        Realizando a busca e filtrando na tabela
    '''
    tipoGrafico = request.GET.get('tipoGrafico')
    buscaDe = request.GET.get('dataDe')
    buscaAte = request.GET.get('dataAte')
    buscaTipoOcorrrencia = request.GET.get('tipoOcorrencia')
    
    if buscaDe and buscaAte :
        if tipoGrafico == "O":
            listAcompanhamentoPedagogico = AcompanhamentoPedagogicoAluno.objects.filter(dataOcorrencia__range=(buscaDe, buscaAte)).values('tipoOcorrencia').order_by('tipoOcorrencia').annotate(count=Count('tipoOcorrencia'))
            for acompanhamentoPedagogico in listAcompanhamentoPedagogico:
                to = TipoOcorrencia.objects.get(id=acompanhamentoPedagogico['tipoOcorrencia'])
                acompanhamentoPedagogico['tipoOcorrencia'] = to.nome 

            return render(request, 'chartAcompanhamento.html', {'lista':listAcompanhamentoPedagogico, 'listTipoOcorrencia':listTipoOcorrencia, 'tipoGrafico':tipoGrafico})
        elif tipoGrafico == "A":
            listaAtestado = {}
            dataDe = datetime.strptime(buscaDe, "%Y-%m-%d")
            dataAte = datetime.strptime(buscaAte, "%Y-%m-%d")
            while dataDe < dataAte:
                listAcompanhamentoPedagogico = AcompanhamentoPedagogicoAluno.objects.filter(dataAtestadoInicio__lte=dataDe, dataAtestadoFim__gte=dataDe, tipoOcorrencia__id__exact=buscaTipoOcorrrencia).values('tipoOcorrencia').order_by('tipoOcorrencia').annotate(count=Count('tipoOcorrencia'))    

                for ap in listAcompanhamentoPedagogico:  
                    listaAtestado[dataDe.strftime('%d/%m')] = ap['count']
                
                dataDe = dataDe + timedelta(days = 1)

            return render(request, 'chartAcompanhamento.html', {'listTipoOcorrencia':listTipoOcorrencia,'tipoGrafico':tipoGrafico, 'lista':listaAtestado})
    else:
        return render(request, 'chartAcompanhamento.html', {'listTipoOcorrencia':listTipoOcorrencia,'tipoGrafico':tipoGrafico})


@login_required(login_url="/login/")
def updateSimDeficiencia(request, id):
    info, _ = InformacoesAlunos.objects.get_or_create(aluno_id=id, defaults={'paevs': 'N'})
    info.deficiencia = 'S'
    info.save()
    return redirect('pedagogico:listAcompanhamentoPedagogico', id=id)

@login_required(login_url="/login/")
def updateNaoDeficiencia(request, id):
    info, _ = InformacoesAlunos.objects.get_or_create(aluno_id=id, defaults={'paevs': 'N'})
    info.deficiencia = 'N'
    info.save()
    return redirect('pedagogico:listAcompanhamentoPedagogico', id=id)

@login_required(login_url="/login/")
@permission_required(perm='pedagogico.delete_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def excluirAcompanhamentoPedagogico(request, id):
    acompanhamento = get_object_or_404(AcompanhamentoPedagogicoAluno, id=id)
    aluno_id = acompanhamento.aluno_id

    if request.method == "POST":
        motivo = request.POST.get('motivoExclusao', '').strip()
        if not motivo:
            messages.error(request, "É obrigatório informar o motivo da exclusão.")
            return redirect('pedagogico:listAcompanhamentoPedagogico', id=aluno_id)

        # Identifica a Pessoa associada ao usuário autenticado
        usuario_responsavel = getattr(request.user, 'pessoa', None)
        if not usuario_responsavel:
            usuario_responsavel = Pessoa.objects.filter(user=request.user).first()

        # Aplica o Soft Delete gravando quem excluiu, o motivo e a data
        acompanhamento.status = 'E'
        acompanhamento.motivoExclusao = motivo
        acompanhamento.excluidoPor = usuario_responsavel
        acompanhamento.dataExclusao = datetime.now()
        acompanhamento.save()

        messages.success(request, "Atendimento removido com sucesso!")
        return redirect('pedagogico:listAcompanhamentoPedagogico', id=aluno_id)

    return redirect('pedagogico:listAcompanhamentoPedagogico', id=aluno_id)


@login_required(login_url="/login/")
def listAlunosComDeficiencia(request):
    """
    Lista todos os alunos que possuem a flag de deficiência marcada como 'S',
    seguindo o mesmo modelo da listagem de alunos com PAEVS.
    """
    # 1. Busca os registros com deficiência ativa
    info_alunos = InformacoesAlunos.objects.filter(
        deficiencia='S'
    ).select_related('aluno').order_by('aluno__nome')

    alunos_ids = [item.aluno_id for item in info_alunos]

    # 2. Busca cursos/matrículas ativas desses alunos para exibir curso e período atual
    matriculas_ativas = Matricula.objects.filter(
        aluno_id__in=alunos_ids,
        status='A'
    ).select_related('unidadeCurricular__curso').order_by('periodo')

    # Agrupa cursos por aluno (evitando duplicações)
    cursos_por_aluno = {}
    for m in matriculas_ativas:
        if m.aluno_id not in cursos_por_aluno and m.unidadeCurricular and m.unidadeCurricular.curso:
            cursos_por_aluno[m.aluno_id] = {
                'curso': m.unidadeCurricular.curso.nome,
                'periodo': m.periodo
            }

    # 3. Monta a lista final para o template
    dados_alunos = []
    for info in info_alunos:
        aluno = info.aluno
        vinculo = cursos_por_aluno.get(aluno.id, {'curso': 'Sem matrícula ativa', 'periodo': '-'})
        dados_alunos.append({
            'aluno': aluno,
            'curso': vinculo['curso'],
            'periodo': vinculo['periodo'],
            'paevs': info.paevs,
        })

    return render(request, "listAlunosComNecessidades.html", {
        'dados_alunos': dados_alunos,
        'total': len(dados_alunos),
    })