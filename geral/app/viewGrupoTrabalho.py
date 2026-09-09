from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from geral.app.formGrupoTrabalho import GrupoTrabalhoForm, ParticipantesGrupoTrabalhoForm
from geral.models import GrupoTrabalho, Pessoa, ParticipantesGrupoTrabalho


######
# FORM GRUPO DE TRABALHO
######
@login_required(login_url="/login/")
@permission_required(perm='geral.view_grupotrabalho', login_url='/geral/paginaSemPermissao')
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

    return render(request, 'grupoTrabalho.html', {'lista':lista})


@login_required(login_url="/login/")
@permission_required(perm='geral.add_grupotrabalho', login_url='/geral/paginaSemPermissao')
def addGrupoTrabalho(request):
    form = GrupoTrabalhoForm()
    if(request.method == 'POST'):
        form = GrupoTrabalhoForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/geral/listGrupoTrabalho')        
    elif(request.method == 'GET'):
        return render(request, "addGrupoTrabalho.html", {'form':form})    


@login_required(login_url="/login/")
@permission_required(perm='geral.change_grupotrabalho', login_url='/geral/paginaSemPermissao')
def updateGrupoTrabalho(request, id):
    grupoTrabalho = get_object_or_404(GrupoTrabalho, id=id)
    form = GrupoTrabalhoForm(instance=grupoTrabalho)
    
    if(request.method == 'POST'):
        form = GrupoTrabalhoForm(request.POST, instance=grupoTrabalho)
        if(form.is_valid()):
            grupoTrabalho = form.save(commit=False)
            form.save()
            return redirect('/geral/listGrupoTrabalho')   
    elif(request.method == 'GET'):
        return render(request, "updateGrupoTrabalho.html", {'form':form, 'grupoTrabalho': grupoTrabalho})    

######
# FORM PARTICIPANTES GRUPO TRABALHO
######
@login_required(login_url="/login/")
@permission_required(perm='geral.view_participantesgrupotrabalho', login_url='/geral/paginaSemPermissao')
def listParticipantesGrupoTrabalho(request, id):
    grupoTrabalho = get_object_or_404(GrupoTrabalho, id=id)
    lista = ParticipantesGrupoTrabalho.objects.filter(grupoTrabalho=grupoTrabalho)
    form = ParticipantesGrupoTrabalhoForm()

    '''
        Criando paginação
    '''
    paginas = Paginator(lista, 5)
    page = request.GET.get('page')
    lista = paginas.get_page(page)  

    return render(request, 'participantesGrupoTrabalho.html', {'lista':lista, 'form':form, 'grupoTrabalho':grupoTrabalho})

@login_required(login_url="/login/")
@permission_required(perm='geral.add_participantesgrupotrabalho', login_url='/geral/paginaSemPermissao')
def addParticipantesGrupoTrabalho(request, id):
    form = ParticipantesGrupoTrabalhoForm()
    if(request.method == 'POST'):
        grupoTrabalho = get_object_or_404(GrupoTrabalho, id=id)
        form = ParticipantesGrupoTrabalhoForm(request.POST)
        form.instance.grupoTrabalho = grupoTrabalho
        if(form.is_valid()):
            try:
                form.save()
                return listParticipantesGrupoTrabalho(request, id)
            except:
                return listParticipantesGrupoTrabalho(request, id)    
        else:
            return render(request, "participantesGrupoTrabalho.html")      
    elif(request.method == 'GET'):
        return render(request, "participantesGrupoTrabalho.html")


@login_required(login_url="/login/")
@permission_required(perm='geral.delete_participantesgrupotrabalho', login_url='/geral/paginaSemPermissao')
def deleteParticipantesGrupoTrabalho(request, grupoTrabalho, id):
    participante = get_object_or_404(ParticipantesGrupoTrabalho, id=id)
    participante.delete()
    return listParticipantesGrupoTrabalho(request, grupoTrabalho)