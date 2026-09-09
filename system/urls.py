from django.urls import path

from . import views

app_name="system"

urlpatterns = [
    path('', views.index, name='index'),
    path('system/usuario/', views.usuario, name='usuario'),
]
