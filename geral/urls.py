from django.urls import path, re_path

from . import views
from .app import viewGrupoTrabalho

app_name="geral"

urlpatterns = [
    path('geral/listServidor', views.listServidor, name='listServidor'),
    path('geral/addServidor', views.addServidor, name='addServidor'),
    path('geral/updateServidor/<int:id>/', views.updateServidor, name='updateServidor'),
    path('geral/listGrupoTrabalho', viewGrupoTrabalho.listGrupoTrabalho, name='listGrupoTrabalho'),
    path('geral/addGrupoTrabalho', viewGrupoTrabalho.addGrupoTrabalho, name='addGrupoTrabalho'),
    path('geral/updateGrupoTrabalho/<int:id>/', viewGrupoTrabalho.updateGrupoTrabalho, name='updateGrupoTrabalho'),
    path('geral/participantesGrupoTrabalho/<int:id>/', viewGrupoTrabalho.listParticipantesGrupoTrabalho, name='listParticipantesGrupoTrabalho'),
    path('geral/addParticipantesGrupoTrabalho/<int:id>/', viewGrupoTrabalho.addParticipantesGrupoTrabalho, name='addParticipantesGrupoTrabalho'),
    path('geral/deleteParticipantesGrupoTrabalho/<int:grupoTrabalho>/<int:id>/', viewGrupoTrabalho.deleteParticipantesGrupoTrabalho, name='deleteParticipantesGrupoTrabalho'),
    path('geral/paginaSemPermissao', views.paginaSemPermissao, name='paginaSemPermissao'),
    path('logout/', views.user_logout, name='logout'),
]
