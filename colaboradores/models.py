from django.db import models
from geografia.models import Cidade, Bairro
from django.contrib.auth.models import User

class Colaborador(models.Model):
    # O Django criará automaticamente um campo 'id' como chave primária (PK)
    nome = models.CharField(max_length=100) # Coluna no DB será 'nome'
    telefone = models.CharField(max_length=20, blank=True, null=True) # Coluna no DB será 'telefone'

    # ForeignKeys para Cidade e Bairro. O Django criará 'cidade_id' e 'bairro_id' no DB.
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.SET_NULL, null=True, blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'colaboradores' # A tabela no DB será 'colaboradores'
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']

    def __str__(self):
        return self.nome