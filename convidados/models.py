from django.db import models
from colaboradores.models import Colaborador
from geografia.models import Cidade, Bairro

class Convidado(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='convidados')

class Meta:
    verbose_name = "Convidado"
    verbose_name_plural = "Convidados"
    ordering = ['nome']

    def __str__(self):
        return self.nome