from django.contrib.auth.models import User
from django.db import models


class Visitante(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    funcao = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to="recepcao/fotos/", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.nome


class AtendimentoStatus(models.TextChoices):
    AGUARDANDO = "aguardando", "Aguardando"
    EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
    CONCLUIDO = "concluido", "Concluído"
    CANCELADO = "cancelado", "Cancelado"
    AUSENTE = "ausente", "Ausente"


class Atendimento(models.Model):
    visitante = models.ForeignKey(
        Visitante, on_delete=models.CASCADE, related_name="atendimentos"
    )
    recepcionista = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atendimentos_recebidos",
    )
    # Atendente será um modelo específico para a recepção (nome simples)
    atendente = models.ForeignKey(
        "recepcao.Attendente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atendimentos_assumidos",
    )
    pessoa_destino = models.CharField(
        max_length=150, blank=True, null=True, help_text="Com quem veio falar"
    )

    status = models.CharField(
        max_length=20,
        choices=AtendimentoStatus.choices,
        default=AtendimentoStatus.AGUARDANDO,
    )

    demanda_resumo = models.CharField(max_length=200, blank=True, null=True)
    demanda_detalhes = models.TextField(blank=True, null=True)

    horario_chegada = models.DateTimeField(auto_now_add=True)
    inicio_atendimento = models.DateTimeField(blank=True, null=True)
    fim_atendimento = models.DateTimeField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-horario_chegada"]

    def __str__(self) -> str:
        return f"Atendimento {self.id} - {self.visitante.nome}"

    @property
    def tempo_espera(self):
        if self.inicio_atendimento:
            return self.inicio_atendimento - self.horario_chegada
        return None

    @property
    def tempo_em_atendimento(self):
        if self.inicio_atendimento and self.fim_atendimento:
            return self.fim_atendimento - self.inicio_atendimento
        return None


class AtendimentoAnexo(models.Model):
    atendimento = models.ForeignKey(
        Atendimento, on_delete=models.CASCADE, related_name="anexos"
    )
    arquivo = models.FileField(upload_to="recepcao/anexos/")
    descricao = models.CharField(max_length=200, blank=True, null=True)
    enviado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.descricao or self.arquivo.name


class TipoEvento(models.TextChoices):
    CHEGADA = "chegada", "Chegada"
    CHAMADO = "chamado", "Chamado para atendimento"
    INICIO = "inicio", "Início do atendimento"
    FIM = "fim", "Fim do atendimento"
    CANCELAMENTO = "cancelamento", "Cancelamento"
    AUSENTE = "ausente", "Ausente"
    NOTA = "nota", "Nota"
    ANEXO = "anexo", "Anexo adicionado"


class AtendimentoEvento(models.Model):
    atendimento = models.ForeignKey(
        Atendimento, on_delete=models.CASCADE, related_name="eventos"
    )
    tipo = models.CharField(max_length=20, choices=TipoEvento.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    detalhes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.timestamp:%d/%m/%Y %H:%M}"


# Create your models here.


class Attendente(models.Model):
    nome = models.CharField(max_length=150)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome
