from django.contrib import admin

from .models import Bairro, Cidade  # 1. Importe os seus modelos


# 2. Crie classes de admin para customização (opcional, mas boa prática)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome_cidade", "uf_cidade")  # Colunas a exibir na lista
    search_fields = ("nome_cidade", "uf_cidade")  # Adiciona uma barra de busca


class BairroAdmin(admin.ModelAdmin):
    list_display = ("nome_bairro", "cidade")  # Colunas a exibir na lista
    search_fields = ("nome_bairro",)  # Adiciona uma barra de busca
    list_filter = ("cidade",)  # Adiciona um filtro lateral por cidade


# 3. Registe os seus modelos com as suas classes de admin
admin.site.register(Cidade, CidadeAdmin)
admin.site.register(Bairro, BairroAdmin)
