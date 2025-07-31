from django import forms
from .models import Colaborador
from geografia.models import Bairro

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome', 'telefone', 'cidade', 'bairro']
        labels = {
            'nome': 'Nome:',
            'telefone': 'Telefone:',
            'cidade': 'Cidade:',
            'bairro': 'Bairro:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})

        self.fields['cidade'].empty_label = "Selecione uma cidade"
        self.fields['bairro'].empty_label = "Primeiro escolha uma cidade"

        self.fields['cidade'].widget.attrs.update({'class': 'select2'})
        self.fields['bairro'].widget.attrs.update({'class': 'select2'})

        self.fields['bairro'].queryset = Bairro.objects.none()

        # Lógica para carregar os bairros se o formulário já tiver dados (ex: na edição)
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
            except (ValueError, TypeError):
                pass  # Ignora erros se o valor não for um número
        elif self.instance.pk and self.instance.cidade:
            self.fields['bairro'].queryset = self.instance.cidade.bairro_set.order_by('nome_bairro')



class RelatorioColaboradoresForm(forms.Form):
    """
    Formulário para filtrar dados de relatório de colaboradores.
    """
    # Filtros de Data para o cadastro do colaborador
    data_cadastro_inicio = forms.DateField(
        label="Cadastro a partir de",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_cadastro_fim = forms.DateField(
        label="Cadastro até",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Filtro: Quantidade Mínima de Convidados
    min_convidados = forms.IntegerField(
        label="Mínimo de Convidados",
        required=False,
        min_value=0, # Garante que o número não seja negativo
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'}) # Adicionado placeholder
    )

    # Opções de Ordenação para os colaboradores
    ORDEM_COLABORADORES_CHOICES = [ # Renomeei para evitar conflito com ORDEM_ALFABETICA_CHOICES de convidados
        ('', 'Não Ordenar'),
        ('nome_asc', 'Nome (A-Z)'),
        ('nome_desc', 'Nome (Z-A)'),
        ('convidados_desc', 'Mais Convidados (Decrescente)'),
        ('convidados_asc', 'Menos Convidados (Crescente)'),
    ]
    ordem_colaboradores = forms.ChoiceField(
        label="Ordenar por",
        choices=ORDEM_COLABORADORES_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Se precisar de lógica dependente (ex: bairro após cidade, se colaborador tiver esses campos),
    # você adicionaria o método __init__ aqui, similar ao que fizemos para o Convidados.
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Lógica para preencher dropdowns dependentes