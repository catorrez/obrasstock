# saas/admin.py
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .models import (
    Project, Module, ProjectModule, Membership, ProjectRole,
    # proxies definidos en models.py
    AdminUser, AdminGroup,
)

# ------------------------------
#  Mantener User/Group registrados (para autocompletes)
#  pero ocultos del dashboard
# ------------------------------
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class HiddenUserAdmin(UserAdmin):
    """Necesario para autocompletes; se oculta en el index."""
    def has_module_permission(self, request):
        return False


@admin.register(Group)
class HiddenGroupAdmin(GroupAdmin):
    """Necesario para permisos; se oculta en el index."""
    def has_module_permission(self, request):
        return False


# ------------------------------
#  Proxies visibles bajo SAAS
# ------------------------------
admin.site.register(AdminUser, UserAdmin)
admin.site.register(AdminGroup, GroupAdmin)


# ========= helpers de permisos (grupos) =========
ALLOWED_GROUPS = ("GodAdmin", "SuperAdmin")

def user_is_platform_admin(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()


# ========= INLINES =========
class ProjectModuleInline(admin.TabularInline):
    model = ProjectModule
    extra = 0
    autocomplete_fields = ["module"]
    fields = ("module", "enabled")
    show_change_link = True


class MembershipInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        owners = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            if not form.cleaned_data:
                continue
            role = form.cleaned_data.get("role")
            if role is None and form.instance.pk:
                role = form.instance.role
            if role == ProjectRole.OWNER:
                owners += 1
        if owners == 0:
            raise ValidationError("Debe existir al menos un OWNER en el proyecto.")


class MembershipInline(admin.TabularInline):
    model = Membership
    formset = MembershipInlineFormSet
    extra = 0
    autocomplete_fields = ["user"]
    fields = ("user", "role", "created_at")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request, obj=None):
        return user_is_platform_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return user_is_platform_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return user_is_platform_admin(request.user)


# ========= ADMINS =========
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectModuleInline, MembershipInline]

    list_display = ("name", "slug", "owners_display", "modules_enabled_display", "members_count")
    search_fields = ("name", "slug", "memberships__user__username", "memberships__user__email")
    ordering = ("name",)

    def members_count(self, obj):
        return obj.memberships.count()
    members_count.short_description = "Miembros"

    def owners_display(self, obj):
        owners = obj.memberships.filter(role=ProjectRole.OWNER).select_related("user")
        return ", ".join(m.user.username for m in owners)
    owners_display.short_description = "Owners"

    def modules_enabled_display(self, obj):
        qs = obj.project_modules.filter(enabled=True).select_related("module")
        return ", ".join(pm.module.name for pm in qs)
    modules_enabled_display.short_description = "Módulos ON"

    def has_module_permission(self, request):
        return request.user.is_authenticated

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        return user_is_platform_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return user_is_platform_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return user_is_platform_admin(request.user)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(ProjectModule)
class ProjectModuleAdmin(admin.ModelAdmin):
    list_display = ("project", "module", "enabled")
    autocomplete_fields = ["project", "module"]

    def has_module_permission(self, request):
        return False


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "created_at")
    search_fields = ("project__name", "user__username", "user__email")
    autocomplete_fields = ["project", "user"]

    def has_module_permission(self, request):
        return False
