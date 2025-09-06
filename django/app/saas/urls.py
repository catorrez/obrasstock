# saas/urls.py
from django.urls import path
from . import views as saas_views  # import "eager" solo para rutas que ya funcionan

def join_project_lazy(request, token, *args, **kwargs):
    # Lazy import para evitar ImportError/ciclos al arrancar
    from .views import join_project
    return join_project(request, token, *args, **kwargs)

urlpatterns = [
    # TUS RUTAS EXISTENTES
    path("p/<slug:project_slug>/", saas_views.project_home, name="project_home"),
    path("p/<slug:project_slug>/modules/<slug:code>/toggle/", saas_views.toggle_module, name="toggle_module"),
    path("p/<slug:project_slug>/invites/new/", saas_views.create_invite, name="create_invite"),

    # NUEVA RUTA CON LAZY IMPORT
    path("join/<uuid:token>/", join_project_lazy, name="join_project"),
    # Si el token no es UUID en DB, usa esta en su lugar:
    # path("join/<slug:token>/", join_project_lazy, name="join_project"),
]