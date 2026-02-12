from typing import ClassVar

from django import forms

from geografia.models import Bairro, Cidade

from .models import TIPO_CHOICES, Colaborador


class RelatorioColaboradoresForm(forms.Form):
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


class ColaboradorForm(forms.ModelForm):
    novo_bairro = forms.CharField(
        required=False,
        label="Novo Bairro:",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite o nome do novo bairro"
        })
    )

    data_nascimento = forms.DateField(
        required=False,
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "form-control",
                "placeholder": "dd/mm/aaaa",
                "data-mask": "00/00/0000",
            },
        ),
        label="Data de Nascimento:",
    )

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo:",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Colaborador
        fields: ClassVar = [
            "nome",
            "telefone",
            "data_nascimento",
            "cidade",
            "bairro",
            "tipo",
            "novo_bairro",
        ]
        labels: ClassVar = {
            "nome": "Nome:",
            "telefone": "Telefone:",
            "cidade": "Cidade:",
            "bairro": "Bairro:",
        }

    has_phone_warning = False

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get("nome")
        telefone = cleaned_data.get("telefone")
        cidade = cleaned_data.get("cidade")
        bairro = cleaned_data.get("bairro")
        novo_bairro = cleaned_data.get("novo_bairro", "").strip()

        # 1. VALIDAÇÃO DE NOME ÚNICO (Erro - barra o formulário)
        if nome and (
            Colaborador.objects.filter(nome__iexact=nome)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            self.add_error("nome", forms.ValidationError("", code="nome_existente"))

        # 2. VALIDAÇÃO DE TELEFONE DUPLICADO (Aviso - não barra o formulário)
        if telefone and (
            Colaborador.objects.filter(telefone=telefone)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            self.has_phone_warning = True

        # 3. LÓGICA DE CRIAÇÃO DE NOVO BAIRRO
        if novo_bairro:
            if not cidade:
                self.add_error("novo_bairro", "Selecione uma cidade antes de criar um novo bairro.")
            else:
                # Verificar se já existe bairro com o mesmo nome na cidade
                existing_bairro = Bairro.objects.filter(
                    nome_bairro__iexact=novo_bairro, cidade=cidade
                ).first()
                if existing_bairro:
                    # Se já existe, usa o bairro existente
                    cleaned_data["bairro"] = existing_bairro
                    cleaned_data["novo_bairro"] = ""
                else:
                    # Criar o novo bairro
                    novo_bairro_obj = Bairro.objects.create(
                        nome_bairro=novo_bairro,
                        cidade=cidade
                    )
                    cleaned_data["bairro"] = novo_bairro_obj
                    cleaned_data["novo_bairro"] = ""
        elif not bairro and cidade:
            # Se não selecionou bairro e não criou um novo, mostrar erro
            self.add_error("bairro", "Selecione um bairro ou crie um novo.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["nome"].widget.attrs.update({"class": "form-control"})
        self.fields["telefone"].widget.attrs.update({"class": "form-control"})
        self.fields["data_nascimento"].widget.attrs.update({"class": "form-control"})
        self.fields["novo_bairro"].widget.attrs.update({"class": "form-control"})

        self.fields["cidade"].empty_label = "Selecione uma cidade"
        self.fields["bairro"].empty_label = "Primeiro escolha uma cidade"

        self.fields["cidade"].widget.attrs.update({"class": "select2"})
        self.fields["bairro"].widget.attrs.update({"class": "select2"})

        self.fields["bairro"].queryset = Bairro.objects.none()

        # Lógica para carregar os bairros se o formulário já tiver dados (ex: na edição)
        if self.instance and getattr(self.instance, "bairro", None):
            # Caso de edição: garantir queryset e seleção do bairro e cidade atuais
            self.fields["cidade"].initial = (
                self.instance.bairro.cidade.pk
                if self.instance.bairro and self.instance.bairro.cidade
                else (self.instance.cidade.pk if self.instance.cidade else None)
            )
            if self.instance.bairro and self.instance.bairro.cidade:
                self.fields["bairro"].queryset = Bairro.objects.filter(
                    cidade=self.instance.bairro.cidade
                ).order_by("nome_bairro")
                self.fields["bairro"].initial = self.instance.bairro.pk
        elif "cidade" in self.data:
            try:
                cidade_id = int(self.data.get("cidade"))
                self.fields["bairro"].queryset = Bairro.objects.filter(
                    cidade_id=cidade_id
                ).order_by("nome_bairro")
            except (ValueError, TypeError):
                pass  # Ignora erros se o valor não for um número
        elif self.instance.pk and self.instance.cidade:
            # Caso de edição sem bairro definido, mas com cidade
            self.fields["bairro"].queryset = self.instance.cidade.bairros.order_by(
                "nome_bairro"
            )
