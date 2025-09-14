# chat/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Message

online_users = set()


@login_required
def chat_view(request):
    users = User.objects.exclude(id=request.user.id).select_related("profile")
    return render(request, "chat/chat.html", {"users": users})


def test_websocket(request):
    """View simples para testar WebSocket"""
    with open("test_websocket.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


def test_websocket_simple(request):
    """View para testar WebSocket com consumer simples"""
    with open("test_websocket_simple.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


def debug_chat(request):
    """View para debugar o chat WebSocket"""
    with open("debug_chat.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


def simple_chat_test(request):
    """View para testar o chat simples"""
    with open("simple_chat_test.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


def chat_complete_test(request):
    """View para testar o chat completo"""
    with open("test_chat_complete.html") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


@login_required
def fetch_messages(request, username):
    try:
        from django.utils import timezone

        mensagens = Message.objects.filter(
            sender__username__in=[request.user.username, username],
            recipient__username__in=[request.user.username, username],
        ).order_by("timestamp")

        # Marcar mensagens recebidas como lidas
        mensagens_nao_lidas = mensagens.filter(recipient=request.user, read=False)
        mensagens_nao_lidas.update(read=True, read_at=timezone.now())

        data = [
            {
                "sender": msg.sender.get_full_name(),
                "message": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "read": msg.read,
                "is_own": msg.sender == request.user,
            }
            for msg in mensagens
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def lista_contatos(request):
    contatos = User.objects.exclude(id=request.user.id)
    return JsonResponse(
        [{"id": u.id, "username": u.username} for u in contatos], safe=False
    )


def contatos_status(request):
    custom_user = get_user_model()
    contatos = custom_user.objects.exclude(id=request.user.id).select_related("profile")
    contatos_data = [
        {
            "username": c.username,
            "full_name": c.get_full_name() or c.username,
            "online": c.profile.online if hasattr(c, "profile") else False,
        }
        for c in contatos
    ]
    return JsonResponse(contatos_data, safe=False)


@login_required
def mensagens(request):
    return render(request, "chat/chat.html")
