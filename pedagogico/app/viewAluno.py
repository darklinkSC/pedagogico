from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from geral.models import TIPO_PESSOA_ALUNO
from geral.models import Pessoa
from pedagogico.models import Matricula
from django.db.models import Q
from pedagogico.app.formsAluno import AlunoForm, AlunoUpdateForm, MatriculaForm


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def listAluno(request):
    lista = Pessoa.objects.filter(tipoPessoa=TIPO_PESSOA_ALUNO)
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 20)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'alunos.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addAluno(request):
    form = AlunoForm()
    if(request.method == 'POST'):
        form = AlunoForm(request.POST, request.FILES)
        form.instance.tipoPessoa = "A"
        if(form.is_valid()):
            form.save()
            return redirect('/pedagogico/listAluno')


    return render(request, "addAluno.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def updateAluno(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    form = AlunoUpdateForm(instance=pessoa)

    if(request.method == 'POST'):
        form = AlunoUpdateForm(request.POST, request.FILES, instance=pessoa)
        if(form.is_valid()):
            pessoa = form.save(commit=False)
            form.save()
            return listAluno(request)   
    elif(request.method == 'GET'):
        return render(request, "updateAluno.html", {'form':form, 'pessoa': pessoa})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_acompanhamentopedagogicoaluno', login_url='/geral/paginaSemPermissao')
def addMatricula(request, id):
    form = MatriculaForm()
    aluno = get_object_or_404(Pessoa, id=id)

    lista = Matricula.objects.filter(aluno=aluno)

    if(request.method == 'POST'):
        form = MatriculaForm(request.POST)
        if(form.is_valid()):
            form.instance.aluno = aluno
            form.save()

            return redirect('/pedagogico/listAluno')
    elif(request.method == 'GET'):
        return render(request, "addMatricula.html", {'form':form,'aluno':aluno,'lista':lista})