from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

from .views import (
    CustomLoginView, 
    ver_clientes, 
    agregar_reporte, 
    agregar_cliente, 
    ver_reportes, 
    editar_reporte, 
    dashboard, 
    editar_cliente, 
    calendario,
    CustomLogoutView,
    ActualizarPerfilView,
    ProfileUpdate
)
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy

# Utilizamos `never_cache` para la vista de cierre de sesión
urlpatterns = [
    # Autenticación
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdate.as_view(), name='profile'),


    path('dashboard/', login_required(dashboard), name='dashboard'),
    path('ver_clientes/', login_required(ver_clientes), name='ver_clientes'),
    path('agregar_cliente/', login_required(agregar_cliente), name='agregar_cliente'),  
    path('editar_cliente/<int:cliente_id>/', login_required(editar_cliente), name='editar_cliente'),
    path('agregar_reporte/<int:cliente_id>/', login_required(agregar_reporte), name='agregar_reporte'),
    path('ver_reportes/<int:cliente_id>/', login_required(ver_reportes), name='ver_reportes'),
    path('editar_reporte/<int:reporte_id>/', login_required(editar_reporte), name='editar_reporte'),
    path('calendario/', login_required(calendario), name='calendario'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
