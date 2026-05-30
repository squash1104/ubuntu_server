from typing import ClassVar

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from geografia.models import Bairro, Cidade

COR_CHOICES = [
    ("success", "Verde"),
    ("primary", "Azul"),
    ("danger", "Vermelho"),
    ("warning", "Amarelo"),
    ("info", "Azul Claro"),
    ("secondary", "Cinza"),
    ("dark", "Preto"),
    ("purple", "Roxo"),
    ("pink", "Rosa"),
    ("orange", "Laranja"),
    ("teal", "Verde Azulado"),
    ("cyan", "Ciano"),
    ("indigo", "Índigo"),
    ("brown", "Marrom"),
    ("lime", "Lima"),
    ("coral", "Coral"),
    ("navy", "Marinho"),
    ("olive", "Oliva"),
]


COR_MAP_HEX = {
    "success": "#198754",
    "primary": "#0d6efd",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0",
    "secondary": "#6c757d",
}


class TipoColaborador(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    cor = models.CharField(max_length=20, choices=COR_CHOICES, default="success")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    responsaveis = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="Usuários responsáveis",
    )

    class Meta:
        db_table = "tipos_colaborador"
        verbose_name = "Tipo de Colaborador"
        verbose_name_plural = "Tipos de Colaborador"
        ordering: ClassVar = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def cor_css(self):
        return COR_MAP_HEX.get(self.cor, self.cor)


class Colaborador(models.Model):
    # O Django criará automaticamente um campo 'id' como chave primária (PK)
    nome = models.CharField(max_length=100)  # Coluna no DB será 'nome'
    telefone = models.CharField(
        max_length=20, blank=True, null=True
    )  # Coluna no DB será 'telefone'

    data_nascimento = models.DateField(null=True, blank=True)

    # ForeignKeys para Cidade e Bairro. O Django criará 'cidade_id' e 'bairro_id' no DB.
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)

    tipo = models.ForeignKey(
        TipoColaborador,
        on_delete=models.PROTECT,
        related_name="colaboradores",
        verbose_name="Tipo",
        default=1,  # Será definido durante a migração
    )

    data_cadastro = models.DateTimeField(auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "colaboradores"  # A tabela no DB será 'colaboradores'
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering: ClassVar = ["nome"]

    def __str__(self):
        return self.nome
