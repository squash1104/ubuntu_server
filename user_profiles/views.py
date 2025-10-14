from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils import timezone

from colaboradores.models import Colaborador
from convidados.models import Convidado
from historico.models import Historico

from .forms import CustomPasswordChangeForm, ProfileForm
from .models import Profile


@login_required
def user_settings(request):
    """Página de configurações do usuário"""
    # Obter ou criar perfil do usuário
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Inicializar formulários
    profile_form = ProfileForm(instance=profile, user=request.user)
    password_form = CustomPasswordChangeForm(user=request.user)

    # Estatísticas do usuário logado
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Cadastros feitos pelo usuário logado
    colaboradores_cadastrados = Colaborador.objects.filter(
        cadastrado_por=request.user
    ).count()
    convidados_cadastrados = Convidado.objects.filter(
        colaborador__cadastrado_por=request.user
    ).count()
    total_cadastros_usuario = colaboradores_cadastrados + convidados_cadastrados

    # Dados de produtividade dos últimos 7 dias (apenas do usuário)
    productivity_data = []
    last_7_days = []
    for i in range(7):
        date = today - timedelta(days=6 - i)
        count = Convidado.objects.filter(
            colaborador__cadastrado_por=request.user, data_cadastro__date=date
        ).count()
        productivity_data.append(count)
        last_7_days.append(date.strftime("%a"))

    # Calcular ranking do usuário
    def calcular_ranking_usuario():
        # Buscar todos os usuários e seus totais
        usuarios_stats = []
        for user in Colaborador.objects.values_list(
            "cadastrado_por", flat=True
        ).distinct():
            if user:
                colab_count = Colaborador.objects.filter(cadastrado_por=user).count()
                conv_count = Convidado.objects.filter(
                    colaborador__cadastrado_por=user
                ).count()
                total = colab_count + conv_count
                usuarios_stats.append(
                    {
                        "usuario": user,
                        "total": total,
                        "colaboradores": colab_count,
                        "convidados": conv_count,
                    }
                )

        # Ordenar por total
        usuarios_stats.sort(key=lambda x: x["total"], reverse=True)

        # Encontrar posição do usuário logado
        for i, user_data in enumerate(usuarios_stats, 1):
            if user_data["usuario"] == request.user:
                return i, user_data
        return None, None

    posicao_ranking, dados_usuario = calcular_ranking_usuario()

    # Calcular badges do usuário (usando a mesma lógica do dashboard)
    def calcular_badges_usuario(total, colaboradores, convidados):
        badges = []

        # Badges por total de cadastros
        if total >= 1000:
            badges.append(
                {"emoji": "👑", "nome": "Rei dos Cadastros", "cor": "bg-danger"}
            )
        elif total >= 500:
            badges.append({"emoji": "💎", "nome": "Diamante", "cor": "bg-primary"})
        elif total >= 250:
            badges.append({"emoji": "🏆", "nome": "Campeão", "cor": "bg-warning"})
        elif total >= 100:
            badges.append({"emoji": "🥇", "nome": "Ouro", "cor": "bg-warning"})
        elif total >= 50:
            badges.append(
                {"emoji": "⭐", "nome": "Super Cadastrador", "cor": "bg-success"}
            )
        elif total >= 25:
            badges.append({"emoji": "🔥", "nome": "Em Chamas", "cor": "bg-danger"})
        elif total >= 10:
            badges.append({"emoji": "🚀", "nome": "Decolando", "cor": "bg-info"})
        elif total >= 5:
            badges.append({"emoji": "🌱", "nome": "Crescendo", "cor": "bg-success"})
        elif total >= 1:
            badges.append({"emoji": "🌱", "nome": "Iniciante", "cor": "bg-secondary"})
        else:
            badges.append({"emoji": "🌱", "nome": "Novato", "cor": "bg-secondary"})

        return badges

    badges_usuario = calcular_badges_usuario(
        total_cadastros_usuario, colaboradores_cadastrados, convidados_cadastrados
    )

    # Histórico do usuário (paginado)
    historico_usuario = Historico.objects.filter(usuario=request.user).order_by(
        "-data_hora"
    )
    paginator = Paginator(historico_usuario, 10)  # 10 itens por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    stats = {
        "total_convidados": convidados_cadastrados,
        "convidados_hoje": Convidado.objects.filter(
            colaborador__cadastrado_por=request.user, data_cadastro__date=today
        ).count(),
        "convidados_semana": Convidado.objects.filter(
            colaborador__cadastrado_por=request.user, data_cadastro__date__gte=week_ago
        ).count(),
        "convidados_mes": Convidado.objects.filter(
            colaborador__cadastrado_por=request.user, data_cadastro__date__gte=month_ago
        ).count(),
        "badges": badges_usuario,
        "posicao_ranking": posicao_ranking,
        "total_cadastros_usuario": total_cadastros_usuario,
        "horas_logado": 0,  # Implementar lógica de tracking de tempo
        "sessoes_hoje": 1,  # Implementar lógica de sessões
        "dias_ativo": (today - request.user.date_joined.date()).days,
        "productivity_data": productivity_data,
        "last_7_days": last_7_days,
        "page_obj": page_obj,
    }

    if request.method == "POST":
        if "profile_submit" in request.POST:
            profile_form = ProfileForm(
                request.POST, request.FILES, instance=profile, user=request.user
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect("user_profiles:user_settings")

        elif "password_submit" in request.POST:
            password_form = CustomPasswordChangeForm(
                user=request.user, data=request.POST
            )
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Senha alterada com sucesso!")
                return redirect("user_profiles:user_settings")

    context = {
        "profile_form": profile_form,
        "password_form": password_form,
        "profile": profile,
        "stats": stats,
    }

    return render(request, "user_profiles/settings.html", context)
