from collections import Counter
from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import login, logout

from django.contrib.auth.views import LoginView

from clientes.forms import ClienteForm, ReporteForm, CustomAuthenticationForm, DateSelectForm
from .models import Cliente, Reporte, Asesor, Coordinador, Profile
from django.contrib.auth.models import Group, User
from django.db.models import Count, Q, Sum

from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
# Crear grupo para asesores
grupo_asesores, creado = Group.objects.get_or_create(name='Asesores')

# Crear grupo para coordinadores
grupo_coordinadores, creado = Group.objects.get_or_create(name='Coordinadores')

# Asignar asesores a su grupo
grupo_asesores.user_set.set(Asesor.objects.all().values_list('usuario', flat=True))

# Asignar coordinadores a su grupo
grupo_coordinadores.user_set.set(Coordinador.objects.all().values_list('usuario', flat=True))

# AUTENTICACION
@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    model = Profile
    fields = ['avatar']
    success_url = reverse_lazy('profile')
    template_name = 'registration/profile_form.html'

    def get_object(self):
        # Recuperar el objeto que sea va editar
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name='dispatch')
class ActualizarPerfilView(View):
    template_name = 'actualizar_perfil.html'
    form_class = UserChangeForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form})

def login_view(request):
    # Tu lógica de manejo del formulario aquí

    # Después de procesar el formulario
    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    else:
        # Si no hay una URL específica, redirige al dashboard u otra ruta
        return redirect('dashboard')
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Llama a la implementación original de dispatch
        response = super().dispatch(request, *args, **kwargs)

        # Hacer tus propias acciones después del cierre de sesión
        logout(request)
        return redirect('login')

    def get_next_page(self):
        next_page = super().get_next_page()
        return next_page or reverse_lazy('login')

# DASHBOARD
@login_required
def dashboard(request):

    ICONOS_SEGUIMIENTO = {
    'informacion_enviada': 'bi bi-info-circle',
    'en_negociacion': 'bi bi-handshake',
    'pendiente_por_llamar': 'bi bi-telephone',
    'no_contesta': 'bi bi-phone-missed',
    'no_interesado': 'bi bi-x-octagon',
    'por_enviar_deposito': 'bi bi-currency-dollar',
    'venta_exitoso': 'bi bi-check-circle',
}

    fecha_actual = timezone.now()
    hace_una_semana = fecha_actual - timedelta(days=7)

    total_clientes = Cliente.objects.filter(
        fecha_de_creacion__gte=hace_una_semana
    ).count()

    total_reportes = Reporte.objects.filter(
        fecha_de_creacion__gte=hace_una_semana
    ).count()

    clientes_publicidad_exitoso = Cliente.objects.filter(
        origen_del_prospecto='publicidad_pagada',
        seguimiento='venta_exitoso',
        fecha_de_creacion__gte=hace_una_semana
    ).count()

    # Calcula el porcentaje de clientes (excluyendo exitosos)
    porcentaje_clientes = 0
    if total_clientes > 0:
        porcentaje_clientes = int(((total_clientes - clientes_publicidad_exitoso) / total_clientes) * 100)

    # Calcula el porcentaje de clientes cerrados exitosos
    porcentaje_clientes_cerrados_exitosos = 0
    if total_clientes > 0:
        porcentaje_clientes_cerrados_exitosos = int((clientes_publicidad_exitoso / total_clientes) * 100)

    # Calcula el porcentaje de reportes
    porcentaje_reportes = 0
    if total_clientes > 0:
        porcentaje_reportes = int((total_reportes / total_clientes) * 100)

    # TOTAL USUARIOS
    total_usuarios = User.objects.exclude(asesor__isnull=False, coordinador__isnull=False, is_staff=True).count()

    # Obtener información de asesores y coordinadores con la cantidad de ventas exitosas
    asesores = Asesor.objects.annotate(num_ventas_exitosas=Count('usuario__cliente', filter=Q(usuario__cliente__seguimiento='venta_exitoso')))
    coordinadores = Coordinador.objects.annotate(num_ventas_exitosas=Count('asesores__usuario__cliente', filter=Q(asesores__usuario__cliente__seguimiento='venta_exitoso')))

    total_ventas_exitosas = Cliente.objects.filter(seguimiento='venta_exitoso').count()

    # Ordenar asesores y coordinadores por la cantidad de ventas exitosas (de mayor a menor)
    asesores = sorted(asesores, key=lambda a: a.num_ventas_exitosas, reverse=True)
    coordinadores = sorted(coordinadores, key=lambda c: c.num_ventas_exitosas, reverse=True)

   # SEGUIMIENTO
    seguimiento_choices = Cliente.SEGUIMIENTO_CHOICES

    # Calcula los porcentajes y las cantidades de seguimiento
    porcentajes_seguimiento = []
    cantidades_seguimiento = []

    for opcion in Cliente.SEGUIMIENTO_CHOICES:
        cantidad_clientes_con_opcion = Cliente.objects.filter(
            seguimiento=opcion[0],
            fecha_de_creacion__gte=hace_una_semana
        ).count()
        
        cantidades_seguimiento.append(cantidad_clientes_con_opcion)

        porcentaje = 0
        if total_clientes > 0:
            porcentaje = int((cantidad_clientes_con_opcion / total_clientes) * 100)
        
        porcentajes_seguimiento.append(porcentaje)


    # ORIGEN DEL PROSPECTO
    origen_choices = Cliente.ORIGEN_CHOICES

    # Calcula las cantidades de origen
    cantidades_origen = []
    for opcion in Cliente.ORIGEN_CHOICES:
        cantidad_clientes_con_opcion = Cliente.objects.filter(
            origen_del_prospecto=opcion[0],
            fecha_de_creacion__gte=hace_una_semana
        ).count()
        cantidades_origen.append(cantidad_clientes_con_opcion)

    return render(request, 'dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_reportes': total_reportes,
        'clientes_publicidad_exitoso': clientes_publicidad_exitoso,
        'porcentaje_clientes_cerrados_exitosos': porcentaje_clientes_cerrados_exitosos,
        'porcentaje_reportes': porcentaje_reportes,
        'porcentaje_clientes': porcentaje_clientes,
        'total_ventas_exitosas': total_ventas_exitosas,
        'asesores': asesores,
        'coordinadores': coordinadores,
        'seguimiento_choices': seguimiento_choices,
        'porcentajes_seguimiento': porcentajes_seguimiento,
        'cantidades_seguimiento': cantidades_seguimiento,
        'iconos_seguimiento': ICONOS_SEGUIMIENTO,
        'origen_choices': origen_choices,
        'cantidades_origen': cantidades_origen,
    })
# CLIENTES
@login_required
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    else:
        form = ClienteForm(user=request.user)

    return render(request, 'agregar_cliente.html', {'form': form})
@login_required
def ver_clientes(request):
    usuario = request.user

    if usuario.groups.filter(name='Coordinadores').exists():
        # Usuario es coordinador
        coordinador = Coordinador.objects.get(usuario=usuario)
        if coordinador.es_asesor:
            # Si el coordinador también es un asesor, mostrar sus propios clientes
            clientes = Cliente.objects.filter(asesor_coordinador=usuario)
        else:
            # Si solo es coordinador, mostrar clientes de sus asesores y de él mismo
            clientes = Cliente.objects.filter(
                Q(asesor_coordinador__in=coordinador.asesores.all()) |
                Q(asesor_coordinador=usuario)
            ).distinct()
    elif usuario.groups.filter(name='Asesores').exists():
        # Usuario es asesor
        clientes = Cliente.objects.filter(asesor_coordinador=usuario)
    else:
        # Usuario es administrador
        clientes = Cliente.objects.all()

    return render(request, 'ver_clientes.html', {'clientes': clientes})

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('ver_clientes')
    else:
        form = ClienteForm(instance=cliente, user=request.user)

    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})

# REPORTES

@login_required
def agregar_reporte(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '')
        reporte = Reporte(cliente=cliente, descripcion=descripcion)
        reporte.save()

    return redirect('ver_clientes')


# Reportes

@login_required
def agregar_reporte(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)

    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.cliente = cliente
            reporte.save()
            return redirect('ver_reportes', cliente_id=cliente.id)
    else:
        form = ReporteForm()

    return render(request, 'agregar_reporte.html', {'form': form, 'cliente': cliente})

@login_required
def editar_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, pk=reporte_id)
    cliente = reporte.cliente
    
    if request.method == 'POST':
        form = ReporteForm(request.POST, instance=reporte)
        if form.is_valid():
            form.save()
            return redirect('ver_reportes', cliente_id=cliente.id)
    else:
        form = ReporteForm(instance=reporte)

    return render(request, 'editar_reporte.html', {'form': form, 'cliente': cliente, 'reporte': reporte})
@login_required
def ver_reportes(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    reportes = Reporte.objects.filter(cliente=cliente)
    return render(request, 'ver_reportes.html', {'cliente': cliente, 'reportes': reportes})


# FUNCIONES EXTRAS

def calendario(request):
    if request.method == 'POST':
        form = DateSelectForm(request.POST)
        if form.is_valid():
            fecha_seleccionada = form.cleaned_data['fecha']
            # Aquí puedes agregar la lógica para obtener eventos en la fecha seleccionada
            # Por ahora, simplemente mostraré la fecha seleccionada
            return render(request, 'calendario.html', {'form': form, 'fecha_seleccionada': fecha_seleccionada})
    else:
        form = DateSelectForm()

    return render(request, 'calendario.html', {'form': form})