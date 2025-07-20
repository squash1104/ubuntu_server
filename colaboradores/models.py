from django.db import models
from geografia.models import Cidade, Bairro

class Colaborador(models.Model):
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'colaboradores'
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']

    def __str__(self):
        return self.nome
