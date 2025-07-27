from django import forms
from .models import Convidado
from geografia.models import Bairro

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