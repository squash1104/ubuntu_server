from typing import ClassVar

import django_filters
from django import forms
from django.db.models.fields import return_None

from .models import TIPO_CHOICES, Bairro, Cidade, Colaborador

META_STATUS_CHOICES = (
    ("pendente", "Meta Pendente (0-19)"),
    ("atingida", "Meta Atingida (20)"),
    ("superada", "Meta Superada (21+)"),
)


class ColaboradorFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr="icontains", label="Nome")

    data_cadastro__gte = django_filters.DateFilter(
        field_name="data_cadastro",
        lookup_expr="gte",
        label="Data de Cadastro (início)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_cadastro__lte = django_filters.DateFilter(
        field_name="data_cadastro",
        lookup_expr="lte",
        label="Data de Cadastro (fim)",
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
            ("total_convidados", "total_convidados"),
            ("data_cadastro", "Data de Cadastro"),
        ),
        choices=(
            ("nome", "Nome (A-Z)"),
            ("-nome", "Nome (Z-A)"),
            ("cidade__nome_cidade", "Cidade (A-Z)"),
            ("-cidade__nome_cidade", "Cidade (Z-A)"),
            ("bairro__nome_bairro", "Bairro (A-Z)"),
            ("-bairro__nome_bairro", "Bairro (Z-A)"),
            ("total_convidados", "Convidados (Menor para Maior)"),
            ("-total_convidados", "Convidados (Maior para Menor)"),
            ("data_cadastro", "Data de Cadastro (Mais antiga)"),
            ("-data_cadastro", "Data de Cadastro (Mais recente)"),
        ),
        label="Ordenar por",
    )

    # NOVO FILTRO: Usando ChoiceFilter com método personalizado
    meta_status = django_filters.ChoiceFilter(
        choices=META_STATUS_CHOICES, label="Meta Status", method="filter_by_meta_status"
    )

    # Filtro por tipo (colaborador ou ACS/ACE)
    tipo = django_filters.ChoiceFilter(choices=TIPO_CHOICES, label="Tipo")

    def filter_by_meta_status(self, queryset, name, value):
        if value == "---":
            return_None()
        if value == "pendente":
            return queryset.filter(total_convidados__lt=20)
        if value == "atingida":
            return queryset.filter(total_convidados=20)
        if value == "superada":
            return queryset.filter(total_convidados__gt=20)
        return queryset

    class Meta:
        model = Colaborador
        fields: ClassVar = [
            "nome",
            "cidade",
            "bairro",
            "data_cadastro__gte",
            "data_cadastro__lte",
        ]
