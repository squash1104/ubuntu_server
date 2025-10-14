from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TipoAcao(models.TextChoices):
    """Tipos de ações que podem ser registradas no histórico"""

    CRIAR = "CRIAR", "Criar"
    EDITAR = "EDITAR", "Editar"
    EXCLUIR = "EXCLUIR", "Excluir"
    VISUALIZAR = "VISUALIZAR", "Visualizar"
    ENFILEIRAR = "ENFILEIRAR", "Enfileirar"
    INICIAR_ATENDIMENTO = "INICIAR_ATENDIMENTO", "Iniciar Atendimento"
    CONCLUIR_ATENDIMENTO = "CONCLUIR_ATENDIMENTO", "Concluir Atendimento"
    CANCELAR_ATENDIMENTO = "CANCELAR_ATENDIMENTO", "Cancelar Atendimento"
    LOGIN = "LOGIN", "Login"
    LOGOUT = "LOGOUT", "Logout"


class TipoObjeto(models.TextChoices):
    """Tipos de objetos que podem ter histórico"""

    COLABORADOR = "COLABORADOR", "Colaborador"
    CONVIDADO = "CONVIDADO", "Convidado"
    ATENDIMENTO = "ATENDIMENTO", "Atendimento"
    VISITANTE = "VISITANTE", "Visitante"
    USUARIO = "USUARIO", "Usuário"
    SISTEMA = "SISTEMA", "Sistema"


class Historico(models.Model):
    """Modelo para registrar histórico de ações no sistema"""

    # Informações básicas
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário"
    )
    acao = models.CharField(
        max_length=50, choices=TipoAcao.choices, verbose_name="Ação"
    )
    tipo_objeto = models.CharField(
        max_length=50, choices=TipoObjeto.choices, verbose_name="Tipo de Objeto"
    )

    # Informações do objeto afetado
    objeto_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="ID do Objeto"
    )
    objeto_nome = models.CharField(max_length=255, verbose_name="Nome do Objeto")

    # Detalhes da ação
    descricao = models.TextField(
        verbose_name="Descrição", help_text="Descrição detalhada da ação realizada"
    )
    detalhes_antes = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Detalhes Antes",
        help_text="Estado do objeto antes da ação (para edições)",
    )
    detalhes_depois = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Detalhes Depois",
        help_text="Estado do objeto depois da ação",
    )

    # Metadados
    data_hora = models.DateTimeField(default=timezone.now, verbose_name="Data e Hora")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="Endereço IP"
    )
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")

    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Histórico"
        verbose_name_plural = "Históricos"
        ordering = ["-data_hora"]
        indexes = [
            models.Index(fields=["-data_hora"]),
            models.Index(fields=["tipo_objeto", "acao"]),
            models.Index(fields=["usuario", "-data_hora"]),
            models.Index(fields=["objeto_id", "tipo_objeto"]),
        ]

    def __str__(self):
        return f"{self.get_acao_display()} {self.get_tipo_objeto_display()}: {self.objeto_nome}"

    @property
    def acao_icon(self):
        """Retorna o ícone Bootstrap correspondente à ação"""
        icons = {
            TipoAcao.CRIAR: "bi-plus-circle",
            TipoAcao.EDITAR: "bi-pencil",
            TipoAcao.EXCLUIR: "bi-trash",
            TipoAcao.VISUALIZAR: "bi-eye",
            TipoAcao.ENFILEIRAR: "bi-queue",
            TipoAcao.INICIAR_ATENDIMENTO: "bi-play-circle",
            TipoAcao.CONCLUIR_ATENDIMENTO: "bi-check-circle",
            TipoAcao.CANCELAR_ATENDIMENTO: "bi-x-circle",
            TipoAcao.LOGIN: "bi-box-arrow-in-right",
            TipoAcao.LOGOUT: "bi-box-arrow-right",
        }
        return icons.get(self.acao, "bi-info-circle")

    @property
    def acao_color(self):
        """Retorna a cor Bootstrap correspondente à ação"""
        colors = {
            TipoAcao.CRIAR: "success",
            TipoAcao.EDITAR: "warning",
            TipoAcao.EXCLUIR: "danger",
            TipoAcao.VISUALIZAR: "info",
            TipoAcao.ENFILEIRAR: "primary",
            TipoAcao.INICIAR_ATENDIMENTO: "primary",
            TipoAcao.CONCLUIR_ATENDIMENTO: "success",
            TipoAcao.CANCELAR_ATENDIMENTO: "danger",
            TipoAcao.LOGIN: "info",
            TipoAcao.LOGOUT: "secondary",
        }
        return colors.get(self.acao, "secondary")

    @property
    def tipo_objeto_icon(self):
        """Retorna o ícone Bootstrap correspondente ao tipo de objeto"""
        icons = {
            TipoObjeto.COLABORADOR: "bi-person-badge",
            TipoObjeto.CONVIDADO: "bi-person-plus",
            TipoObjeto.ATENDIMENTO: "bi-calendar-check",
            TipoObjeto.VISITANTE: "bi-person",
            TipoObjeto.USUARIO: "bi-person-circle",
            TipoObjeto.SISTEMA: "bi-gear",
        }
        return icons.get(self.tipo_objeto, "bi-file")

    def get_objeto_url(self):
        """Retorna a URL para visualizar o objeto afetado"""
        if not self.objeto_id:
            return None

        urls = {
            TipoObjeto.COLABORADOR: f"/colaboradores/editar/{self.objeto_id}/",
            TipoObjeto.CONVIDADO: f"/convidados/editar/{self.objeto_id}/",
            TipoObjeto.ATENDIMENTO: f"/recepcao/atendimento/{self.objeto_id}/",
            TipoObjeto.VISITANTE: f"/recepcao/visitante/editar/{self.objeto_id}/",
        }
        return urls.get(self.tipo_objeto)
