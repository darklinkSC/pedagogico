from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from .models import TIPO_PESSOA_SERVIDOR
from .models import Pessoa
from .forms import ServidorForm
from django.db.models import Q

def index(request):
    return request


@login_required(login_url="/login/")
@permission_required(perm='geral.view_servidor', login_url='/geral/paginaSemPermissao')
def listServidor(request):
    lista = Pessoa.objects.filter(tipoPessoa=TIPO_PESSOA_SERVIDOR)
    
    ''' 
        Realizando a busca e filtrando na tabela
    '''
    busca = request.GET.get('search')
    if busca:
        lista = lista.filter(Q(nome__icontains = busca))

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 5)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'servidores.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='geral.add_servidor', login_url='/geral/paginaSemPermissao')
def addServidor(request):
    form = ServidorForm()
    if(request.method == 'POST'):
        form = ServidorForm(request.POST)
        form.instance.tipoPessoa = 'S' #SERVIDOR
        if(form.is_valid()):
            form.save()
            return redirect('/geral/listServidor')        
    elif(request.method == 'GET'):
        return render(request, "addServidor.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='geral.change_servidor', login_url='/geral/paginaSemPermissao')
def updateServidor(request, id):
    pessoa = get_object_or_404(Pessoa, id=id)
    form = ServidorForm(instance=pessoa)
    
    if(request.method == 'POST'):
        form = ServidorForm(request.POST, instance=pessoa)
        if(form.is_valid()):
            pessoa = form.save(commit=False)
            form.save()
            return redirect('/geral/listServidor')   
    elif(request.method == 'GET'):
        return render(request, "updateServidor.html", {'form':form, 'pessoa': pessoa})    


@login_required(login_url="/login/")
def paginaSemPermissao(request):
    return render(request, "paginaSemPermissao.html")    

