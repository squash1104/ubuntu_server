import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils import timezone as dj_timezone

from geografia.models import Cidade

from .models import (
    Atendimento,
    AtendimentoAnexo,
    AtendimentoEvento,
    AtendimentoStatus,
    Attendente,
    TipoEvento,
    Visitante,
)


def is_recepcionista(user):
    return (
        user.is_authenticated
        and user.groups.filter(
            name__in=["Recepcionista", "Supervisor", "Admin"]
        ).exists()
    )


def is_atendente(user):
    return (
        user.is_authenticated
        and user.groups.filter(name__in=["Atendente", "Supervisor", "Admin"]).exists()
    )


def is_supervisor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name__in=["Supervisor", "Admin"]).exists()
    )


@login_required
@user_passes_test(is_recepcionista)
def home(request):
    # Dashboard principal com KPIs e gráficos por período
    hoje = timezone.localdate()
    preset = (request.GET.get("preset") or "").lower()
    try:
        dt_ini_str = request.GET.get("ini")
        dt_fim_str = request.GET.get("fim")
        if preset:
            if preset == "today":
                dt_ini = hoje
                dt_fim = hoje
            elif preset == "last7":
                dt_fim = hoje
                dt_ini = hoje - timedelta(days=6)
            elif preset == "last30":
                dt_fim = hoje
                dt_ini = hoje - timedelta(days=29)
            elif preset == "month":
                dt_fim = hoje
                dt_ini = hoje.replace(day=1)
            elif preset == "all":
                # Desde o primeiro atendimento registrado
                first = (
                    Atendimento.objects.order_by("horario_chegada")
                    .values_list("horario_chegada", flat=True)
                    .first()
                )
                if first:
                    dt_ini = first.date()
                    dt_fim = hoje
                else:
                    dt_ini = hoje - timedelta(days=29)
                    dt_fim = hoje
            else:
                dt_fim = (
                    timezone.datetime.fromisoformat(dt_fim_str).date()
                    if dt_fim_str
                    else hoje
                )
                dt_ini = (
                    timezone.datetime.fromisoformat(dt_ini_str).date()
                    if dt_ini_str
                    else (hoje - timedelta(days=29))
                )
        else:
            dt_fim = (
                timezone.datetime.fromisoformat(dt_fim_str).date()
                if dt_fim_str
                else hoje
            )
            dt_ini = (
                timezone.datetime.fromisoformat(dt_ini_str).date()
                if dt_ini_str
                else (hoje - timedelta(days=29))
            )
    except Exception:
        dt_fim = hoje
        dt_ini = hoje - timedelta(days=29)

    # Base: atendimentos criados (chegada) no período
    base_qs = Atendimento.objects.filter(
        horario_chegada__date__gte=dt_ini, horario_chegada__date__lte=dt_fim
    )

    total_atend = base_qs.filter(
        status=AtendimentoStatus.CONCLUIDO
    ).count()  # Apenas concluídos
    total_conc = base_qs.filter(status=AtendimentoStatus.CONCLUIDO).count()
    total_canc = base_qs.filter(status=AtendimentoStatus.CANCELADO).count()

    # Médias de tempo
    espera_expr = ExpressionWrapper(
        F("inicio_atendimento") - F("horario_chegada"), output_field=DurationField()
    )
    atendimento_expr = ExpressionWrapper(
        F("fim_atendimento") - F("inicio_atendimento"), output_field=DurationField()
    )

    avg_espera = base_qs.filter(inicio_atendimento__isnull=False).aggregate(
        v=Avg(espera_expr)
    )["v"]
    avg_atend = base_qs.filter(
        fim_atendimento__isnull=False, inicio_atendimento__isnull=False
    ).aggregate(v=Avg(atendimento_expr))["v"]

    def fmt_td(td):
        if not td:
            return "-"
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}h{minutes:02d}m"

    def fmt_td_hours(td):
        if not td:
            return "-"
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}h{minutes:02d}m"

    kpis = {
        "periodo_ini": dt_ini.isoformat(),
        "periodo_fim": dt_fim.isoformat(),
        "preset": preset or "custom",
        "total": total_atend,
        "avg_atendimento": fmt_td(avg_atend),
        "desistencias": total_canc,
        "avg_espera": fmt_td(avg_espera),
    }

    # Séries diárias no período
    labels = []
    serie_chegadas = []
    serie_concluidos = []
    dia = dt_ini
    while dia <= dt_fim:
        labels.append(dia.strftime("%d/%m"))
        serie_chegadas.append(
            Atendimento.objects.filter(horario_chegada__date=dia).count()
        )
        serie_concluidos.append(
            Atendimento.objects.filter(
                status=AtendimentoStatus.CONCLUIDO, fim_atendimento__date=dia
            ).count()
        )
        dia += timedelta(days=1)

    # Distribuição por status no período (com base na chegada)
    status_labels = ["Aguardando", "Em Atendimento", "Concluído", "Cancelado"]
    status_data = [
        base_qs.filter(status=AtendimentoStatus.AGUARDANDO).count(),
        base_qs.filter(status=AtendimentoStatus.EM_ATENDIMENTO).count(),
        base_qs.filter(status=AtendimentoStatus.CONCLUIDO).count(),
        base_qs.filter(status=AtendimentoStatus.CANCELADO).count(),
    ]

    # Por atendente (concluídos dentro do período por data de fim)
    por_atendente = (
        Atendimento.objects.filter(
            status=AtendimentoStatus.CONCLUIDO,
            fim_atendimento__date__gte=dt_ini,
            fim_atendimento__date__lte=dt_fim,
            atendente__isnull=False,
        )
        .values("atendente__nome")
        .annotate(
            total=Count("id"),
            tempo_medio_at=Avg(atendimento_expr),
            tempo_medio_esp=Avg(espera_expr),
        )
        .order_by("-total")
    )
    atendentes_labels = [(p["atendente__nome"]) for p in por_atendente]
    atendentes_data = [p["total"] for p in por_atendente]
    atendentes_avg_at = [
        int(p["tempo_medio_at"].total_seconds() / 60) if p["tempo_medio_at"] else 0
        for p in por_atendente
    ]
    atendentes_avg_esp = [
        int(p["tempo_medio_esp"].total_seconds() / 60) if p["tempo_medio_esp"] else 0
        for p in por_atendente
    ]
    atendentes_rows = [
        {
            "nome": p["atendente__nome"] or "-",
            "total": p["total"],
            "tempo_medio": fmt_td(p["tempo_medio_at"]),
        }
        for p in por_atendente
    ]

    # Agregados mensais (quantidade, média de espera, média de atendimento)
    mensal_labels = []
    mensal_qtd = []
    mensal_esp = []
    mensal_at = []
    # Varre de mês em mês no intervalo
    cursor = dt_ini.replace(day=1)
    end_month = dt_fim.replace(day=1)
    while cursor <= end_month:
        prox = (cursor.replace(day=28) + timedelta(days=4)).replace(
            day=1
        )  # primeiro dia do mês seguinte
        qtd = Atendimento.objects.filter(
            horario_chegada__date__gte=cursor, horario_chegada__date__lt=prox
        ).count()
        esp = Atendimento.objects.filter(
            inicio_atendimento__isnull=False,
            horario_chegada__date__gte=cursor,
            horario_chegada__date__lt=prox,
        ).aggregate(v=Avg(espera_expr))["v"]
        atd = Atendimento.objects.filter(
            fim_atendimento__isnull=False,
            inicio_atendimento__isnull=False,
            inicio_atendimento__date__gte=cursor,
            inicio_atendimento__date__lt=prox,
        ).aggregate(v=Avg(atendimento_expr))["v"]
        mensal_labels.append(cursor.strftime("%b/%y"))
        mensal_qtd.append(qtd)
        mensal_esp.append(int(esp.total_seconds() / 60) if esp else 0)
        mensal_at.append(int(atd.total_seconds() / 60) if atd else 0)
        cursor = prox

    # Estatísticas dos atendentes no período
    atendentes_stats = (
        Atendimento.objects.filter(
            status=AtendimentoStatus.CONCLUIDO,
            fim_atendimento__date__gte=dt_ini,
            fim_atendimento__date__lte=dt_fim,
            atendente__isnull=False,
        )
        .values("atendente__nome")
        .annotate(
            total_atendimentos=Count("id"),
            tempo_total_atendimento=Avg(atendimento_expr),
            tempo_medio_atendimento=Avg(atendimento_expr),
        )
        .order_by("-total_atendimentos")
    )

    atendentes_detalhados = []
    for att in atendentes_stats:
        # Calcular total de horas atendendo
        total_horas_display = "-"
        if att["tempo_total_atendimento"]:
            total_seconds = int(
                att["tempo_total_atendimento"].total_seconds()
                * att["total_atendimentos"]
            )
            total_horas_display = fmt_td_hours(timedelta(seconds=total_seconds))

        # Formatar tempo médio
        tempo_medio_display = fmt_td(att["tempo_medio_atendimento"])

        atendentes_detalhados.append(
            {
                "nome": att["atendente__nome"] or "-",
                "total_atendimentos": att["total_atendimentos"],
                "total_horas": total_horas_display,
                "tempo_medio": tempo_medio_display,
            }
        )

    # Lista de atendimentos recentes com filtro de data e paginação
    atendimentos_recentes_qs = Atendimento.objects.filter(
        status__in=[AtendimentoStatus.CONCLUIDO, AtendimentoStatus.CANCELADO],
        horario_chegada__date__gte=dt_ini,
        horario_chegada__date__lte=dt_fim,
    ).order_by("-fim_atendimento")

    # Paginação - 20 itens por página
    paginator = Paginator(atendimentos_recentes_qs, 20)
    page_number = request.GET.get("page", 1)

    try:
        atendimentos_page = paginator.get_page(page_number)
    except Exception:
        atendimentos_page = paginator.get_page(1)

    atendimentos_recentes = []
    for at in atendimentos_page:
        total_display = "-"
        try:
            if at.fim_atendimento and at.horario_chegada:
                total_seconds = int(
                    (at.fim_atendimento - at.horario_chegada).total_seconds()
                )
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_display = f"{hours:02d}h{minutes:02d}m"
        except Exception:
            total_display = "-"
        atendimentos_recentes.append(
            {
                "id": at.id,
                "horario_chegada": at.horario_chegada,
                "inicio_atendimento": at.inicio_atendimento,
                "fim_atendimento": at.fim_atendimento,
                "visitante_nome": getattr(at.visitante, "nome", "-"),
                "atendente_nome": (
                    getattr(at.atendente, "nome", "-") if at.atendente else "-"
                ),
                "status_display": at.get_status_display(),
                "status": at.status,
                "total_display": total_display,
            }
        )

    context = {
        "kpis": kpis,
        "chart_7d_labels": labels,
        "chart_7d_chegadas": serie_chegadas,
        "chart_7d_concluidos": serie_concluidos,
        "status_labels": status_labels,
        "status_data": status_data,
        "atendentes_labels": atendentes_labels,
        "atendentes_data": atendentes_data,
        "atendentes_avg_at": atendentes_avg_at,
        "atendentes_avg_esp": atendentes_avg_esp,
        "atendentes_rows": atendentes_rows,
        "atendentes_detalhados": atendentes_detalhados,
        "mensal_labels": mensal_labels,
        "mensal_qtd": mensal_qtd,
        "mensal_esp": mensal_esp,
        "mensal_at": mensal_at,
        "atendimentos_recentes": atendimentos_recentes,
        "atendimentos_page": atendimentos_page,
        "dt_ini": dt_ini,
        "dt_fim": dt_fim,
    }
    # Dados de geolocalização dos municípios dos visitantes
    from geografia.models import Cidade

    municipios_heat_data = []
    municipios_data = (
        Visitante.objects.filter(municipio__isnull=False)
        .exclude(municipio="")
        .values("municipio")
        .annotate(total=Count("id"))
        .order_by("-total")[:20]  # Top 20 municípios
    )

    for municipio_info in municipios_data:
        municipio_nome = municipio_info["municipio"]
        total_visitantes = municipio_info["total"]

        # Buscar coordenadas da cidade
        try:
            cidade = Cidade.objects.filter(nome_cidade__iexact=municipio_nome).first()

            if cidade and cidade.latitude_cidade and cidade.longitude_cidade:
                municipios_heat_data.append(
                    [
                        float(cidade.latitude_cidade),
                        float(cidade.longitude_cidade),
                        total_visitantes,  # Intensidade baseada no número de visitantes
                    ]
                )
        except Exception:
            # Se não encontrar coordenadas, pula este município
            continue

    municipios_labels = [m["municipio"] for m in municipios_data]
    municipios_values = [m["total"] for m in municipios_data]

    # adiciona total de visitantes cadastrados
    try:
        total_visitantes = Visitante.objects.count()
    except Exception:
        total_visitantes = 0

    context["total_visitantes"] = total_visitantes
    context["municipios_labels"] = municipios_labels
    context["municipios_values"] = municipios_values
    context["municipios_heat_data"] = municipios_heat_data
    return render(request, "recepcao/home.html", context)


@login_required
@user_passes_test(is_recepcionista)
def dashboard(request):
    # Filtra apenas dados do dia atual para controle em tempo real
    hoje = timezone.now().date()
    inicio_dia = timezone.make_aware(
        timezone.datetime.combine(hoje, timezone.datetime.min.time())
    )
    fim_dia = timezone.make_aware(
        timezone.datetime.combine(hoje, timezone.datetime.max.time())
    )

    aguardando = Atendimento.objects.filter(
        status=AtendimentoStatus.AGUARDANDO, horario_chegada__date=hoje
    ).order_by("horario_chegada")

    em_atendimento = Atendimento.objects.filter(
        status=AtendimentoStatus.EM_ATENDIMENTO, horario_chegada__date=hoje
    ).order_by("-inicio_atendimento")

    atendimentos_qs = Atendimento.objects.filter(
        status__in=[AtendimentoStatus.CONCLUIDO, AtendimentoStatus.CANCELADO],
        horario_chegada__date=hoje,
    ).order_by("-fim_atendimento")[:20]

    atendimentos_recentes = []
    for at in atendimentos_qs:
        total_display = "-"
        try:
            if at.fim_atendimento and at.horario_chegada:
                total_seconds = int(
                    (at.fim_atendimento - at.horario_chegada).total_seconds()
                )
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_display = f"{hours:02d}h{minutes:02d}m"
        except Exception:
            total_display = "-"
        atendimentos_recentes.append(
            {
                "id": at.id,
                "horario_chegada": at.horario_chegada,
                "inicio_atendimento": at.inicio_atendimento,
                "fim_atendimento": at.fim_atendimento,
                "visitante_nome": getattr(at.visitante, "nome", "-"),
                "atendente_nome": (
                    getattr(at.atendente, "nome", "-") if at.atendente else "-"
                ),
                "status_display": at.get_status_display(),
                "status": at.status,
                "total_display": total_display,
            }
        )

    # 📌 Calcula total de horas de atendimento (somando apenas concluídos com início e fim do dia atual)
    concluidos = Atendimento.objects.filter(
        status=AtendimentoStatus.CONCLUIDO,
        inicio_atendimento__isnull=False,
        fim_atendimento__isnull=False,
        horario_chegada__date=hoje,
    )

    total_segundos = sum(
        (a.fim_atendimento - a.inicio_atendimento).total_seconds() for a in concluidos
    )

    horas, resto = divmod(int(total_segundos), 3600)
    minutos, _ = divmod(resto, 60)
    total_horas_display = f"{horas:02d}h{minutos:02d}m"

    # KPIs locais para a página de fila (apenas dados do dia atual)
    kpis = {
        "aguardando": aguardando.count(),
        "em_atendimento": em_atendimento.count(),
        "concluidos_hoje": Atendimento.objects.filter(
            status=AtendimentoStatus.CONCLUIDO, fim_atendimento__date=hoje
        ).count(),
        "cancelados_hoje": Atendimento.objects.filter(
            status=AtendimentoStatus.CANCELADO, fim_atendimento__date=hoje
        ).count(),
        "total_horas": total_horas_display,
    }

    # Lista de atendentes e seu status (livre/ocupado) - apenas do dia atual
    atendentes_all = Attendente.objects.all().order_by("nome")
    atendentes_status = []
    for atd in atendentes_all:
        ocupado = Atendimento.objects.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO,
            atendente=atd,
            horario_chegada__date=hoje,
        ).exists()
        atendentes_status.append(
            {
                "id": atd.id,
                "nome": atd.nome,
                "ocupado": ocupado,
            }
        )

    context = {
        "aguardando": aguardando,
        "em_atendimento": em_atendimento,
        "atendimentos_recentes": atendimentos_recentes,
        "kpis": kpis,
        "atendentes_status": atendentes_status,
    }
    return render(request, "recepcao/dashboard.html", context)


@login_required
@user_passes_test(is_recepcionista)
def visitantes_list(request):
    q = request.GET.get("q")
    sort = request.GET.get("sort") or "nome"
    direction = request.GET.get("dir") or "asc"
    order = sort
    if direction == "desc":
        order = f"-{sort}"

    visitantes_qs = Visitante.objects.all()
    if q:
        visitantes_qs = visitantes_qs.filter(nome__icontains=q)
    try:
        visitantes_qs = visitantes_qs.order_by(order)
    except Exception:
        visitantes_qs = visitantes_qs.order_by("nome")

    paginator = Paginator(visitantes_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    atendentes = Attendente.objects.all().order_by("nome")

    # Adicionar estatísticas de atendimentos para cada visitante
    visitantes_com_stats = []
    for visitante in page_obj.object_list:
        # Calcular estatísticas de atendimentos
        atendimentos_stats = {
            "concluidos": visitante.atendimentos.filter(
                status=AtendimentoStatus.CONCLUIDO
            ).count(),
            "aguardando": visitante.atendimentos.filter(
                status=AtendimentoStatus.AGUARDANDO
            ).count(),
            "em_atendimento": visitante.atendimentos.filter(
                status=AtendimentoStatus.EM_ATENDIMENTO
            ).count(),
            "cancelados": visitante.atendimentos.filter(
                status=AtendimentoStatus.CANCELADO
            ).count(),
        }

        # Adicionar as estatísticas como atributos do visitante
        visitante.atendimentos_concluidos = atendimentos_stats["concluidos"]
        visitante.atendimentos_aguardando = atendimentos_stats["aguardando"]
        visitante.atendimentos_em_atendimento = atendimentos_stats["em_atendimento"]
        visitante.atendimentos_cancelados = atendimentos_stats["cancelados"]

        visitantes_com_stats.append(visitante)

    ctx = {
        "visitantes": visitantes_com_stats,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "sort": sort,
        "dir": direction,
        "atendentes": atendentes,
    }
    return render(request, "recepcao/visitantes_list.html", ctx)


@login_required
@user_passes_test(is_recepcionista)
def visitante_enfileirar(request, pk: int):
    visitante = get_object_or_404(Visitante, pk=pk)
    if request.method == "POST":
        pessoa_destino = request.POST.get("pessoa_destino") or None
        demanda_resumo = request.POST.get("demanda_resumo") or None
        demanda_detalhes = request.POST.get("demanda_detalhes") or None
        atendente = None
        atendente_id = request.POST.get("atendente_id")
        if atendente_id:
            try:
                atendente = Attendente.objects.get(pk=int(atendente_id))
            except Exception:
                atendente = None
        at = Atendimento.objects.create(
            visitante=visitante,
            recepcionista=request.user,
            atendente=atendente,
            pessoa_destino=pessoa_destino,
            demanda_resumo=demanda_resumo,
            demanda_detalhes=demanda_detalhes,
            status=AtendimentoStatus.AGUARDANDO,
        )
        AtendimentoEvento.objects.create(
            atendimento=at, tipo=TipoEvento.CHEGADA, usuario=request.user
        )
        # Broadcast chegada para sincronização em tempo real
        try:
            agu = Atendimento.objects.filter(
                status=AtendimentoStatus.AGUARDANDO
            ).count()
            emat = Atendimento.objects.filter(
                status=AtendimentoStatus.EM_ATENDIMENTO
            ).count()
            event_uuid = str(uuid.uuid4())
            payload = {
                "type": "recepcao_update",
                "action": "chegada",
                "id": at.id,
                "chegada": (
                    at.horario_chegada.isoformat() if at.horario_chegada else None
                ),
                "visitante": visitante.nome,
                "atendente": getattr(atendente, "nome", None),
                "kpis": {"aguardando": agu, "em_atendimento": emat},
                "event_uuid": event_uuid,
                "demanda_resumo": demanda_resumo or "",
                "demanda_detalhes": demanda_detalhes or "",
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notify_recepcao", payload)
        except Exception:
            pass
        # Resposta AJAX (sem reload)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "ok": True,
                    "event_uuid": event_uuid,
                    **{k: v for k, v in payload.items() if k != "type"},
                }
            )
        # Notificação
        from django.contrib import messages

        messages.success(request, f"{visitante.nome} adicionado à fila com sucesso.")
        return redirect("recepcao:visitantes_list")
    # GET mostra um formulário simples na página de detalhe ou redireciona
    return redirect("recepcao:visitante_detail", pk=pk)


@login_required
@user_passes_test(is_recepcionista)
def visitante_delete(request, pk: int):
    visitante = get_object_or_404(Visitante, pk=pk)
    if request.method == "POST":
        nome = visitante.nome
        visitante.delete()
        from django.contrib import messages

        messages.success(request, f"{nome} removido com sucesso.")
        return redirect("recepcao:visitantes_list")
    raise Http404()


@login_required
@user_passes_test(is_recepcionista)
def visitante_create(request):
    if request.method == "POST":
        try:
            nome = request.POST.get("nome", "").strip()
            if not nome:
                cidades_mt = Cidade.objects.filter(uf_cidade__iexact="MT").order_by(
                    "nome_cidade"
                )
                atendentes = Attendente.objects.all().order_by("nome")
                return render(
                    request,
                    "recepcao/visitante_form.html",
                    {
                        "error": "Informe o nome do visitante.",
                        "cidades_mt": cidades_mt,
                        "atendentes": atendentes,
                    },
                )

            # Criar o visitante
            visitante = Visitante.objects.create(
                nome=nome,
                telefone=request.POST.get("telefone") or None,
                funcao=request.POST.get("funcao") or None,
                municipio=request.POST.get("municipio") or None,
                email=request.POST.get("email") or None,
                data_nascimento=request.POST.get("data_nascimento") or None,
                criado_por=request.user,
            )

            # Enfileirar direto, se solicitado
            if request.POST.get("enfileirar") == "1":
                atendente = None
                atendente_id = request.POST.get("atendente_id")
                if atendente_id:
                    try:
                        atendente = Attendente.objects.get(pk=int(atendente_id))
                    except Exception:
                        atendente = None

                # Criar demanda se fornecida
                demanda_resumo = request.POST.get("demanda_resumo", "").strip()
                demanda_detalhes = request.POST.get("demanda_detalhes", "").strip()

                Atendimento.objects.create(
                    visitante=visitante,
                    recepcionista=request.user,
                    atendente=atendente,
                    status=AtendimentoStatus.AGUARDANDO,
                    demanda_resumo=demanda_resumo or None,
                    demanda_detalhes=demanda_detalhes or None,
                )

            # Redirecionar para a lista de visitantes
            return redirect("recepcao:visitantes_list")

        except Exception as e:
            # Log do erro para debug
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao criar visitante: {e!s}")

            cidades_mt = Cidade.objects.filter(uf_cidade__iexact="MT").order_by(
                "nome_cidade"
            )
            atendentes = Attendente.objects.all().order_by("nome")
            return render(
                request,
                "recepcao/visitante_form.html",
                {
                    "error": f"Erro ao salvar visitante: {e!s}",
                    "cidades_mt": cidades_mt,
                    "atendentes": atendentes,
                },
            )

    cidades_mt = Cidade.objects.filter(uf_cidade__iexact="MT").order_by("nome_cidade")
    atendentes = Attendente.objects.all().order_by("nome")
    return render(
        request,
        "recepcao/visitante_form.html",
        {"cidades_mt": cidades_mt, "atendentes": atendentes},
    )


@login_required
@user_passes_test(is_recepcionista)
def visitante_detail(request, pk: int):
    visitante = get_object_or_404(Visitante, pk=pk)
    atendimentos = visitante.atendimentos.all().order_by("-horario_chegada")
    cidades_mt = Cidade.objects.filter(uf_cidade__iexact="MT").order_by("nome_cidade")
    atendentes = Attendente.objects.all().order_by("nome")
    return render(
        request,
        "recepcao/visitante_detail.html",
        {
            "visitante": visitante,
            "atendimentos": atendimentos,
            "cidades_mt": cidades_mt,
            "atendentes": atendentes,
        },
    )


@login_required
@user_passes_test(is_recepcionista)
def visitante_update(request, pk: int):
    visitante = get_object_or_404(Visitante, pk=pk)
    view_mode = request.GET.get("view") == "1"
    if request.method == "POST" and not view_mode:
        visitante.nome = request.POST.get("nome") or visitante.nome
        visitante.telefone = request.POST.get("telefone") or None
        visitante.funcao = request.POST.get("funcao") or None
        visitante.municipio = request.POST.get("municipio") or None
        visitante.email = request.POST.get("email") or None
        visitante.data_nascimento = request.POST.get("data_nascimento") or None
        if request.FILES.get("foto"):
            visitante.foto = request.FILES["foto"]
        visitante.save()
        from django.urls import reverse

        return redirect(
            reverse("recepcao:visitante_update", kwargs={"pk": visitante.pk})
            + "?view=1"
        )
    cidades_mt = Cidade.objects.filter(uf_cidade__iexact="MT").order_by("nome_cidade")
    atendentes = Attendente.objects.all().order_by("nome")

    # Calcular estatísticas de atendimentos para o histórico
    atendimentos_stats = {
        "concluidos": visitante.atendimentos.filter(
            status=AtendimentoStatus.CONCLUIDO
        ).count(),
        "aguardando": visitante.atendimentos.filter(
            status=AtendimentoStatus.AGUARDANDO
        ).count(),
        "em_atendimento": visitante.atendimentos.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO
        ).count(),
        "cancelados": visitante.atendimentos.filter(
            status=AtendimentoStatus.CANCELADO
        ).count(),
    }

    return render(
        request,
        "recepcao/visitante_form.html",
        {
            "visitante": visitante,
            "view_mode": view_mode,
            "cidades_mt": cidades_mt,
            "atendentes": atendentes,
            "atendimentos_concluidos": atendimentos_stats["concluidos"],
            "atendimentos_aguardando": atendimentos_stats["aguardando"],
            "atendimentos_em_atendimento": atendimentos_stats["em_atendimento"],
            "atendimentos_cancelados": atendimentos_stats["cancelados"],
        },
    )


@login_required
@user_passes_test(is_supervisor)
def atendentes(request):
    # agora gerenciamos Attendente modelo simples
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            nome = request.POST.get("nome")
            if nome:
                Attendente.objects.create(nome=nome)
        elif action == "update":
            uid = request.POST.get("user_id")
            nome = request.POST.get("nome")
            if uid and nome:
                try:
                    a = Attendente.objects.get(pk=int(uid))
                    a.nome = nome
                    a.save()
                except Exception:
                    pass
        elif action == "remove":
            uid = request.POST.get("user_id")
            try:
                a = Attendente.objects.get(pk=int(uid))
                a.delete()
            except Exception:
                pass
        return redirect("recepcao:atendentes")

    atendentes_qs = Attendente.objects.all().order_by("nome")

    # Adicionar estatísticas de atendimentos para cada atendente
    atendentes_com_stats = []
    for atendente in atendentes_qs:
        # Calcular estatísticas de atendimentos
        atendimentos_stats = {
            "concluidos": Atendimento.objects.filter(
                atendente=atendente, status=AtendimentoStatus.CONCLUIDO
            ).count(),
            "em_andamento": Atendimento.objects.filter(
                atendente=atendente, status=AtendimentoStatus.EM_ATENDIMENTO
            ).count(),
        }

        # Adicionar as estatísticas como atributos do atendente
        atendente.atendimentos_concluidos = atendimentos_stats["concluidos"]
        atendente.atendimentos_em_andamento = atendimentos_stats["em_andamento"]

        atendentes_com_stats.append(atendente)

    return render(
        request, "recepcao/atendentes.html", {"atendentes": atendentes_com_stats}
    )


@login_required
@user_passes_test(is_recepcionista)
def chamar_proximo(request):
    # pega o mais antigo aguardando
    prox = (
        Atendimento.objects.filter(status=AtendimentoStatus.AGUARDANDO)
        .order_by("horario_chegada")
        .first()
    )
    if not prox:
        # Se AJAX, retorna JSON amigável
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "message": "Não há pessoas aguardando."})
        return redirect("recepcao:dashboard")
    # garante recepcionista automaticamente se não estiver definido
    if not prox.recepcionista:
        prox.recepcionista = request.user
    prox.status = AtendimentoStatus.EM_ATENDIMENTO
    prox.inicio_atendimento = timezone.now()
    # não atribuímos request.user ao campo atendente (é FK para Attendente)
    prox.save()

    # create events but avoid duplicates: create CHAMADO and INICIO only if not recently created
    def _create_event_if_not_recent(
        at: Atendimento, tipo: str, usuario, window_seconds=5
    ):
        last = at.eventos.order_by("-timestamp").first()
        if (
            last
            and last.tipo == tipo
            and (dj_timezone.now() - last.timestamp).total_seconds() < window_seconds
        ):
            return None
        return AtendimentoEvento.objects.create(
            atendimento=at, tipo=tipo, usuario=usuario
        )

    _create_event_if_not_recent(prox, TipoEvento.CHAMADO, request.user)
    _create_event_if_not_recent(prox, TipoEvento.INICIO, request.user)
    # Se for requisição AJAX, devolve JSON e notifica via WS, sem navegar
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        agu = Atendimento.objects.filter(status=AtendimentoStatus.AGUARDANDO).count()
        emat = Atendimento.objects.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO
        ).count()
        atendente_name = None
        try:
            atendente_name = (
                getattr(prox.atendente, "nome", None)
                or getattr(
                    prox.atendente, "get_full_name", lambda: str(prox.atendente)
                )()
            )
        except Exception:
            atendente_name = str(prox.atendente)
        event_uuid = str(uuid.uuid4())
        payload = {
            "type": "recepcao_update",
            "action": "iniciar",
            "id": prox.id,
            "inicio": (
                prox.inicio_atendimento.isoformat() if prox.inicio_atendimento else None
            ),
            "visitante": prox.visitante.nome,
            "atendente": atendente_name,
            "kpis": {"aguardando": agu, "em_atendimento": emat},
            "event_uuid": event_uuid,
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notify_recepcao", payload)
        except Exception:
            pass
        return JsonResponse(
            {
                "ok": True,
                "event_uuid": event_uuid,
                **{k: v for k, v in payload.items() if k != "type"},
            }
        )

    return redirect("recepcao:atendimento_detail", pk=prox.pk)


@login_required
@user_passes_test(is_recepcionista)
def atendimento_detail(request, pk: int):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    return render(
        request, "recepcao/atendimento_detail.html", {"atendimento": atendimento}
    )


@login_required
@user_passes_test(is_recepcionista)
def atendimento_iniciar(request, pk: int):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if atendimento.status == AtendimentoStatus.AGUARDANDO:
        atendimento.status = AtendimentoStatus.EM_ATENDIMENTO
        # garante recepcionista automaticamente se não estiver definido
        if not atendimento.recepcionista:
            atendimento.recepcionista = request.user
        atendimento.inicio_atendimento = timezone.now()
        atendimento.save()
        # avoid duplicate INICIO events created in short succession
        last = atendimento.eventos.order_by("-timestamp").first()
        if not (
            last
            and last.tipo == TipoEvento.INICIO
            and (dj_timezone.now() - last.timestamp).total_seconds() < 5
        ):
            AtendimentoEvento.objects.create(
                atendimento=atendimento, tipo=TipoEvento.INICIO, usuario=request.user
            )
    # Se for requisição AJAX, devolve JSON com info mínima para atualizar UI
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        agu = Atendimento.objects.filter(status=AtendimentoStatus.AGUARDANDO).count()
        emat = Atendimento.objects.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO
        ).count()
        atendente_name = None
        try:
            atendente_name = (
                getattr(atendimento.atendente, "nome", None)
                or getattr(
                    atendimento.atendente,
                    "get_full_name",
                    lambda: str(atendimento.atendente),
                )()
            )
        except Exception:
            atendente_name = str(atendimento.atendente)
        # broadcast to reception group
        event_uuid = str(uuid.uuid4())
        payload = {
            "type": "recepcao_update",
            "action": "iniciar",
            "id": atendimento.id,
            "inicio": atendimento.inicio_atendimento.isoformat(),
            "visitante": atendimento.visitante.nome,
            "atendente": atendente_name,
            "kpis": {"aguardando": agu, "em_atendimento": emat},
            "event_uuid": event_uuid,
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notify_recepcao", payload)
        except Exception:
            pass
        return JsonResponse(
            {
                "ok": True,
                "event_uuid": event_uuid,
                **{k: v for k, v in payload.items() if k != "type"},
            }
        )
    return redirect("recepcao:atendimento_detail", pk=pk)


@login_required
@user_passes_test(is_recepcionista)
def atendimento_encerrar(request, pk: int):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if atendimento.status == AtendimentoStatus.EM_ATENDIMENTO:
        atendimento.status = AtendimentoStatus.CONCLUIDO
        atendimento.fim_atendimento = timezone.now()
        atendimento.save()
        # Evita eventos FIM duplicados em sequência curta
        last = atendimento.eventos.order_by("-timestamp").first()
        if not (
            last
            and last.tipo == TipoEvento.FIM
            and (dj_timezone.now() - last.timestamp).total_seconds() < 5
        ):
            AtendimentoEvento.objects.create(
                atendimento=atendimento, tipo=TipoEvento.FIM, usuario=request.user
            )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        agu = Atendimento.objects.filter(status=AtendimentoStatus.AGUARDANDO).count()
        emat = Atendimento.objects.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO
        ).count()
        fim_iso = (
            atendimento.fim_atendimento.isoformat()
            if atendimento.fim_atendimento
            else None
        )
        event_uuid = str(uuid.uuid4())
        # calcula total_display (fim - chegada)
        total_display = "-"
        try:
            if atendimento.fim_atendimento and atendimento.horario_chegada:
                total_seconds = int(
                    (
                        atendimento.fim_atendimento - atendimento.horario_chegada
                    ).total_seconds()
                )
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_display = f"{hours:02d}:{minutes:02d}"
        except Exception:
            total_display = "-"
        payload = {
            "type": "recepcao_update",
            "action": "encerrar",
            "id": atendimento.id,
            "chegada": (
                atendimento.horario_chegada.isoformat()
                if atendimento.horario_chegada
                else None
            ),
            "inicio": (
                atendimento.inicio_atendimento.isoformat()
                if atendimento.inicio_atendimento
                else None
            ),
            "fim": fim_iso,
            "visitante": atendimento.visitante.nome,
            "atendente": getattr(atendimento.atendente, "nome", None),
            "kpis": {"aguardando": agu, "em_atendimento": emat},
            "event_uuid": event_uuid,
            "total_display": total_display,
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notify_recepcao", payload)
        except Exception:
            pass
        return JsonResponse(
            {
                "ok": True,
                "event_uuid": event_uuid,
                **{k: v for k, v in payload.items() if k != "type"},
            }
        )
    return redirect("recepcao:atendimento_detail", pk=pk)


@login_required
@user_passes_test(is_recepcionista)
def atendimento_cancelar(request, pk: int):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    atendimento.status = AtendimentoStatus.CANCELADO
    atendimento.fim_atendimento = timezone.now()
    atendimento.save()
    # Evita eventos CANCELAMENTO duplicados em sequência curta
    last = atendimento.eventos.order_by("-timestamp").first()
    if not (
        last
        and last.tipo == TipoEvento.CANCELAMENTO
        and (dj_timezone.now() - last.timestamp).total_seconds() < 5
    ):
        AtendimentoEvento.objects.create(
            atendimento=atendimento, tipo=TipoEvento.CANCELAMENTO, usuario=request.user
        )
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        agu = Atendimento.objects.filter(status=AtendimentoStatus.AGUARDANDO).count()
        emat = Atendimento.objects.filter(
            status=AtendimentoStatus.EM_ATENDIMENTO
        ).count()
        canc = Atendimento.objects.filter(status=AtendimentoStatus.CANCELADO).count()
        event_uuid = str(uuid.uuid4())
        total_display = "-"
        try:
            if atendimento.fim_atendimento and atendimento.horario_chegada:
                total_seconds = int(
                    (
                        atendimento.fim_atendimento - atendimento.horario_chegada
                    ).total_seconds()
                )
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                total_display = f"{hours:02d}:{minutes:02d}"
        except Exception:
            total_display = "-"
        payload = {
            "type": "recepcao_update",
            "action": "cancelar",
            "id": atendimento.id,
            "chegada": (
                atendimento.horario_chegada.isoformat()
                if atendimento.horario_chegada
                else None
            ),
            "inicio": (
                atendimento.inicio_atendimento.isoformat()
                if atendimento.inicio_atendimento
                else None
            ),
            "fim": (
                atendimento.fim_atendimento.isoformat()
                if atendimento.fim_atendimento
                else None
            ),
            "visitante": atendimento.visitante.nome,
            "atendente": getattr(atendimento.atendente, "nome", None),
            "kpis": {"aguardando": agu, "em_atendimento": emat, "cancelados": canc},
            "event_uuid": event_uuid,
            "total_display": total_display,
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notify_recepcao", payload)
        except Exception:
            pass
        return JsonResponse(
            {
                "ok": True,
                "event_uuid": event_uuid,
                **{k: v for k, v in payload.items() if k != "type"},
            }
        )
    return redirect("recepcao:atendimento_detail", pk=pk)


@login_required
@user_passes_test(is_recepcionista)
def atendimento_anexar(request, pk: int):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if request.method == "POST" and request.FILES.get("arquivo"):
        AtendimentoAnexo.objects.create(
            atendimento=atendimento,
            arquivo=request.FILES["arquivo"],
            descricao=request.POST.get("descricao") or None,
            enviado_por=request.user,
        )
        AtendimentoEvento.objects.create(
            atendimento=atendimento, tipo=TipoEvento.ANEXO, usuario=request.user
        )
        return redirect("recepcao:atendimento_detail", pk=pk)
    return render(
        request, "recepcao/atendimento_anexos.html", {"atendimento": atendimento}
    )


@login_required
@user_passes_test(is_recepcionista)
def declaracao_visitante(request, pk: int):
    visitante = get_object_or_404(Visitante, pk=pk)
    # Versão simples HTML para impressão; PDF pode ser adicionado depois
    return render(
        request,
        "recepcao/declaracao_visitante.html",
        {"visitante": visitante, "agora": timezone.now()},
    )


@login_required
@user_passes_test(is_recepcionista)
def relatorios(request):
    from datetime import datetime, timedelta

    from django.db.models import Avg, Count, Q
    from django.utils import timezone

    # Período padrão: últimos 30 dias
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    inicio_30_dias = hoje - timedelta(days=30)

    # Filtros de data (se fornecidos)
    data_inicio = request.GET.get("data_inicio", inicio_30_dias.strftime("%Y-%m-%d"))
    data_fim = request.GET.get("data_fim", hoje.strftime("%Y-%m-%d"))

    try:
        dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
    except:
        dt_inicio = inicio_30_dias
        dt_fim = hoje

    # Filtro de atendimentos no período
    atendimentos_periodo = Atendimento.objects.filter(
        horario_chegada__date__gte=dt_inicio, horario_chegada__date__lte=dt_fim
    )

    # 1. Resumo Geral
    total_atendimentos = atendimentos_periodo.count()
    concluidos = atendimentos_periodo.filter(status=AtendimentoStatus.CONCLUIDO).count()
    cancelados = atendimentos_periodo.filter(status=AtendimentoStatus.CANCELADO).count()
    em_andamento = atendimentos_periodo.filter(
        status=AtendimentoStatus.EM_ATENDIMENTO
    ).count()
    aguardando = atendimentos_periodo.filter(
        status=AtendimentoStatus.AGUARDANDO
    ).count()

    # 2. Tempos médios (apenas para atendimentos concluídos)
    atendimentos_concluidos = atendimentos_periodo.filter(
        status=AtendimentoStatus.CONCLUIDO,
        inicio_atendimento__isnull=False,
        fim_atendimento__isnull=False,
    )

    # Calcular tempo médio de espera
    espera_expr = ExpressionWrapper(
        F("inicio_atendimento") - F("horario_chegada"), output_field=DurationField()
    )

    # Calcular tempo médio de atendimento
    atendimento_expr = ExpressionWrapper(
        F("fim_atendimento") - F("inicio_atendimento"), output_field=DurationField()
    )

    tempo_medio_espera = atendimentos_concluidos.aggregate(avg_espera=Avg(espera_expr))[
        "avg_espera"
    ]

    tempo_medio_atendimento = atendimentos_concluidos.aggregate(
        avg_atendimento=Avg(atendimento_expr)
    )["avg_atendimento"]

    # 3. Atendimentos por atendente
    por_atendente = (
        atendimentos_periodo.filter(atendente__isnull=False)
        .values("atendente__nome")
        .annotate(
            total=Count("id"),
            concluidos=Count("id", filter=Q(status=AtendimentoStatus.CONCLUIDO)),
            cancelados=Count("id", filter=Q(status=AtendimentoStatus.CANCELADO)),
            tempo_medio_at=Avg(
                atendimento_expr, filter=Q(status=AtendimentoStatus.CONCLUIDO)
            ),
            tempo_medio_esp=Avg(
                espera_expr, filter=Q(status=AtendimentoStatus.CONCLUIDO)
            ),
        )
        .order_by("-total")
    )

    # 4. Atendimentos por dia (últimos 30 dias)
    atendimentos_por_dia = []
    for i in range(30):
        data = hoje - timedelta(days=i)
        qtd = atendimentos_periodo.filter(horario_chegada__date=data).count()
        atendimentos_por_dia.append({"data": data.strftime("%d/%m"), "quantidade": qtd})
    atendimentos_por_dia.reverse()

    # 5. Top 5 visitantes mais frequentes
    top_visitantes = (
        atendimentos_periodo.values("visitante__nome", "visitante__id")
        .annotate(total_visitas=Count("id"))
        .order_by("-total_visitas")[:5]
    )

    # 6. Horários de maior movimento
    horarios_movimento = []
    for hora in range(8, 18):  # 8h às 17h
        qtd = atendimentos_periodo.filter(horario_chegada__hour=hora).count()
        horarios_movimento.append({"hora": f"{hora:02d}:00", "quantidade": qtd})

    # Função para formatar duração
    def fmt_td(td):
        if not td:
            return "00h00m"
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}h{minutes:02d}m"

    context = {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "total_atendimentos": total_atendimentos,
        "concluidos": concluidos,
        "cancelados": cancelados,
        "em_andamento": em_andamento,
        "aguardando": aguardando,
        "tempo_medio_espera": fmt_td(tempo_medio_espera),
        "tempo_medio_atendimento": fmt_td(tempo_medio_atendimento),
        "por_atendente": por_atendente,
        "atendimentos_por_dia": atendimentos_por_dia,
        "top_visitantes": top_visitantes,
        "horarios_movimento": horarios_movimento,
        "fmt_td": fmt_td,
    }

    return render(request, "recepcao/relatorios.html", context)


# Create your views here.
