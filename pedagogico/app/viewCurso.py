from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from pedagogico.models import Curso
from django.db.models import Q
from pedagogico.app.formsCurso import CursoForm


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_curso', login_url='/geral/paginaSemPermissao')
def listCurso(request):
    lista = Curso.objects.all()
    
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

    return render(request, 'curso.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_curso', login_url='/geral/paginaSemPermissao')
def addCurso(request):
    form = CursoForm()
    if(request.method == 'POST'):
        form = CursoForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/pedagogico/listCurso')        
    elif(request.method == 'GET'):
        return render(request, "addCurso.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='pedagogico.view_curso', login_url='/geral/paginaSemPermissao')
def updateCurso(request, id):
    curso = get_object_or_404(Curso, id=id)
    form = CursoForm(instance=curso)
    
    if(request.method == 'POST'):
        form = CursoForm(request.POST, instance=curso)
        if(form.is_valid()):
            curso = form.save(commit=False)
            form.save()
            return redirect('/pedagogico/listCurso')   
    elif(request.method == 'GET'):
        return render(request, "updateCurso.html", {'form':form, 'curso': curso})    


    

    