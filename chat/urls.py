from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("historico/<str:username>/", views.fetch_messages, name="fetch_messages"),
    path("lista/", views.lista_contatos, name="lista_contatos"),
    path("contatos_status/", views.contatos_status, name="contatos_status"),
    path("mensagens/", views.mensagens, name="chat_mensagens"),
    path("test/", views.test_websocket, name="test_websocket"),
    path("test-simple/", views.test_websocket_simple, name="test_websocket_simple"),
    path("debug/", views.debug_chat, name="debug_chat"),
    path("simple-test/", views.simple_chat_test, name="simple_chat_test"),
    path("complete-test/", views.chat_complete_test, name="chat_complete_test"),
]
