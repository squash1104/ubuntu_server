from django.db import models

class Cidade(models.Model):
    # O id_cidade será gerado automaticamente pelo Django como 'id' (pk)
    nome_cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    class Meta:
        # Django por padrão criaria 'geografia_cidade'. Mantenha 'cidades' para usar sua tabela existente.
        db_table = 'cidades'
        unique_together = ('nome_cidade', 'uf') 

    def __str__(self):
        return f"{self.nome_cidade} - {self.uf}"

class Bairro(models.Model):
    # O id_bairro será gerado automaticamente pelo Django como 'id' (pk)
    nome_bairro = models.CharField(max_length=100)
    # ForeignKey: id_cidade no DB, relacionado ao modelo Cidade no app 'geografia'
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name='bairros')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    class Meta:
        # Django por padrão criaria 'geografia_bairro'. Mantenha 'bairros' para usar sua tabela existente.
        db_table = 'bairros'
        unique_together = ('nome_bairro', 'cidade')

    def __str__(self):
        return f"{self.nome_bairro} ({self.cidade.nome_cidade})"