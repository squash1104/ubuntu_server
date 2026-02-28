from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Historico, TipoAcao, TipoObjeto
from .utils import registrar_reset_senha


@login_required
def historico_list(request):
    """Lista o histórico de ações do sistema"""

    # Filtros
    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")
    acao = request.GET.get("acao", "")
    tipo_objeto = request.GET.get("tipo_objeto", "")
    usuario = request.GET.get("usuario", "")
    usuario_id = request.GET.get("usuario_id", "")
    busca = request.GET.get("busca", "")

    # Query base
    historicos = Historico.objects.select_related("usuario").all()

    # Aplicar filtros
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            historicos = historicos.filter(data_hora__date__gte=dt_inicio)
        except ValueError:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            historicos = historicos.filter(data_hora__date__lte=dt_fim)
        except ValueError:
            pass

    if acao:
        if acao == "CRIAR_USUARIO":
            historicos = historicos.filter(
                acao=TipoAcao.CRIAR, tipo_objeto=TipoObjeto.USUARIO
            )
        else:
            historicos = historicos.filter(acao=acao)

    if tipo_objeto:
        historicos = historicos.filter(tipo_objeto=tipo_objeto)

    if usuario_id:
        try:
            historicos = historicos.filter(usuario_id=int(usuario_id))
        except (TypeError, ValueError):
            pass
    elif usuario:
        historicos = historicos.filter(usuario__username__icontains=usuario)

    if busca:
        historicos = historicos.filter(
            Q(objeto_nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(usuario__first_name__icontains=busca)
            | Q(usuario__last_name__icontains=busca)
            | Q(usuario__username__icontains=busca)
        )

    # Ordenação (mais recente primeiro)
    historicos = historicos.order_by("-data_hora")

    # Paginação
    paginator = Paginator(historicos, 25)  # 25 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Estatísticas
    total_historicos = historicos.count()
    hoje = timezone.now().date()
    ontem = hoje - timedelta(days=1)
    esta_semana = hoje - timedelta(days=7)

    stats = {
        "total": total_historicos,
        "hoje": historicos.filter(data_hora__date=hoje).count(),
        "ontem": historicos.filter(data_hora__date=ontem).count(),
        "esta_semana": historicos.filter(data_hora__date__gte=esta_semana).count(),
    }

    # Ações mais comuns
    acoes_comuns = (
        historicos.values("acao").annotate(total=Count("id")).order_by("-total")[:5]
    )

    # Tipos de objeto mais afetados
    tipos_comuns = (
        historicos.values("tipo_objeto")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # Opções de ação (removendo ações da recepção) e adicionando 'Criar Usuário'
    opcoes_acao = [
        (TipoAcao.CRIAR, "Criar"),
        (TipoAcao.EDITAR, "Editar"),
        (TipoAcao.EXCLUIR, "Excluir"),
        (TipoAcao.LOGIN, "Login"),
        (TipoAcao.LOGOUT, "Logout"),
        (TipoAcao.RESET, "Reset"),
        ("CRIAR_USUARIO", "Criar Usuário"),
    ]

    # Opções de tipo de objeto (removendo Atendimento, Visitante, Sistema)
    opcoes_tipo_objeto = [
        (TipoObjeto.COLABORADOR, "Colaborador"),
        (TipoObjeto.CONVIDADO, "Convidado"),
        (TipoObjeto.USUARIO, "Usuário"),
    ]

    usuarios = User.objects.order_by("username").all()

    context = {
        "page_obj": page_obj,
        "stats": stats,
        "acoes_comuns": acoes_comuns,
        "tipos_comuns": tipos_comuns,
        "filtros": {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "acao": acao,
            "tipo_objeto": tipo_objeto,
            "usuario": usuario,
            "usuario_id": usuario_id,
            "busca": busca,
        },
        "opcoes_acao": opcoes_acao,
        "opcoes_tipo_objeto": opcoes_tipo_objeto,
        "usuarios": usuarios,
        "data_inicio_str": data_inicio,
        "data_fim_str": data_fim,
        "acao_filtro": acao,
        "tipo_objeto_filtro": tipo_objeto,
        "usuario_filtro": usuario,
        "usuario_id_filtro": usuario_id,
    }

    return render(request, "historico/historico_list.html", context)


@login_required
def historico_detail(request, pk):
    """Detalhes de um registro de histórico"""
    try:
        historico = Historico.objects.select_related("usuario").get(pk=pk)
    except Historico.DoesNotExist:
        return render(request, "404.html", status=404)

    context = {
        "historico": historico,
    }

    return render(request, "historico/historico_detail.html", context)


class PasswordResetCompleteWithLogView(PasswordResetConfirmView):
    """
    View customizada que herda do PasswordResetConfirmView do Django
    e registra no histórico quando a senha é redefinida com sucesso.
    """
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")
    post_reset_login = False

    def form_valid(self, form):
        # Salva a nova senha primeiro
        response = super().form_valid(form)
        
        # Após redefinir a senha com sucesso, registra no histórico
        # O usuário é obtido através do método get_user() da view
        # O uidb64 está disponível em self.kwargs
        uidb64 = self.kwargs.get('uidb64')
        user = self.get_user(uidb64) if uidb64 else None
        
        if user is not None:
            try:
                # Registra o reset de senha no histórico
                registrar_reset_senha(user, request=self.request)
            except Exception as e:
                # Não queremos que um erro no histórico impeça o reset de senha
                print(f"Erro ao registrar reset de senha no histórico: {e}")
        
        return response
