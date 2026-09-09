from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PeriodoConselho, ConselhoClasse, ConselhoClasseAluno

@admin.register(PeriodoConselho)
class PeriodoConselhoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')

@admin.register(ConselhoClasse)
class ConselhoClasseAdmin(admin.ModelAdmin):
    list_display = ('id', 'turma', 'ano', 'periodoConselho', 'dataConselho', 'finalizado')
    list_filter = ('ano', 'periodoConselho', 'finalizado')