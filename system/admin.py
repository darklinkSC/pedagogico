from django.contrib import admin

# Register your models here.
from .models import Estado, Cidade, Campus, Sistema, Pais

class EstadoAdmin(admin.ModelAdmin):
    fields = ['nome','sigla','pais']

class CidadeAdmin(admin.ModelAdmin):
    fields = ['nome','ddd','estado']

class CampusAdmin(admin.ModelAdmin):
    fields = ['nome','cidade']


admin.site.register(Pais)
admin.site.register(Estado,EstadoAdmin)
admin.site.register(Cidade,CidadeAdmin)
admin.site.register(Campus,CampusAdmin)
admin.site.register(Sistema)
