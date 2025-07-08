from django.urls import path
from . import views # Importa as views do app convidados

app_name = 'convidados'

urlpatterns = [
    path('', views.lista_convidados, name='lista_convidados'),
    path('cadastrar/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path('do_colaborador/<int:colaborador_id>/', views.colaborador_convidados, name='colaborador_convidados'),
    path('cadastrar/<int:colaborador_id>/', views.cadastrar_convidado, name='cadastrar_convidado_para_colaborador'),
    path('editar/<int:convidado_id>/', views.editar_convidado, name='editar_convidado'),
    path('excluir/<int:convidado_id>/', views.excluir_convidado, name='excluir_convidado'),
]
