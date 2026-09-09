from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from ged.models import Local
from django.db.models import Q
from ged.app.formsLocal import LocalForm


@login_required(login_url="/login/")
@permission_required(perm='ged.view_local', login_url='/geral/paginaSemPermissao')
def listLocal(request):
    lista = Local.objects.all()
    
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

    return render(request, 'listLocal.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='ged.view_local', login_url='/geral/paginaSemPermissao')
def addLocal(request):
    form = LocalForm()
    if(request.method == 'POST'):
        form = LocalForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/ged/listLocal')     
    elif(request.method == 'GET'):
        return render(request, "addLocal.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='ged.view_local', login_url='/geral/paginaSemPermissao')
def updateLocal(request, id):
    local = get_object_or_404(Local, id=id)
    form = LocalForm(instance=local)
    
    if(request.method == 'POST'):
        form = LocalForm(request.POST, instance=local)
        if(form.is_valid()):
            local = form.save(commit=False)
            form.save()
            return redirect('/ged/listLocal')  
    elif(request.method == 'GET'):
        return render(request, "updateLocal.html", {'form':form, 'local': local})    


    

    