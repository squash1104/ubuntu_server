from typing import ClassVar

from django import forms
from django.core.exceptions import ValidationError

from colaboradores.models import Colaborador
from geografia.models import Bairro, Cidade

from .models import Convidado


class RelatorioConvidadosForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data de Início",
        required=False,  # O campo não é obrigatório
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        required=False,  # O campo não é obrigatório
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all().order_by("nome_cidade"),  # Busca todas as cidades
        label="Cidade",
        required=False,
        empty_label="Todas as Cidades",  # Opção para não filtrar por cidade
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),  # Adicione 'select2' se você usa essa lib
    )

    bairro = forms.ModelChoiceField(
        queryset=Bairro.objects.none(),  # Começa vazio, será preenchido via JS
        label="Bairro",
        required=False,
        empty_label="Todos os Bairros",  # Opção para não filtrar por bairro
        widget=forms.Select(
            attrs={"class": "form-control"}
        ),  # Adicione 'select2' se você usa essa lib
    )

    ORDENAR_POR_CHOICES: ClassVar = [
        ("", "Não Ordenar"),
        ("nome_asc", "Nome (A-Z)"),
        ("nome_desc", "Nome (Z-A)"),
        ("cidade_asc", "Cidade (A-Z)"),
        ("cidade_desc", "Cidade (Z-A)"),
        ("bairro_asc", "Bairro (A-Z)"),
        ("bairro_desc", "Bairro (Z-A)"),
        ("data_cidade_nome_asc", "Data Cadastro, Cidade, Nome (A-Z)"),
    ]
    ordem = forms.ChoiceField(
        choices=ORDENAR_POR_CHOICES,
        required=False,
        label="Ordenar por",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lógica para preencher o dropdown de bairros dinamicamente
        # Se uma cidade foi selecionada (e o formulário foi submetido)
        if "cidade" in self.data:
            try:
                cidade_id = int(self.data.get("cidade"))
                # Filtra os bairros pela cidade selecionada
                self.fields["bairro"].queryset = Bairro.objects.filter(
                    cidade_id=cidade_id
                ).order_by("nome_bairro")
            except (ValueError, TypeError):
                # Se houver erro na conversão do ID da cidade, não filtra os bairros
                pass
        elif self.initial.get("cidade"):
            # Se o formulário está sendo inicializado com uma cidade (ex: em edição)
            cidade_id = self.initial.get("cidade")
            self.fields["bairro"].queryset = Bairro.objects.filter(
                cidade_id=cidade_id
            ).order_by("nome_bairro")

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_fim = cleaned_data.get("data_fim")

        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValidationError(
                "A data de início não pode ser posterior à data de fim."
            )


class ConvidadoForm(forms.ModelForm):
    # Campos que usam o Select2
    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all().order_by("nome_cidade"),
        label="Cidade",
        widget=forms.Select(
            attrs={
                "class": "form-control select2",
                "data-placeholder": "Selecione uma cidade",
            }
        ),
        required=False,
    )
    bairro = forms.ModelChoiceField(
        queryset=Bairro.objects.none(),
        label="Bairro",
        widget=forms.Select(attrs={"class": "form-control select2"}),
        required=False,
    )

    class Meta:
        model = Convidado
        fields: ClassVar = ["nome", "telefone", "colaborador"]
        widgets: ClassVar = {
            "nome": forms.TextInput(attrs={"class": "form-control", "id": "id_nome"}),
            "telefone": forms.TextInput(
                attrs={"class": "form-control", "id": "id_telefone"}
            ),
            "colaborador": forms.HiddenInput(),
        }
        labels: ClassVar = {
            "nome": "Nome Completo",
            "telefone": "Telefone",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["colaborador"].queryset = Colaborador.objects.all()

        if self.instance and self.instance.bairro:
            self.fields["cidade"].initial = self.instance.bairro.cidade.pk
            self.fields["bairro"].queryset = Bairro.objects.filter(
                cidade=self.instance.bairro.cidade
            ).order_by("nome_bairro")
            self.fields["bairro"].initial = self.instance.bairro.pk

        self.fields["nome"].required = True

    def clean(self):
        cleaned_data = super().clean()
        telefone = cleaned_data.get("telefone")
        instance = self.instance
        self.phone_is_duplicate = False

        if telefone:
            # Lógica para verificar duplicidade de telefone
            query = Convidado.objects.filter(telefone=telefone)
            if instance and instance.pk:
                query = query.exclude(pk=instance.pk)

            if query.exists():
                # Define o atributo de aviso, mas não impede o salvamento
                self.phone_is_duplicate = True

        return cleaned_data
