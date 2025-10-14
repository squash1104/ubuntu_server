from datetime import date, datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Historico, TipoAcao, TipoObjeto


def registrar_acao(
    acao: str,
    tipo_objeto: str,
    objeto_nome: str,
    descricao: str,
    usuario: User = None,
    objeto_id: int = None,
    detalhes_antes: dict = None,
    detalhes_depois: dict = None,
    request=None,
):
    """
    Registra uma ação no histórico do sistema

    Args:
        acao: Tipo de ação (TipoAcao)
        tipo_objeto: Tipo do objeto afetado (TipoObjeto)
        objeto_nome: Nome do objeto afetado
        descricao: Descrição da ação
        usuario: Usuário que realizou a ação (opcional)
        objeto_id: ID do objeto afetado (opcional)
        detalhes_antes: Estado anterior do objeto (opcional)
        detalhes_depois: Estado posterior do objeto (opcional)
        request: Request HTTP para capturar IP e User Agent (opcional)
    """

    # Capturar IP e User Agent se request for fornecido
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

    # Sanitizar estruturas JSON (converter date/datetime e objetos em strings)
    def _to_json_serializable(value):
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        # Django models e FKs
        try:
            # Usar representação de string para objetos não-serializáveis
            from django.db.models import Model  # import local para evitar custo global

            if isinstance(value, Model):
                return str(value)
        except Exception:
            pass
        if isinstance(value, dict):
            return {str(k): _to_json_serializable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_to_json_serializable(v) for v in list(value)]
        # Fallback: string
        return str(value)

    detalhes_antes = _to_json_serializable(detalhes_antes)
    detalhes_depois = _to_json_serializable(detalhes_depois)

    # Criar registro de histórico
    historico = Historico.objects.create(
        usuario=usuario,
        acao=acao,
        tipo_objeto=tipo_objeto,
        objeto_id=objeto_id,
        objeto_nome=objeto_nome,
        descricao=descricao,
        detalhes_antes=detalhes_antes,
        detalhes_depois=detalhes_depois,
        ip_address=ip_address,
        user_agent=user_agent,
        data_hora=timezone.now(),
    )

    # Enviar notificação em tempo real via WebSocket
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "historico_updates",
                {
                    "type": "historico.novo",
                    "historico": {
                        "id": historico.id,
                        "data_hora": historico.data_hora.strftime("%d/%m %H:%M"),
                        "acao": historico.get_acao_display(),
                        "acao_valor": historico.acao,
                        "acao_color": historico.acao_color,
                        "descricao": historico.descricao,
                        "usuario": (
                            historico.usuario.get_full_name()
                            or historico.usuario.username
                            if historico.usuario
                            else "Sistema"
                        ),
                    },
                },
            )
    except Exception as e:
        # Não queremos que um erro no WebSocket impeça o registro
        print(f"Erro ao enviar notificação WebSocket: {e}")

    return historico


def get_client_ip(request):
    """Obtém o IP real do cliente considerando proxies"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def registrar_criacao_colaborador(colaborador, usuario, request=None):
    """Registra a criação de um colaborador (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.CRIAR,
        tipo_objeto=TipoObjeto.COLABORADOR,
        objeto_nome=colaborador.nome,
        descricao=f"Colaborador '{colaborador.nome}' foi criado",
        usuario=usuario,
        objeto_id=colaborador.id,
        detalhes_depois={
            "nome": colaborador.nome,
            "telefone": colaborador.telefone,
            "data_nascimento": getattr(colaborador, "data_nascimento", None),
            "cidade": (
                str(getattr(colaborador, "cidade", None))
                if getattr(colaborador, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(colaborador, "bairro", None))
                if getattr(colaborador, "bairro", None)
                else None
            ),
            "cadastrado_por": getattr(
                getattr(colaborador, "cadastrado_por", None), "username", None
            ),
        },
        request=request,
    )


def registrar_edicao_colaborador(colaborador, usuario, dados_antes, request=None):
    """Registra a edição de um colaborador (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.EDITAR,
        tipo_objeto=TipoObjeto.COLABORADOR,
        objeto_nome=colaborador.nome,
        descricao=f"Colaborador '{colaborador.nome}' foi editado",
        usuario=usuario,
        objeto_id=colaborador.id,
        detalhes_antes=dados_antes,
        detalhes_depois={
            "nome": colaborador.nome,
            "telefone": colaborador.telefone,
            "data_nascimento": getattr(colaborador, "data_nascimento", None),
            "cidade": (
                str(getattr(colaborador, "cidade", None))
                if getattr(colaborador, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(colaborador, "bairro", None))
                if getattr(colaborador, "bairro", None)
                else None
            ),
            "cadastrado_por": getattr(
                getattr(colaborador, "cadastrado_por", None), "username", None
            ),
        },
        request=request,
    )


def registrar_exclusao_colaborador(colaborador, usuario, request=None):
    """Registra a exclusão de um colaborador (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.EXCLUIR,
        tipo_objeto=TipoObjeto.COLABORADOR,
        objeto_nome=colaborador.nome,
        descricao=f"Colaborador '{colaborador.nome}' foi excluído",
        usuario=usuario,
        objeto_id=colaborador.id,
        detalhes_antes={
            "nome": colaborador.nome,
            "telefone": colaborador.telefone,
            "data_nascimento": getattr(colaborador, "data_nascimento", None),
            "cidade": (
                str(getattr(colaborador, "cidade", None))
                if getattr(colaborador, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(colaborador, "bairro", None))
                if getattr(colaborador, "bairro", None)
                else None
            ),
            "cadastrado_por": getattr(
                getattr(colaborador, "cadastrado_por", None), "username", None
            ),
        },
        request=request,
    )


def registrar_criacao_convidado(convidado, usuario, request=None):
    """Registra a criação de um convidado (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.CRIAR,
        tipo_objeto=TipoObjeto.CONVIDADO,
        objeto_nome=convidado.nome,
        descricao=f"Convidado '{convidado.nome}' foi criado",
        usuario=usuario,
        objeto_id=convidado.id,
        detalhes_depois={
            "nome": convidado.nome,
            "telefone": convidado.telefone,
            "data_nascimento": getattr(convidado, "data_nascimento", None),
            "cidade": (
                str(getattr(convidado, "cidade", None))
                if getattr(convidado, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(convidado, "bairro", None))
                if getattr(convidado, "bairro", None)
                else None
            ),
            "colaborador": (
                str(getattr(convidado, "colaborador", None))
                if getattr(convidado, "colaborador", None)
                else None
            ),
        },
        request=request,
    )


def registrar_edicao_convidado(convidado, usuario, dados_antes, request=None):
    """Registra a edição de um convidado (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.EDITAR,
        tipo_objeto=TipoObjeto.CONVIDADO,
        objeto_nome=convidado.nome,
        descricao=f"Convidado '{convidado.nome}' foi editado",
        usuario=usuario,
        objeto_id=convidado.id,
        detalhes_antes=dados_antes,
        detalhes_depois={
            "nome": convidado.nome,
            "telefone": convidado.telefone,
            "data_nascimento": getattr(convidado, "data_nascimento", None),
            "cidade": (
                str(getattr(convidado, "cidade", None))
                if getattr(convidado, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(convidado, "bairro", None))
                if getattr(convidado, "bairro", None)
                else None
            ),
            "colaborador": (
                str(getattr(convidado, "colaborador", None))
                if getattr(convidado, "colaborador", None)
                else None
            ),
        },
        request=request,
    )


def registrar_exclusao_convidado(convidado, usuario, request=None):
    """Registra a exclusão de um convidado (campos alinhados ao modelo atual)."""
    return registrar_acao(
        acao=TipoAcao.EXCLUIR,
        tipo_objeto=TipoObjeto.CONVIDADO,
        objeto_nome=convidado.nome,
        descricao=f"Convidado '{convidado.nome}' foi excluído",
        usuario=usuario,
        objeto_id=convidado.id,
        detalhes_antes={
            "nome": convidado.nome,
            "telefone": convidado.telefone,
            "data_nascimento": getattr(convidado, "data_nascimento", None),
            "cidade": (
                str(getattr(convidado, "cidade", None))
                if getattr(convidado, "cidade", None)
                else None
            ),
            "bairro": (
                str(getattr(convidado, "bairro", None))
                if getattr(convidado, "bairro", None)
                else None
            ),
            "colaborador": (
                str(getattr(convidado, "colaborador", None))
                if getattr(convidado, "colaborador", None)
                else None
            ),
        },
        request=request,
    )


def registrar_atendimento(atendimento, acao, usuario, request=None):
    """Registra ações relacionadas a atendimentos"""
    acao_map = {
        "enfileirar": TipoAcao.ENFILEIRAR,
        "iniciar": TipoAcao.INICIAR_ATENDIMENTO,
        "concluir": TipoAcao.CONCLUIR_ATENDIMENTO,
        "cancelar": TipoAcao.CANCELAR_ATENDIMENTO,
    }

    descricao_map = {
        "enfileirar": f"Visitante '{atendimento.visitante.nome}' foi adicionado à fila",
        "iniciar": f"Atendimento de '{atendimento.visitante.nome}' foi iniciado",
        "concluir": f"Atendimento de '{atendimento.visitante.nome}' foi concluído",
        "cancelar": f"Atendimento de '{atendimento.visitante.nome}' foi cancelado",
    }

    return registrar_acao(
        acao=acao_map.get(acao, TipoAcao.VISUALIZAR),
        tipo_objeto=TipoObjeto.ATENDIMENTO,
        objeto_nome=f"Atendimento #{atendimento.id} - {atendimento.visitante.nome}",
        descricao=descricao_map.get(acao, f"Ação '{acao}' realizada no atendimento"),
        usuario=usuario,
        objeto_id=atendimento.id,
        request=request,
    )


def registrar_login(usuario, request=None):
    """Registra o login de um usuário"""
    nome_completo = usuario.get_full_name() or usuario.username
    return registrar_acao(
        acao=TipoAcao.LOGIN,
        tipo_objeto=TipoObjeto.USUARIO,
        objeto_nome=nome_completo,
        descricao=f"Usuário '{nome_completo}' fez login no sistema",
        usuario=usuario,
        objeto_id=usuario.id,
        request=request,
    )


def registrar_logout(usuario, request=None):
    """Registra o logout de um usuário"""
    nome_completo = usuario.get_full_name() or usuario.username
    return registrar_acao(
        acao=TipoAcao.LOGOUT,
        tipo_objeto=TipoObjeto.USUARIO,
        objeto_nome=nome_completo,
        descricao=f"Usuário '{nome_completo}' fez logout do sistema",
        usuario=usuario,
        objeto_id=usuario.id,
        request=request,
    )


def registrar_criacao_usuario(usuario_criado, criado_por, request=None):
    """Registra a criação de um novo usuário"""
    nome_completo = usuario_criado.get_full_name() or usuario_criado.username
    return registrar_acao(
        acao=TipoAcao.CRIAR,
        tipo_objeto=TipoObjeto.USUARIO,
        objeto_nome=nome_completo,
        descricao=f"Usuário '{nome_completo}' foi criado",
        usuario=criado_por,
        objeto_id=usuario_criado.id,
        detalhes_depois={
            "username": usuario_criado.username,
            "email": usuario_criado.email,
            "first_name": usuario_criado.first_name,
            "last_name": usuario_criado.last_name,
            "is_staff": usuario_criado.is_staff,
            "is_active": usuario_criado.is_active,
            "is_superuser": usuario_criado.is_superuser,
        },
        request=request,
    )
