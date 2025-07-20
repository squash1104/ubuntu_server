from django.db import models
from geografia.models import Cidade, Bairro

class Convidado(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)

class Meta:
    db_table = 'convidados_convidado'
    verbose_name = "Convidado"
    verbose_name_plural = "Convidados"
    ordering = ['nome']

    def __str__(self):
        return self.nome