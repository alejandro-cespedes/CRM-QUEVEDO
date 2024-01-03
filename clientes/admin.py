from django.contrib import admin
from .models import Cliente, Reporte, Asesor, Coordinador

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'dni', 'celular', 'origen_del_prospecto', 'asesor_coordinador', 'seguimiento')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'descripcion', 'fecha_de_creacion', 'fecha_de_actualizacion')

@admin.register(Asesor)
class AsesorAdmin(admin.ModelAdmin):
    list_display = ('usuario','grupo_coordinador')

@admin.register(Coordinador)
class CoordinadorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'es_asesor')
