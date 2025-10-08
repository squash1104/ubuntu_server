from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "full_name",
    ]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Usuário", {"fields": ("user",)}),
        ("Informações Pessoais", {"fields": ("photo", "full_name")}),
        (
            "Metadados",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
