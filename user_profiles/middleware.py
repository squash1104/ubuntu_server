from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone

from .models import UserSession


class UserActivityMiddleware:
    """Atualiza atividade de usuário e encerra sessões ociosas.

    - Atualiza/Cria UserSession para o session_key atual
    - Marca end_at e desloga se ocioso por mais que IDLE_TIMEOUT_SECONDS
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if not request.user.is_authenticated:
                return self.get_response(request)

            if not request.session.session_key:
                request.session.save()

            session_key = request.session.session_key
            now = timezone.now()

            sess, _ = UserSession.objects.get_or_create(
                user=request.user, session_key=session_key
            )

            idle_seconds = (now - (sess.last_seen_at or sess.start_at)).total_seconds()
            idle_limit = getattr(settings, "IDLE_TIMEOUT_SECONDS", 1800)

            if idle_seconds > idle_limit and not sess.end_at:
                sess.end_at = now
                sess.save(update_fields=["end_at"])
                logout(request)
                messages.warning(request, "Sessão expirada por inatividade")
                return redirect("login")

            sess.last_seen_at = now
            sess.save(update_fields=["last_seen_at"])
        except Exception:
            pass

        return self.get_response(request)
