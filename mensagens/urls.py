from django.urls import path
from . import views

app_name = 'mensagens'

urlpatterns = [
    path('enviar/', views.enviar_mensagens_view, name='enviar_mensagens'),
    path('templates/', views.get_templates_view, name='get_templates'),
    path('historico/', views.historico_mensagens_view, name='historico_mensagens'),
    path('templates/gerenciar/', views.gerenciar_templates_view, name='gerenciar_templates'),
]
