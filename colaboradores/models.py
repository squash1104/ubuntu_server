from django.db import models

class Colaborador(models.Model):
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=20, blank=True, null=True)
    cidade = models.ForeinKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeinKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
 
    class Meta:
        db_table = 'colaboradores_colaborador'
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']

    def __str__(self):
        return self.nome
