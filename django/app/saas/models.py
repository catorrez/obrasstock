from django.db import models
from django.contrib.auth.models import User, Group


class Module(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ("code",)

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ProjectModule(models.Model):
    project = models.ForeignKey(Project, related_name="project_modules", on_delete=models.CASCADE)
    module  = models.ForeignKey(Module,  related_name="project_modules", on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project module"
        verbose_name_plural = "Project modules"
        unique_together = (("project", "module"),)

    def __str__(self) -> str:
        return f"{self.project} · {self.module}"


class ProjectRole(models.IntegerChoices):
    VIEWER = 10, "viewer"
    EDITOR = 20, "editor"
    ADMIN  = 30, "admin"
    OWNER  = 40, "owner"


class Membership(models.Model):
    project = models.ForeignKey(Project, related_name="memberships", on_delete=models.CASCADE)
    user    = models.ForeignKey(User,    related_name="project_memberships", on_delete=models.CASCADE)
    role    = models.PositiveSmallIntegerField(choices=ProjectRole.choices, default=ProjectRole.VIEWER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
        unique_together = (("project", "user"),)
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.user} → {self.project} ({self.get_role_display()})"


class Invite(models.Model):
    """Invitaciones a un proyecto (lo usan las vistas)."""
    project = models.ForeignKey(Project, related_name="invites", on_delete=models.CASCADE)
    # Se puede invitar por email o asociar a un usuario existente
    email   = models.EmailField(blank=True, null=True)
    user    = models.ForeignKey(User, related_name="project_invites", on_delete=models.SET_NULL, blank=True, null=True)
    token   = models.CharField(max_length=64, unique=True)
    role    = models.PositiveSmallIntegerField(choices=ProjectRole.choices, default=ProjectRole.VIEWER)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        who = self.email or (self.user and self.user.username) or "invite"
        return f"{who} → {self.project} ({self.get_role_display()})"


# Proxies para mover “Usuarios” y “Grupos” a SAAS en el admin
class AdminUser(User):
    class Meta:
        proxy = True
        app_label = "saas"
        verbose_name = "Usuarios (admin)"
        verbose_name_plural = "Usuarios (admin)"


class AdminGroup(Group):
    class Meta:
        proxy = True
        app_label = "saas"
        verbose_name = "Grupos (admin)"
        verbose_name_plural = "Grupos (admin)"
