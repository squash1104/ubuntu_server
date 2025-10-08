from django import forms

from colaboradores.models import Colaborador

from .models import Bairro, Convidado


class ConvidadoForm(forms.ModelForm):
    # Alinhar com ColaboradorForm: campo de data com máscara e placeholder
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

    class Meta:
        model = Convidado
        fields = [
            "nome",
            "telefone",
            "data_nascimento",
            "cidade",
            "bairro",
            "colaborador",
        ]
        labels = {
            "nome": "Nome:",
            "telefone": "Telefone:",
            "cidade": "Cidade:",
            "bairro": "Bairro:",
            "colaborador": "Colaborador:",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Classes e placeholders consistentes com ColaboradorForm
        self.fields["nome"].widget.attrs.update({"class": "form-control"})
        self.fields["telefone"].widget.attrs.update({"class": "form-control"})
        self.fields["data_nascimento"].widget.attrs.update({"class": "form-control"})

        # Placeholders dos selects e classes select2
        self.fields["cidade"].empty_label = "Selecione uma cidade"
        self.fields["bairro"].empty_label = "Primeiro escolha uma cidade"

        self.fields["cidade"].widget.attrs.update({"class": "select2"})
        self.fields["bairro"].widget.attrs.update({"class": "select2"})

        if "colaborador" in self.fields:
            # Opcional: select2 para colaborador, se presente
            self.fields["colaborador"].widget.attrs.update({"class": "select2"})
            if getattr(self.fields["colaborador"], "empty_label", None) is not None:
                self.fields["colaborador"].empty_label = "Selecione um colaborador"

        # Atualizar queryset do bairro baseado na cidade selecionada
        if "cidade" in self.data:
            try:
                cidade_id = int(self.data.get("cidade"))
                self.fields["bairro"].queryset = Bairro.objects.filter(
                    cidade_id=cidade_id
                ).order_by("nome_bairro")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Se estiver editando um convidado existente
            if self.instance.cidade:
                self.fields["bairro"].queryset = Bairro.objects.filter(
                    cidade=self.instance.cidade
                ).order_by("nome_bairro")
            else:
                self.fields["bairro"].queryset = Bairro.objects.none()
        else:
            # Se for um novo convidado
            self.fields["bairro"].queryset = Bairro.objects.none()


class RelatorioConvidadosForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data Início",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
    )
    data_fim = forms.DateField(
        label="Data Fim",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
    )
    colaborador = forms.ModelChoiceField(
        queryset=Colaborador.objects.all().order_by("nome"),
        empty_label="Todos os Colaboradores",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
