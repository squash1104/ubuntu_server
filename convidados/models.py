from django.db import models
from colaboradores.models import Colaborador

class Convidado(models.Model):
	nome = models.CharField(max_length=255)
	telefone = models.CharField(max_length=20)
	email = models.EmailField(max_length=255, blank=True, null=True)
    cidade = models.ForeinKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeinKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)
	colaborador = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, related_name='convidados')

	class Meta:
        db_table = 'convidados_convidado'
		verbose_name = "Convidado"
		verbose_name_plural = "Convidados"
		ordering = ['nome']

	def __str__(self):
		return self.nome
