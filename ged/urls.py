from django.urls import path, re_path

from . import views
from .app import viewLocal 
from .app import viewRegistros

app_name="ged"

urlpatterns = [
    #### TIPO DE OCORRENCIA ####
    path('ged/listLocal/', viewLocal.listLocal, name='listLocal'),
    path('ged/addLocal/', viewLocal.addLocal, name='addLocal'),
    path('ged/updateLocal/<int:id>', viewLocal.updateLocal, name='updateLocal'),
    #### SISTEMA DE REGISTROS ####
    path('ged/listGTRegistros/', viewRegistros.listGrupoTrabalho, name='listGTRegistros'),   
    path('ged/listRegistros/<int:id>', viewRegistros.listRegistros, name='listRegistros'),   
    path('ged/addRegistro/<int:id>', viewRegistros.addRegistro, name='addRegistro'),   
]
