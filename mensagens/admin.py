from django.contrib import admin

from .models import TemplateMensagem


@admin.register(TemplateMensagem)
class TemplateMensagemAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo_mensagem", "meta_template_name", "ativo", "criado_em")
    list_filter = ("tipo_mensagem", "ativo")
    search_fields = ("nome", "meta_template_name", "conteudo")
    fieldsets = (
        (
            None,
            {
                "fields": ("nome", "tipo_mensagem", "conteudo", "ativo"),
            },
        ),
        (
            "Template do Meta (opcional)",
            {
                "fields": ("meta_template_name", "meta_template_language", "imagem"),
                "description": "Preencha apenas se tiver um template aprovado no Meta Business. O sistema enviará como template do Meta em vez de texto livre.",
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
