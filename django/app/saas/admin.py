from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import User, Group

from .models import (
    AdminGroup,
    AdminUser,
    Module,
    Project,
    ProjectModule,
    Membership,
    ProjectRole,
    Invite,
)

# 1) Quitar la sección por defecto “Autenticación y autorización”
for m in (User, Group):
    try:
        admin.site.unregister(m)
    except admin.sites.NotRegistered:
        pass

# 2) Evitar duplicados si el servidor recarga
for m in (AdminUser, AdminGroup):
    try:
        admin.site.unregister(m)
    except admin.sites.NotRegistered:
        pass

# 3) Registrar proxies en el apartado SAAS
@admin.register(AdminGroup)
class AdminGroupAdmin(DjangoGroupAdmin):
    pass

@admin.register(AdminUser)
class AdminUserAdmin(UserAdmin):
    pass


class ProjectModuleInline(admin.TabularInline):
    model = ProjectModule
    extra = 0
    autocomplete_fields = ["module"]
    fields = ("module", "enabled")
    show_change_link = True


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    raw_id_fields = ("user",)
    fields = ("user", "role", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectModuleInline, MembershipInline]
    list_display = ("name", "slug", "members_count")
    search_fields = (
        "name",
        "slug",
        "memberships__user__username",
        "memberships__user__email",
    )
    ordering = ("name",)

    def members_count(self, obj):
        return obj.memberships.count()
    members_count.short_description = "Miembros"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(ProjectModule)
class ProjectModuleAdmin(admin.ModelAdmin):
    list_display = ("project", "module", "enabled")
    autocomplete_fields = ["project", "module"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "created_at")
    search_fields = ("project__name", "user__username", "user__email")
    raw_id_fields = ("project", "user")
    date_hierarchy = "created_at"


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ("project", "email", "user", "role", "accepted", "created_at")
    search_fields = ("project__name", "email", "user__username", "user__email", "token")
    raw_id_fields = ("project", "user")
    list_filter = ("accepted", "role")
    readonly_fields = ("created_at",)
