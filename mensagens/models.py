from typing import ClassVar

from django.contrib.auth.models import User
from django.db import models


class TipoMensagem(models.TextChoices):
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"


class StatusMensagem(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    ENVIADA = "enviada", "Enviada"
    FALHOU = "falhou", "Falhou"


class StatusCampanha(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    ENVIANDO = "enviando", "Enviando"
    CONCLUIDO = "concluido", "Concluído"
    PARCIAL = "parcial", "Parcial"
    CANCELADO = "cancelado", "Cancelado"


class CampanhaMensagem(models.Model):
    titulo = models.CharField(max_length=200)
    filtros_usados = models.JSONField(default=dict, blank=True)
    tipo_mensagem = models.CharField(max_length=10, choices=TipoMensagem.choices)
    conteudo = models.TextField()
    template_usado = models.CharField(max_length=100, blank=True, null=True)
    total_destinatarios = models.IntegerField(default=0)
    total_enviadas = models.IntegerField(default=0)
    total_falhas = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=StatusCampanha.choices, default=StatusCampanha.PENDENTE
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering: ClassVar = ["-criado_em"]
        verbose_name = "Campanha de Mensagem"
        verbose_name_plural = "Campanhas de Mensagens"

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"


class MensagemAniversario(models.Model):
    destinatario_nome = models.CharField(max_length=200)
    destinatario_telefone = models.CharField(max_length=20)
    destinatario_tipo = models.CharField(max_length=20)  # 'colaborador' ou 'convidado'
    destinatario_id = models.PositiveIntegerField()  # ID do colaborador ou convidado

    tipo_mensagem = models.CharField(max_length=10, choices=TipoMensagem.choices)
    conteudo = models.TextField()
    template_usado = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(
        max_length=10, choices=StatusMensagem.choices, default=StatusMensagem.PENDENTE
    )
    data_envio = models.DateTimeField(auto_now_add=True)
    data_processamento = models.DateTimeField(blank=True, null=True)

    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    erro_detalhes = models.TextField(blank=True, null=True)

    # Metadados da API externa
    api_message_id = models.CharField(max_length=200, blank=True, null=True)
    api_response = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-data_envio"]
        verbose_name = "Mensagem de Aniversário"
        verbose_name_plural = "Mensagens de Aniversário"

    def __str__(self):
        return f"{self.destinatario_nome} - {self.get_tipo_mensagem_display()} - {self.get_status_display()}"


class Mensagem(models.Model):
    campanha = models.ForeignKey(
        CampanhaMensagem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mensagens",
    )
    destinatario_nome = models.CharField(max_length=200)
    destinatario_telefone = models.CharField(max_length=20)
    destinatario_tipo = models.CharField(max_length=20)
    destinatario_id = models.PositiveIntegerField()
    tipo_mensagem = models.CharField(max_length=10, choices=TipoMensagem.choices)
    conteudo = models.TextField()
    template_usado = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=StatusMensagem.choices, default=StatusMensagem.PENDENTE
    )
    data_envio = models.DateTimeField(auto_now_add=True)
    data_processamento = models.DateTimeField(null=True, blank=True)
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    erro_detalhes = models.TextField(blank=True, null=True)
    api_message_id = models.CharField(max_length=200, blank=True, null=True)
    api_response = models.JSONField(blank=True, null=True)

    class Meta:
        ordering: ClassVar = ["-data_envio"]
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"

    def __str__(self):
        tipo = self.get_tipo_mensagem_display()
        status = self.get_status_display()
        return f"{self.destinatario_nome} - {tipo} - {status}"


class TemplateMensagem(models.Model):
    nome = models.CharField(max_length=100)
    tipo_mensagem = models.CharField(max_length=10, choices=TipoMensagem.choices)
    conteudo = models.TextField(
        help_text="Use {nome} para o nome da pessoa e {idade} para a idade"
    )
    imagem = models.URLField(blank=True, default="")
    meta_template_name = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Nome do template aprovado no Meta Business (ex: promocao_maio). Deixe vazio para enviar como texto livre."
    )
    meta_template_language = models.CharField(
        max_length=10, blank=True, default="pt_BR"
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Template de Mensagem"
        verbose_name_plural = "Templates de Mensagem"

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_mensagem_display()})"
