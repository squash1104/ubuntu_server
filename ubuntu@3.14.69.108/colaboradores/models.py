from django.db import models

class Colaborador(models.Model):
	nome = models.CharField(max_length=255)
	contato = models.CharField(max_length=255, blank=True, null=True)
	bairro = models.CharField(max_length=100)
	cidade = models.CharField(max_length=100)
	cargo = models.CharField(max_length=100)

	class Meta:
		verbose_name = "Colaborador"
		verbose_name_plural = "Colaboradores"

	def __str__ (self):
		return self.nome
