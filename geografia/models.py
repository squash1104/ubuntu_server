from django.db import models

class Cidade(models.Model):
    # O Django criará automaticamente um campo 'id' como chave primária (PK)
    nome_cidade = models.CharField(max_length=100)
    uf_cidade = models.CharField(max_length=2)
    latitude_cidade = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude_cidade = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    class Meta:
        db_table = 'cidades' # A tabela no DB será 'cidades'
        unique_together = ('nome_cidade', 'uf_cidade')

    def __str__(self):
        return f"{self.nome_cidade} - {self.uf_cidade}"

class Bairro(models.Model):
    # O Django criará automaticamente um campo 'id' como chave primária (PK)
    nome_bairro = models.CharField(max_length=100)
    # ForeignKey para Cidade. O Django criará a coluna 'cidade_id' no DB.
    # Não precisa de db_column ou to_field.
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='bairros')

    latitude_bairro = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude_bairro = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    class Meta:
        db_table = 'bairros' # A tabela no DB será 'bairros'
        unique_together = ('nome_bairro', 'cidade')

    def __str__(self):
        return self.nome_bairro