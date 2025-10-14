from django.urls import path

from . import views  # Importa as views do app colaboradores

app_name = "colaboradores"

urlpatterns = [
    path("", views.lista_colaboradores, name="lista_colaboradores"),
    path("adicionar/", views.adicionar_colaborador, name="adicionar_colaborador"),
    path("editar/<int:pk>/", views.editar_colaborador, name="editar_colaborador"),
    path(
        "excluir/<int:colaborador_id>/",
        views.excluir_colaborador,
        name="excluir_colaborador",
    ),
    path(
        "relatorios/colaboradores/",
        views.relatorio_colaboradores_view,
        name="relatorio_colaboradores_form",
    ),
    path("get_bairros_ajax/", views.get_bairros_ajax, name="get_bairros_ajax"),
    path("check_telefone/", views.check_telefone_exists, name="check_telefone_exists"),
    path("check_nome/", views.check_nome_exists, name="check_nome_exists"),
]
