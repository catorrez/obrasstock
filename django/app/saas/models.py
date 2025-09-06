from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from .models import Project, Module, ProjectModule, Membership, ProjectRole
from .models import AdminUser, AdminGroup  # <— los proxies

# 1) Quitar los User/Group originales para que NO aparezcan en “Autenticación y autorización”
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# 2) Registrar los proxies bajo la app “saas” (quedarán en la sección SAAS)
@admin.register(AdminUser)
class AdminUserProxyAdmin(UserAdmin):
    # puedes personalizar list_display, search_fields, etc. si quieres
    pass

@admin.register(AdminGroup)
class AdminGroupProxyAdmin(GroupAdmin):
    pass

# 3) Resto de tus admins (asegúrate de NO bloquearlos con has_module_permission=False)
class ProjectModuleInline(admin.TabularInline):
    model = ProjectModule
    extra = 0
    autocomplete_fields = ["module"]
    fields = ("module", "enabled")
    show_change_link = True

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    autocomplete_fields = ["user"]
    fields = ("user", "role", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectModuleInline, MembershipInline]
    list_display = ("name", "slug")
    search_fields = ("name", "slug")

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")

# Estos dos se gestionan como auxiliares; si no quieres que aparezcan en el menú, ocúltalos:
@admin.register(ProjectModule)
class ProjectModuleAdmin(admin.ModelAdmin):
    list_display = ("project", "module", "enabled")
    autocomplete_fields = ["project", "module"]
    def has_module_permission(self, request):
        return False  # se administran desde el inline en Project

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "created_at")
    search_fields = ("project__name", "user__username", "user__email")
    autocomplete_fields = ["project", "user"]
    def has_module_permission(self, request):
        return False  # se administran desde el inline en Project
