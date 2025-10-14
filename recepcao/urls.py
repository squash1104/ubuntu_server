from django.urls import path

from . import views

app_name = "recepcao"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("visitantes/", views.visitantes_list, name="visitantes_list"),
    path("visitantes/novo/", views.visitante_create, name="visitante_create"),
    # Detalhe redireciona para editar no modo visualização
    path("visitantes/<int:pk>/", views.visitante_update, name="visitante_detail"),
    path(
        "visitantes/<int:pk>/editar/", views.visitante_update, name="visitante_update"
    ),
    path(
        "visitantes/<int:pk>/enfileirar/",
        views.visitante_enfileirar,
        name="visitante_enfileirar",
    ),
    path(
        "visitantes/<int:pk>/remover/", views.visitante_delete, name="visitante_delete"
    ),
    path("atendentes/", views.atendentes, name="atendentes"),
    path("fila/chamar/", views.chamar_proximo, name="chamar_proximo"),
    path("atendimentos/<int:pk>/", views.atendimento_detail, name="atendimento_detail"),
    path(
        "atendimentos/<int:pk>/iniciar/",
        views.atendimento_iniciar,
        name="atendimento_iniciar",
    ),
    path(
        "atendimentos/<int:pk>/encerrar/",
        views.atendimento_encerrar,
        name="atendimento_encerrar",
    ),
    path(
        "atendimentos/<int:pk>/cancelar/",
        views.atendimento_cancelar,
        name="atendimento_cancelar",
    ),
    path(
        "atendimentos/<int:pk>/anexos/",
        views.atendimento_anexar,
        name="atendimento_anexar",
    ),
    path(
        "declaracao/<int:pk>/", views.declaracao_visitante, name="declaracao_visitante"
    ),
    path("relatorios/", views.relatorios, name="relatorios"),
    path("aniversariantes/", views.aniversariantes, name="aniversariantes"),
]
