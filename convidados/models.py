from typing import ClassVar

from django.db import models

from colaboradores.models import Colaborador
from geografia.models import Bairro, Cidade


class Convidado(models.Model):
    # O Django criará automaticamente um campo 'id' como chave primária (PK)
    nome = models.CharField(max_length=100)  # Coluna no DB será 'nome'
    telefone = models.CharField(
        max_length=20, blank=True, null=True
    )  # Coluna no DB será 'telefone'

    data_nascimento = models.DateField(null=True, blank=True)

    # ForeignKeys para Cidade, Bairro e Colaborador.
    # O Django criará 'cidade_id', 'bairro_id', 'colaborador_id' no DB.
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="convidados",
    )

    data_cadastro = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "convidados"  # A tabela no DB será 'convidados'
        verbose_name = "Convidado"
        verbose_name_plural = "Convidados"
        ordering: ClassVar = ["nome"]

    def __str__(self):
        return self.nome
