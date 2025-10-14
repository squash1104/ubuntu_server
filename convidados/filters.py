from typing import ClassVar

import django_filters
from django import forms

from .models import Bairro, Cidade, Convidado


class ConvidadoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr="icontains", label="Nome do Convidado")

    data_cadastro__gte = django_filters.DateFilter(
        field_name="data_cadastro",
        lookup_expr="gte",
        label="Data de Início",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_cadastro__lte = django_filters.DateFilter(
        field_name="data_cadastro",
        lookup_expr="lte",
        label="Data de Fim",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    # Filtros de ForeignKey (Cidade e Bairro)
    cidade = django_filters.ModelChoiceFilter(
        queryset=Cidade.objects.all(), label="Cidade"
    )
    bairro = django_filters.ModelChoiceFilter(
        queryset=Bairro.objects.all(), label="Bairro"
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("nome", "Nome"),
            ("cidade__nome_cidade", "Cidade"),
            ("bairro__nome_bairro", "Bairro"),
            ("data_cadastro", "Data de Cadastro"),
        ),
        choices=(
            ("nome", "Nome (A-Z)"),
            ("-nome", "Nome (Z-A)"),
            ("cidade__nome_cidade", "Cidade (A-Z)"),
            ("-cidade__nome_cidade", "Cidade (Z-A)"),
            ("bairro__nome_bairro", "Bairro (A-Z)"),
            ("-bairro__nome_bairro", "Bairro (Z-A)"),
            ("data_cadastro", "Data de Cadastro (Mais antiga)"),
            ("-data_cadastro", "Data de Cadastro (Mais recente)"),
        ),
    )

    class Meta:
        model = Convidado
        fields: ClassVar = [
            "nome",
            "cidade",
            "bairro",
            "data_cadastro__gte",
            "data_cadastro__lte",
        ]
