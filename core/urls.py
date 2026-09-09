# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("app.urls")),            # UI Kits Html files
    path("", include("system.urls")),         # Sistema para adiministracao pelo ADMIN
    path("", include("geral.urls", namespace='geral')), #Cadastros Gerais
    path("", include("ged.urls", namespace='ged')), #Sistema de Registros
    path("", include("pedagogico.urls", namespace='pedagogico')) #Sistema pedagogico
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
