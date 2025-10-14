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
        widgets = {
            "colaborador": forms.Select(attrs={"class": "form-control select2"}),
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
            # Obrigatório: select2 para colaborador
            self.fields["colaborador"].widget.attrs.update({"class": "select2"})
            self.fields["colaborador"].empty_label = "Selecione um colaborador"
            self.fields["colaborador"].required = True
            self.fields["colaborador"].widget.attrs["required"] = "required"
            # Forçar o campo a ser obrigatório
            self.fields["colaborador"].empty_values = []

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

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            # Verificar se já existe um convidado com este nome
            queryset = Convidado.objects.filter(nome__iexact=nome)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    f'O nome "{nome}" já está cadastrado. Escolha um nome diferente.',
                    code='nome_duplicado'
                )
        return nome

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Verificar se já existe um convidado com este telefone
            convidado_existente = Convidado.objects.filter(telefone=telefone)
            if self.instance.pk:
                convidado_existente = convidado_existente.exclude(pk=self.instance.pk)
            
            if convidado_existente.exists():
                convidado = convidado_existente.first()
                # Marcar como duplicado para exibir aviso (não erro)
                self.phone_is_duplicate = True
                self.duplicate_phone_convidado = convidado.nome
            
            # Verificar se já existe um colaborador com este telefone
            from colaboradores.models import Colaborador
            colaborador_existente = Colaborador.objects.filter(telefone=telefone)
            if colaborador_existente.exists():
                colaborador = colaborador_existente.first()
                # Marcar como duplicado para exibir aviso (não erro)
                self.phone_is_duplicate = True
                self.duplicate_phone_colaborador = colaborador.nome
        
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        colaborador = cleaned_data.get('colaborador')
        
        if not colaborador:
            self.add_error('colaborador', 'É obrigatório selecionar um colaborador.')
        
        return cleaned_data


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
