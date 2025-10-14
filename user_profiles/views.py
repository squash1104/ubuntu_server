from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from colaboradores.models import Colaborador
from convidados.models import Convidado
from historico.models import Historico, TipoAcao, TipoObjeto

from .forms import CustomPasswordChangeForm, ProfileForm
from .models import Profile, UserSession


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
    from django.db.models import Q

    convidados_cadastrados = (
        Convidado.objects.filter(
            Q(colaborador__cadastrado_por=request.user) | Q(cadastrado_por=request.user)
        )
        .distinct()
        .count()
    )
    total_cadastros_usuario = colaboradores_cadastrados + convidados_cadastrados

    # Dados de produtividade dos últimos 7 dias (apenas do usuário)
    productivity_data = []
    last_7_days = []
    for i in range(7):
        date = today - timedelta(days=6 - i)
        count = (
            Convidado.objects.filter(
                Q(colaborador__cadastrado_por=request.user)
                | Q(cadastrado_por=request.user),
                data_cadastro__date=date,
            )
            .distinct()
            .count()
        )
        productivity_data.append(count)
        last_7_days.append(date.strftime("%a"))

    # Calcular ranking do usuário
    def calcular_ranking_usuario():
        # Ranking geral (mesma lógica do dashboard):
        # contar colaboradores e convidados do usuário
        from django.contrib.auth.models import User as DjangoUser
        from django.db.models import Q

        usuarios_stats = []
        for u in DjangoUser.objects.all():
            colab_count = Colaborador.objects.filter(cadastrado_por=u).count()
            conv_count = (
                Convidado.objects.filter(
                    Q(colaborador__cadastrado_por=u) | Q(cadastrado_por=u)
                )
                .distinct()
                .count()
            )
            total = colab_count + conv_count
            usuarios_stats.append(
                {
                    "usuario": u,
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

    # Calcular badges do usuário (com datas de conquista) usando histórico cumulativo
    def calcular_badges_usuario(total, colaboradores, convidados):
        niveis = [
            (1, "🌱", "Iniciante", "bg-secondary"),
            (5, "🌱", "Crescendo", "bg-success"),
            (10, "🚀", "Decolando", "bg-info"),
            (25, "🔥", "Em Chamas", "bg-danger"),
            (50, "⭐", "Super Cadastrador", "bg-success"),
            (100, "🥇", "Ouro", "bg-warning"),
            (250, "🏆", "Campeão", "bg-warning"),
            (500, "💎", "Diamante", "bg-primary"),
            (1000, "👑", "Rei dos Cadastros", "bg-danger"),
        ]

        # Monta a linha do tempo de criações do usuário (colaborador ou convidado)
        eventos = (
            Historico.objects.filter(
                usuario=request.user,
                acao=TipoAcao.CRIAR,
                tipo_objeto__in=[
                    TipoObjeto.COLABORADOR,
                    TipoObjeto.CONVIDADO,
                ],
            )
            .order_by("data_hora")
            .values("data_hora")
        )

        badges = []
        cumul = 0
        idx_nivel = 0
        # Salvaguarda: não permitir desbloquear níveis acima do total atual
        max_allowed = total
        # Avança cumulativamente atribuindo a data em que alcançou cada nível
        for idx, ev in enumerate(eventos, 1):
            cumul = idx
            while (
                idx_nivel < len(niveis)
                and cumul >= niveis[idx_nivel][0]
                and niveis[idx_nivel][0] <= max_allowed
            ):
                min_val, emoji, nome, cor = niveis[idx_nivel]
                badges.append(
                    {
                        "emoji": emoji,
                        "nome": nome,
                        "cor": cor,
                        "data": ev["data_hora"],
                        "min": min_val,
                    }
                )
                idx_nivel += 1
                if idx_nivel >= len(niveis):
                    break

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

    # Tempo logado e sessões
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = UserSession.objects.filter(
        user=request.user, start_at__gte=today_start
    )
    horas_logado = sum(s.duration_seconds for s in today_sessions) / 3600.0
    sessoes_hoje = today_sessions.count()

    # Contagens por período (somar convidados e colaboradores do usuário)
    convidados_hoje = (
        Convidado.objects.filter(
            Q(colaborador__cadastrado_por=request.user)
            | Q(cadastrado_por=request.user),
            data_cadastro__date=today,
        )
        .distinct()
        .count()
    )
    colaboradores_hoje = Colaborador.objects.filter(
        cadastrado_por=request.user, data_cadastro__date=today
    ).count()

    convidados_semana = (
        Convidado.objects.filter(
            Q(colaborador__cadastrado_por=request.user)
            | Q(cadastrado_por=request.user),
            data_cadastro__date__gte=week_ago,
        )
        .distinct()
        .count()
    )
    colaboradores_semana = Colaborador.objects.filter(
        cadastrado_por=request.user, data_cadastro__date__gte=week_ago
    ).count()

    convidados_mes = (
        Convidado.objects.filter(
            Q(colaborador__cadastrado_por=request.user)
            | Q(cadastrado_por=request.user),
            data_cadastro__date__gte=month_ago,
        )
        .distinct()
        .count()
    )
    colaboradores_mes = Colaborador.objects.filter(
        cadastrado_por=request.user, data_cadastro__date__gte=month_ago
    ).count()

    stats = {
        "total_convidados": convidados_cadastrados,
        # Cartões por período: soma de convidados + colaboradores
        "convidados_hoje": convidados_hoje + colaboradores_hoje,
        "convidados_semana": convidados_semana + colaboradores_semana,
        "convidados_mes": convidados_mes + colaboradores_mes,
        "badges": badges_usuario,
        "posicao_ranking": posicao_ranking,
        "total_cadastros_usuario": total_cadastros_usuario,
        "horas_logado": f"{horas_logado:.1f}",
        "sessoes_hoje": sessoes_hoje,
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


@login_required
def productivity_data(request):
    """
    Return JSON data for productivity chart based on
    range param: day/week/month/year.
    """
    from django.db.models import Q

    rng = request.GET.get("range", "week")
    now = timezone.now()
    today = now.date()

    labels = []
    data = []

    def count_for_date(d):
        return (
            Convidado.objects.filter(
                Q(colaborador__cadastrado_por=request.user)
                | Q(cadastrado_por=request.user),
                data_cadastro__date=d,
            )
            .distinct()
            .count()
        )

    if rng == "day":
        # last 24 hours by hour
        for i in range(24):
            hour = (now - timedelta(hours=23 - i)).replace(
                minute=0, second=0, microsecond=0
            )
            labels.append(hour.strftime("%Hh"))
            cnt = (
                Convidado.objects.filter(
                    Q(colaborador__cadastrado_por=request.user)
                    | Q(cadastrado_por=request.user),
                    data_cadastro__gte=hour,
                    data_cadastro__lt=hour + timedelta(hours=1),
                )
                .distinct()
                .count()
            )
            data.append(cnt)
    elif rng == "month":
        # last 30 days
        for i in range(30):
            d = today - timedelta(days=29 - i)
            labels.append(d.strftime("%d/%m"))
            data.append(count_for_date(d))
    elif rng == "year":
        # last 12 months
        from calendar import month_abbr

        year = today.year
        month = today.month
        months = []
        for i in range(11, -1, -1):
            m = (month - i - 1) % 12 + 1
            y = year + ((month - i - 1) // 12)
            months.append((y, m))
        for y, m in months:
            labels.append(f"{month_abbr[m]}/{str(y)[2:]}")
            cnt = (
                Convidado.objects.filter(
                    Q(colaborador__cadastrado_por=request.user)
                    | Q(cadastrado_por=request.user),
                    data_cadastro__year=y,
                    data_cadastro__month=m,
                )
                .distinct()
                .count()
            )
            data.append(cnt)
    else:
        # default week: last 7 days
        for i in range(7):
            d = today - timedelta(days=6 - i)
            labels.append(d.strftime("%a"))
            data.append(count_for_date(d))

    return JsonResponse({"labels": labels, "data": data})
