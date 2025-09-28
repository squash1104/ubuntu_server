from django.urls import path

from . import views

urlpatterns = [
    path("", views.messages_page, name="chat"),
    path("historico/<str:username>/", views.fetch_messages, name="fetch_messages"),
    path("mark_read/", views.mark_message_read, name="mark_message_read"),
    path("mark_read_batch/", views.mark_messages_read_batch, name="mark_messages_read_batch"),
    path("lista/", views.lista_contatos, name="lista_contatos"),
    path("contatos_status/", views.contatos_status, name="contatos_status"),
    path("test/", views.test_websocket, name="test_websocket"),
    path("test-simple/", views.test_websocket_simple, name="test_websocket_simple"),
    path("debug/", views.debug_chat, name="debug_chat"),
    path("simple-test/", views.simple_chat_test, name="simple_chat_test"),
    path("complete-test/", views.chat_complete_test, name="chat_complete_test"),
    path("test-simple/", views.test_chat_simple, name="test_chat_simple"),
    path("test-navbar/", views.test_navbar_responsive, name="test_navbar_responsive"),
]
