from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, Proyecto, RegistroFichaje


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "avatar_preview",
    )


    fieldsets = UserAdmin.fieldsets + (
        ("Campos adicionales", {"fields": ("avatar", "role", "phone_number")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Campos adicionales", {"fields": ("avatar", "role", "phone_number")}),
    )


    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" style="height:40px; border-radius:50%;" />'
            )
        return "—"

    avatar_preview.short_description = "Avatar"


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)


@admin.register(RegistroFichaje)
class RegistroFichajeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'hora_entrada', 'hora_salida', 'proyecto', 'jornada', 'horas_trabajadas', 'completo')
    list_filter = ('fecha', 'jornada', 'completo', 'proyecto')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', '-hora_entrada')
    readonly_fields = ('horas_trabajadas', 'completo', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'fecha')
        }),
        ('Horarios', {
            'fields': ('hora_entrada', 'hora_salida')
        }),
        ('Detalles del trabajo', {
            'fields': ('proyecto', 'jornada')
        }),
        ('Información calculada', {
            'fields': ('horas_trabajadas', 'completo'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
