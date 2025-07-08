from django.urls import path
from . import views # Importa as views do app colaboradores

app_name = 'colaboradores'

urlpatterns = [
    path('', views.lista_colaboradores, name='lista_colaboradores'),
    path('cadastrar/', views.cadastrar_colaborador, name='cadastrar_colaborador'),
    path('editar/<int:colaborador_id>/', views.editar_colaborador, name='editar_colaborador'),
    path('excluir/<int:colaborador_id>/', views.excluir_colaborador, name='excluir_colaborador'),
]

