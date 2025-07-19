from django.urls import path
from . import views
from .views import (lista_convidados, editar_convidado, excluir_convidado)

app_name = 'convidados'

urlpatterns = [
    path('', lista_convidados, name='lista_convidados'),
    path('cadastrar/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path('do_colaborador/<int:colaborador_id>/', views.colaborador_convidados, name='colaborador_convidados'),
    path('cadastrar/<int:colaborador_id>/', views.cadastrar_convidado, name='cadastrar_convidado_para_colaborador'),
    path('editar/<int:pk>/', editar_convidado, name='editar_convidado'),
    path('excluir/<int:pk>/', excluir_convidado, name='excluir_convidado'),
]
