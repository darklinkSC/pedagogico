from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from pedagogico.models import TipoOcorrencia
from django.db.models import Q
from pedagogico.app.formsTipoOcorrencia import TipoOcorrenciaForm


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_tipoocorrencia', login_url='/geral/paginaSemPermissao')
def listTipoOcorrencia(request):
    lista = TipoOcorrencia.objects.all()
    
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

    return render(request, 'tipoOcorrencia.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_tipoocorrencia', login_url='/geral/paginaSemPermissao')
def addTipoOcorrencia(request):
    form = TipoOcorrenciaForm()
    if(request.method == 'POST'):
        form = TipoOcorrenciaForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/pedagogico/listTipoOcorrencia')     
    elif(request.method == 'GET'):
        return render(request, "addTipoOcorrencia.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_tipoocorrencia', login_url='/geral/paginaSemPermissao')
def updateTipoOcorrencia(request, id):
    tipoOcorrencia = get_object_or_404(TipoOcorrencia, id=id)
    form = TipoOcorrenciaForm(instance=tipoOcorrencia)
    
    if(request.method == 'POST'):
        form = TipoOcorrenciaForm(request.POST, instance=tipoOcorrencia)
        if(form.is_valid()):
            tipoOcorrencia = form.save(commit=False)
            form.save()
            return redirect('/pedagogico/listTipoOcorrencia')  
    elif(request.method == 'GET'):
        return render(request, "updateTipoOcorrencia.html", {'form':form, 'tipoOcorrencia': tipoOcorrencia})    


    

    