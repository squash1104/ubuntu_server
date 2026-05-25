from django.urls import path

from . import views

app_name = "mensagens"

urlpatterns = [
    path("", views.painel_mensagens_view, name="painel_mensagens"),
    path("enviar/", views.enviar_mensagens_view, name="enviar_mensagens"),
    path("enviar-massa/", views.enviar_mensagens_massa_view, name="enviar_massa"),
    path("templates/", views.get_templates_view, name="get_templates"),
    path("historico/", views.historico_mensagens_view, name="historico_mensagens"),
    path(
        "templates/gerenciar/",
        views.gerenciar_templates_view,
        name="gerenciar_templates",
    ),
    path(
        "templates/editar/<int:template_id>/",
        views.editar_template_view,
        name="editar_template",
    ),
    path(
        "templates/excluir/<int:template_id>/",
        views.excluir_template_view,
        name="excluir_template",
    ),
    path(
        "salvar-template-rapido/",
        views.salvar_template_rapido_view,
        name="salvar_template_rapido",
    ),
    path("upload-imagem/", views.upload_imagem_view, name="upload_imagem"),
    path(
        "arquivo/<path:caminho>",
        views.servir_arquivo_mensagem_view,
        name="servir_arquivo",
    ),
    path("campanhas/", views.campanhas_list_view, name="campanhas_list"),
    path(
        "campanhas/<int:campanha_id>/",
        views.campanha_detail_view,
        name="campanha_detail",
    ),
]
