"""
URL configuration for sistema_fidelizacao project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import importlib

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import (
    views as auth_views,  # Importe as views de autenticação do Django
)
from django.http import HttpResponse
from django.urls import include, path, re_path
from django_ratelimit.decorators import ratelimit

from historico.views import PasswordResetCompleteWithLogView
from utils_aniversarios.views import aniversariantes_view

from . import views


def health_check_view(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="index"),
    path("home/", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    re_path(
        r"^login/$",
        ratelimit(key="ip", rate="5/m", method="POST")(
            auth_views.LoginView.as_view(template_name="registration/login.html")
        ),
        name="login",
    ),
    path(
        "logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"
    ),  # Redireciona para home após logout
    # path('', include('django.contrib.auth.urls')), #
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/pw_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/pw_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetCompleteWithLogView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/pw_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("mapa-apoiadores/", views.mapa_apoiadores, name="mapa_apoiadores"),
    path("colaboradores/", include("colaboradores.urls", namespace="colaboradores")),
    path("convidados/", include("convidados.urls", namespace="convidados")),
    path("user-profiles/", include("user_profiles.urls", namespace="user_profiles")),
    path("mensagens/", include("mensagens.urls", namespace="mensagens")),
    path("geografia/", include("geografia.urls")),
    path("recepcao/", include("recepcao.urls", namespace="recepcao")),
    path("historico/", include("historico.urls", namespace="historico")),
    path("health/", health_check_view),
    path("sobre/", views.sobre, name="sobre"),
    path("apresentacao/", views.apresentacao_pdf, name="apresentacao_pdf"),
    # path("chat/", include("chat.urls")),  # Chat desabilitado temporariamente
    # security: apenas em produção e se o app existir
    # Página de aniversariantes
    path("aniversariantes/", aniversariantes_view, name="aniversariantes"),
]

# Adiciona rotas do 'security' quando em produção e app disponível
try:
    from decouple import config as _config

    if (
        _config("ENVIRONMENT", default="development") == "production"
        and importlib.util.find_spec("security") is not None
    ):
        urlpatterns += [
            path(
                "security/",
                include(("security.urls", "security"), namespace="security"),
            ),
        ]
except Exception:
    pass

# Adicionar URLs para arquivos estáticos
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Você também pode adicionar o favicon.ico diretamente aqui para facilitar
# from django.views.generic.base import RedirectView
# urlpatterns += [
#     path('favicon.ico', RedirectView.as_view(
#         url=settings.STATIC_URL + 'favicon.ico'
#     ))
# ]
