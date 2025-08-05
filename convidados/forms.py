from django import forms
from .models import Convidado
from geografia.models import Cidade, Bairro


class RelatorioConvidadosForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data de Início",
        required=False,  # O campo não é obrigatório
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        required=False,  # O campo não é obrigatório
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.all().order_by('nome_cidade'),  # Busca todas as cidades
        label="Cidade",
        required=False,
        empty_label="Todas as Cidades",  # Opção para não filtrar por cidade
        widget=forms.Select(attrs={'class': 'form-control'})  # Adicione 'select2' se você usa essa lib
    )

    bairro = forms.ModelChoiceField(
        queryset=Bairro.objects.none(),  # Começa vazio, será preenchido via JS
        label="Bairro",
        required=False,
        empty_label="Todos os Bairros",  # Opção para não filtrar por bairro
        widget=forms.Select(attrs={'class': 'form-control'})  # Adicione 'select2' se você usa essa lib
    )

    ORDENAR_POR_CHOICES = [
        ('', 'Não Ordenar'),
        ('nome_asc', 'Nome (A-Z)'),
        ('nome_desc', 'Nome (Z-A)'),
        ('cidade_asc', 'Cidade (A-Z)'),
        ('cidade_desc', 'Cidade (Z-A)'),
        ('bairro_asc', 'Bairro (A-Z)'),
        ('bairro_desc', 'Bairro (Z-A)'),
        ('data_cidade_nome_asc', 'Data Cadastro, Cidade, Nome (A-Z)'),
    ]
    ordem = forms.ChoiceField(
        choices=ORDENAR_POR_CHOICES,
        required=False,
        label='Ordenar por',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lógica para preencher o dropdown de bairros dinamicamente
        # Se uma cidade foi selecionada (e o formulário foi submetido)
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                # Filtra os bairros pela cidade selecionada
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
            except (ValueError, TypeError):
                # Se houver erro na conversão do ID da cidade, não filtra os bairros
                pass
        elif self.initial.get('cidade'):
            # Se o formulário está sendo inicializado com uma cidade (ex: em edição)
            cidade_id = self.initial.get('cidade')
            self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')


class ConvidadoForm(forms.ModelForm):
    class Meta:
        model = Convidado
        fields = ['nome', 'telefone', 'cidade', 'bairro', 'colaborador']
        labels = {
            'nome': 'Nome:',
            'telefone': 'Telefone:',
            'cidade': 'Cidade:',
            'bairro': 'Bairro:',
            'colaborador': 'Convidado por:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})

        # 1. Adicione a classe 'select2' a todos os dropdowns que você quer estilizar
        self.fields['cidade'].widget.attrs.update({'class': 'select2'})
        self.fields['bairro'].widget.attrs.update({'class': 'select2'})

        if 'colaborador' in self.initial:
            colaborador_inicial = self.initial.get('colaborador')
            # Se sim, esconde o campo e mantém o valor
            self.fields['colaborador'].widget = forms.HiddenInput()
        else:
            # Se não, o campo aparece normalmente como um dropdown
            self.fields['colaborador'].widget.attrs.update({'class': 'select2'})
            self.fields['colaborador'].empty_label = "Selecione um colaborador"

        # 2. Altere o texto padrão se desejar
        self.fields['cidade'].empty_label = "Selecione uma cidade"
        self.fields['bairro'].empty_label = "Primeiro, escolha uma cidade"

        # 3. Defina o dropdown dependente (bairro) para começar vazio
        self.fields['bairro'].queryset = Bairro.objects.none()

        # (importante para as telas de edição)
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.cidade:
            self.fields['bairro'].queryset = self.instance.cidade.bairro_set.order_by('nome_bairro')



