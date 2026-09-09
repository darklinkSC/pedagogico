from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from pedagogico.models import UnidadeCurricular
from django.db.models import Q
from pedagogico.app.formsUnidadeCurricular import UnidadeCurricularForm


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_unidadecurricular', login_url='/geral/paginaSemPermissao')
def listUnidadeCurricular(request):
    lista = UnidadeCurricular.objects.all()
    
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

    return render(request, 'unidadeCurricular.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_unidadecurricular', login_url='/geral/paginaSemPermissao')
def addUnidadeCurricular(request):
    form = UnidadeCurricularForm()
    if(request.method == 'POST'):
        form = UnidadeCurricularForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/pedagogico/listUnidadeCurricular')        
    elif(request.method == 'GET'):
        return render(request, "addUnidadeCurricular.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_unidadecurricular', login_url='/geral/paginaSemPermissao')
def updateUnidadeCurricular(request, id):
    unidadeCurricular = get_object_or_404(UnidadeCurricular, id=id)
    form = UnidadeCurricularForm(instance=unidadeCurricular)
    
    if(request.method == 'POST'):
        form = UnidadeCurricularForm(request.POST, instance=unidadeCurricular)
        if(form.is_valid()):
            unidadeCurricular = form.save(commit=False)
            form.save()
            return redirect('/pedagogico/listUnidadeCurricular')   
    elif(request.method == 'GET'):
        return render(request, "updateUnidadeCurricular.html", {'form':form, 'unidadeCurricular': unidadeCurricular})    


    

    