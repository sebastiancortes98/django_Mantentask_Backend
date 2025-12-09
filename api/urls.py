from django.urls import path, include
from rest_framework import routers
from .views import (
    TipoUsuarioViewSet, NivelAccesoViewSet, SucursalViewSet,
    UsuarioViewSet, EstadoViewSet, MaquinaViewSet,
    SolicitudViewSet, InformeViewSet, TaskViewSet
)

# Router para endpoints REST
router = routers.DefaultRouter()
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipo-usuario')
router.register(r'niveles-acceso', NivelAccesoViewSet, basename='nivel-acceso')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'estados', EstadoViewSet, basename='estado')
router.register(r'maquinas', MaquinaViewSet, basename='maquina')
router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')
router.register(r'informes', InformeViewSet, basename='informe')

# Endpoint legacy
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
