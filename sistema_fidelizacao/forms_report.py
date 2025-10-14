from django import forms


class RelatorioConvidadosForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data de Início",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    # Adicione outros filtros, se necessário, como por status, etc.
    # status = forms.ChoiceField(choices=Convidados.STATUS_CHOICES, required=False)
