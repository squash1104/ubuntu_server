from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from .models import UserSession


class UserActivityMiddleware:
    """Atualiza atividade de usuário e encerra sessões ociosas.

    - Atualiza/Cria UserSession para o session_key atual
    - Marca end_at se ocioso por mais que IDLE_TIMEOUT_SECONDS
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            if not request.user.is_authenticated:
                return response

            # garanta que haja session_key
            if not request.session.session_key:
                request.session.save()

            session_key = request.session.session_key
            now = timezone.now()

            sess, _ = UserSession.objects.get_or_create(
                user=request.user, session_key=session_key
            )
            # Verifica inatividade
            idle_seconds = (now - (sess.last_seen_at or sess.start_at)).total_seconds()
            idle_limit = getattr(settings, "IDLE_TIMEOUT_SECONDS", 1800)
            if idle_seconds > idle_limit and not sess.end_at:
                sess.end_at = now
            # Atualiza last_seen sempre que houver request
            sess.last_seen_at = now
            sess.save(update_fields=["last_seen_at", "end_at"])
        except Exception:
            # Não quebrar request por causa de métricas
            pass

        return response
