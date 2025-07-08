from django.db import models
from colaboradores.models import Colaborador

class Convidado(models.Model):
	nome = models.CharField(max_length=255)
	telefone = models.CharField(max_length=20)
	email = models.EmailField(max_length=255, blank=True, null=True)
	bairro = models.CharField(max_length=100)
	cidade = models.CharField(max_length=100)
	data_cadastro = models.DateTimeField(auto_now_add=True)
	data_confirmacao = models.DateTimeField(blank=True, null=True)

	colaborador = models.ForeignKey(Colaborador, on_delete=models.SET_NULL, null=True, related_name='convidados')

	class Meta:
		verbose_name = "Convidado"
		verbose_name_plural = "Convidados"

	def __str__(self):
		return self.nome
