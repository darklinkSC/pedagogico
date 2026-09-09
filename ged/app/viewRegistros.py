from ged.app.formsRegistros import RegistroForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from geral.models import GrupoTrabalho, Pessoa, ParticipantesGrupoTrabalho
from ged.models import Registro, Marcador
 

######
# FORM GRUPO DE TRABALHO
######
@login_required(login_url="/login/")
@permission_required(perm='ged.view_registro', login_url='/geral/paginaSemPermissao')
def listGrupoTrabalho(request):
    
    lista = GrupoTrabalho.objects.all()
    
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

    return render(request, 'listGrupoTrabalhoRegistros.html', {'lista':lista})



######
# FORM REGISTRO
######
@login_required(login_url="/login/")
@permission_required(perm='ged.view_registro', login_url='/geral/paginaSemPermissao')
def listRegistros(request, id):
    ### Pegando registro do Grupo de Trabalho
    grupoTrabalho = get_object_or_404(GrupoTrabalho, id=id)
    lista = Registro.objects.filter(grupoTrabalho=grupoTrabalho)
    
    print("Lista",lista)

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 10)
    page = request.GET.get('page')
    lista = paginas.get_page(page)

    ### Participantes do GT
    participantes = ParticipantesGrupoTrabalho.objects.filter(grupoTrabalho=grupoTrabalho)

    ### Marcadores do GT
    marcadores = Marcador.objects.filter(grupoTrabalho=grupoTrabalho)

    return render(request, 'listRegistros.html', {'grupoTrabalho':grupoTrabalho , 'lista':lista, 'participantes':participantes, 'marcadores':marcadores})


@login_required(login_url="/login/")
@permission_required(perm='ged.view_registro', login_url='/geral/paginaSemPermissao')
def addRegistro(request, id):
    grupoTrabalho  = get_object_or_404(GrupoTrabalho, id=id)
    form = RegistroForm()
    if(request.method == 'POST'):
        form = RegistroForm(request.POST)
        if(form.is_valid()):
            user = request.user 
            criador = get_object_or_404(Pessoa,user=user)
            
            form.instance.usuarioCriacao = criador
            form.instance.grupoTrabalho = grupoTrabalho
            
            form.save()
            return listRegistros(request, id)     
    elif(request.method == 'GET'):
        return render(request, "addRegistro.html", {'form':form,'grupoTrabalho':grupoTrabalho})