from django.urls import path
from . import views
from .views import (lista_convidados, editar_convidado, excluir_convidado)

app_name = 'convidados'

urlpatterns = [
    path('', lista_convidados, name='lista_convidados'),
    path('cadastrar/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path('cadastrar/<int:colaborador_id>/', views.cadastrar_convidado, name='cadastrar_convidado_por_colaborador'),
    path('editar/<int:pk>/', editar_convidado, name='editar_convidado'),
    path('excluir/<int:pk>/', excluir_convidado, name='excluir_convidado'),
    path('<int:pk>/', views.colaborador_convidados, name='colaborador_convidados'),
    path('relatorios/convidados/', views.relatorio_convidados_view, name='guest_report_form'),
    path('get_bairros_ajax/', views.get_bairros_ajax, name='get_bairros_ajax'),
    path('check_telefone/', views.check_telefone_exists, name='check_telefone_exists_convidado'),
    path('check_nome/', views.check_nome_exists, name='check_nome_exists_convidado'),
]