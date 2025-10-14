from django.contrib.auth.models import User
from django.db import models


class TipoMensagem(models.TextChoices):
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"


class StatusMensagem(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    ENVIADA = "enviada", "Enviada"
    FALHOU = "falhou", "Falhou"


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


class TemplateMensagem(models.Model):
    nome = models.CharField(max_length=100)
    tipo_mensagem = models.CharField(max_length=10, choices=TipoMensagem.choices)
    conteudo = models.TextField(
        help_text="Use {nome} para o nome da pessoa e {idade} para a idade"
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
